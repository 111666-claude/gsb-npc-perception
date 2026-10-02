# npc-perception

NPC 感知：视野锥、视线遮挡、听觉半径与记忆时长，只用 Python 标准库。

```
python3 -m perception.cli --sample cone
python3 -m perception.cli --sample wall
python3 -m perception.cli --sample hear
python3 -m perception.cli --sample memory
python3 -m perception.cli --sample scan
python3 -m unittest discover -s tests -v
```

## 口径（README 为准）

- **视野锥**：目标距离不超过 `view_range`，且与朝向的夹角不超过 `fov_deg/2` 才算看见；
  夹角正好等于半个视野算看见。
- **遮挡**：观察者到目标的线段与任何一段墙相交时看不见。
- **听觉**：不同阵营目标在 `hear_range` 内就能被听见（不要求视野锥，也不要求视线）；
  距离正好等于听觉半径算听见。
- **记忆**：看见或听见的目标保留 `memory_ms`；超过后 `seen`/`heard` 返回 False，
  `contacts` 里也要移除。
- **不变量**：同一串观察序列重复执行结果相同；同阵营目标永不进入感知结果。
- **查询代价**：`observe` 不许遍历全部单位，`scanned_count` 不随单位数线性增长。
- **规模**：10 万单位、每秒 10 万次观察，单次摊还 O(视野内单位数)。

## 输出契约（不改格式）

```
seen=..
heard=..
scanned=..
```

## 目录

```
perception/core.py   视野、遮挡、听觉与记忆
perception/cli.py    命令行入口
tests/               unittest 用例
```
