"""NPC 感知：视野锥、视线遮挡、听觉半径与记忆时长。

缺陷：不看视野锥、不查遮挡、没有听觉、记忆不过期、每次观察扫描全部单位。
"""

import math


def _cross(ax, ay, bx, by):
    return ax * by - ay * bx


def _segments_hit(a, b, c, d):
    """线段 ab 与 cd 是否相交。"""
    def ccw(p, q, r):
        return _cross(q[0] - p[0], q[1] - p[1], r[0] - p[0], r[1] - p[1])

    d1 = ccw(c, d, a)
    d2 = ccw(c, d, b)
    d3 = ccw(a, b, c)
    d4 = ccw(a, b, d)
    if ((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) and \
            ((d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0)):
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
        self.seen_at = {}
        self.heard_at = {}
        self.scanned = 0

    def add(self, eid, x, y, team=0, facing=0.0):
        self.entities[eid] = {"id": eid, "x": x, "y": y, "team": team, "facing": facing}

    def move(self, eid, x, y):
        if eid in self.entities:
            self.entities[eid]["x"] = x
            self.entities[eid]["y"] = y

    def set_facing(self, eid, deg):
        self.entities[eid]["facing"] = deg

    def add_wall(self, x1, y1, x2, y2):
        self.walls.append(((x1, y1), (x2, y2)))

    def observe(self, observer_id, now_ms):
        """更新一次感知。"""
        self.scanned += len(self.entities)
        observer = self.entities[observer_id]
        for target_id, target in self.entities.items():
            if target_id == observer_id or target["team"] == observer["team"]:
                continue
            distance = math.hypot(target["x"] - observer["x"], target["y"] - observer["y"])
            if distance <= self.view_range:
                self.seen_at[(observer_id, target_id)] = now_ms

    def seen(self, observer_id, target_id, now_ms=0):
        return (observer_id, target_id) in self.seen_at

    def heard(self, observer_id, target_id, now_ms=0):
        return (observer_id, target_id) in self.heard_at

    def contacts(self, observer_id, now_ms=0):
        out = []
        for (obs, target), _ in self.seen_at.items():
            if obs == observer_id:
                out.append(target)
        return sorted(out)

    def scanned_count(self):
        return self.scanned
