"""NPC 感知：视野锥、视线遮挡、听觉半径与记忆时长。

口径以 README 为准：视野锥（距离 + 半视野夹角，边界算可见）、墙段遮挡、
跨阵营听觉（不要求视野锥与视线，半径边界算可闻）、记忆到期失效并从
contacts 移除。observe 借助均匀网格只访问观察者邻域内的单位，单次
代价为 O(邻域内单位数)，不随全图单位数线性增长。
"""

import math

_EPS = 1e-9


def _cross(ax, ay, bx, by):
    return ax * by - ay * bx


def _segments_hit(a, b, c, d):
    """线段 ab 与 cd 是否相交（含端点相接与共线重叠）。"""
    def ccw(p, q, r):
        return _cross(q[0] - p[0], q[1] - p[1], r[0] - p[0], r[1] - p[1])

    def on_segment(p, q, r):
        return (min(p[0], r[0]) - _EPS <= q[0] <= max(p[0], r[0]) + _EPS and
                min(p[1], r[1]) <= q[1] <= max(p[1], r[1]) + _EPS)

    d1 = ccw(c, d, a)
    d2 = ccw(c, d, b)
    d3 = ccw(a, b, c)
    d4 = ccw(a, b, d)
    if ((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) and \
            ((d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0)):
        return True
    if d1 == 0 and on_segment(c, a, d):
        return True
    if d2 == 0 and on_segment(c, b, d):
        return True
    if d3 == 0 and on_segment(a, c, b):
        return True
    if d4 == 0 and on_segment(a, d, b):
        return True
    return False


class Perception:
    """一个 NPC 的感知台账。"""

    def __init__(self, view_range, fov_deg, hear_range, memory_ms):
        self.view_range = view_range
        self.fov = fov_deg
        self.hear_range = hear_range
        self.memory_ms = memory_ms
        self.entities = {}
        self.walls = []
        # observer_id -> {target_id: 最后感知时刻}
        self.seen_at = {}
        self.heard_at = {}
        self.scanned = 0
        query_radius = max(view_range, hear_range)
        # 格宽不小于查询半径，半径内的目标必在所在格的 3x3 邻域内。
        self._cell = max(query_radius, 1)
        # 格 -> {eid: 实体字典}，桶内直接存引用，observe 省去二次查找；
        # 用 dict 保持确定的迭代顺序。
        self._grid = {}

    def _cell_of(self, x, y):
        return (math.floor(x / self._cell), math.floor(y / self._cell))

    def add(self, eid, x, y, team=0, facing=0.0):
        if eid in self.entities:
            old = self.entities[eid]
            self._grid[self._cell_of(old["x"], old["y"])].pop(eid, None)
        entity = {"id": eid, "x": x, "y": y, "team": team, "facing": facing}
        self.entities[eid] = entity
        self._grid.setdefault(self._cell_of(x, y), {})[eid] = entity

    def move(self, eid, x, y):
        target = self.entities.get(eid)
        if target is None:
            return
        old_cell = self._cell_of(target["x"], target["y"])
        new_cell = self._cell_of(x, y)
        target["x"] = x
        target["y"] = y
        if old_cell != new_cell:
            self._grid[old_cell].pop(eid, None)
            self._grid.setdefault(new_cell, {})[eid] = target

    def set_facing(self, eid, deg):
        if eid in self.entities:
            self.entities[eid]["facing"] = deg

    def add_wall(self, x1, y1, x2, y2):
        self.walls.append(((x1, y1), (x2, y2)))

    def observe(self, observer_id, now_ms):
        """更新一次感知，只扫描观察者 3x3 邻域格内的单位。"""
        observer = self.entities[observer_id]
        ox, oy = observer["x"], observer["y"]
        team = observer["team"]
        facing = observer["facing"]
        cx, cy = self._cell_of(ox, oy)
        half_fov = self.fov / 2.0
        full_cone = half_fov >= 180.0
        hear_sq = self.hear_range * self.hear_range
        view_sq = self.view_range * self.view_range
        seen_obs = self.seen_at.setdefault(observer_id, {})
        heard_obs = self.heard_at.setdefault(observer_id, {})
        walls = self.walls
        grid = self._grid
        scanned = self.scanned
        degrees = math.degrees
        atan2 = math.atan2
        for gx in (cx - 1, cx, cx + 1):
            for gy in (cy - 1, cy, cy + 1):
                bucket = grid.get((gx, gy))
                if not bucket:
                    continue
                scanned += len(bucket)
                for target_id, target in bucket.items():
                    if target_id == observer_id:
                        continue
                    if target["team"] == team:
                        continue
                    dx = target["x"] - ox
                    dy = target["y"] - oy
                    dist_sq = dx * dx + dy * dy
                    if dist_sq <= hear_sq:
                        heard_obs[target_id] = now_ms
                    if dist_sq > view_sq:
                        continue
                    if full_cone or dist_sq == 0:
                        in_cone = True
                    else:
                        diff = abs(degrees(atan2(dy, dx)) - facing) % 360.0
                        if diff > 180.0:
                            diff = 360.0 - diff
                        in_cone = diff <= half_fov + _EPS
                    if not in_cone:
                        continue
                    if walls:
                        a = (ox, oy)
                        b = (target["x"], target["y"])
                        blocked = any(_segments_hit(a, b, c, d)
                                      for c, d in walls)
                        if blocked:
                            continue
                    seen_obs[target_id] = now_ms
        self.scanned = scanned
        self._prune(observer_id, now_ms)

    def _prune(self, observer_id, now_ms):
        for table in (self.seen_at, self.heard_at):
            inner = table.get(observer_id)
            if not inner:
                continue
            stale = [target_id for target_id, ts in inner.items()
                     if now_ms - ts > self.memory_ms]
            for target_id in stale:
                del inner[target_id]
            if not inner:
                del table[observer_id]

    def _recalled(self, table, observer_id, target_id, now_ms):
        inner = table.get(observer_id)
        if not inner:
            return False
        ts = inner.get(target_id)
        if ts is None:
            return False
        if now_ms - ts > self.memory_ms:
            del inner[target_id]
            if not inner:
                del table[observer_id]
            return False
        return True

    def seen(self, observer_id, target_id, now_ms=0):
        return self._recalled(self.seen_at, observer_id, target_id, now_ms)

    def heard(self, observer_id, target_id, now_ms=0):
        return self._recalled(self.heard_at, observer_id, target_id, now_ms)

    def contacts(self, observer_id, now_ms=0):
        inner = self.seen_at.get(observer_id)
        if not inner:
            return []
        stale = [target_id for target_id, ts in inner.items()
                 if now_ms - ts > self.memory_ms]
        for target_id in stale:
            del inner[target_id]
        if not inner:
            del self.seen_at[observer_id]
            return []
        return sorted(inner)

    def scanned_count(self):
        return self.scanned
