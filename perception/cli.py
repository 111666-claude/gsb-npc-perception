"""命令行入口：跑感知样例。"""

import argparse

from .core import Perception


def build_parser():
    parser = argparse.ArgumentParser(prog="npc-perception", description="NPC 感知")
    parser.add_argument("--sample", default="cone",
                        help="cone / wall / hear / memory / scan")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.sample == "cone":
        world = Perception(view_range=20, fov_deg=90, hear_range=0, memory_ms=1000)
        world.add("npc", 0, 0, team=0, facing=0)
        world.add("mob", 0, 10, team=1)
        world.observe("npc", 0)
        print("seen=%s" % str(world.seen("npc", "mob", 0)).lower())
    elif args.sample == "wall":
        world = Perception(view_range=20, fov_deg=90, hear_range=0, memory_ms=1000)
        world.add("npc", 0, 0, team=0, facing=0)
        world.add("mob", 10, 0, team=1)
        world.add_wall(5, -5, 5, 5)
        world.observe("npc", 0)
        print("seen=%s" % str(world.seen("npc", "mob", 0)).lower())
    elif args.sample == "hear":
        world = Perception(view_range=5, fov_deg=90, hear_range=20, memory_ms=1000)
        world.add("npc", 0, 0, team=0, facing=0)
        world.add("mob", -10, 0, team=1)
        world.observe("npc", 0)
        print("heard=%s" % str(world.heard("npc", "mob", 0)).lower())
    elif args.sample == "memory":
        world = Perception(view_range=20, fov_deg=360, hear_range=0, memory_ms=1000)
        world.add("npc", 0, 0, team=0)
        world.add("mob", 10, 0, team=1)
        world.observe("npc", 0)
        world.move("mob", 10000, 0)
        world.observe("npc", 1001)
        print("seen=%s" % str(world.seen("npc", "mob", 1001)).lower())
    elif args.sample == "scan":
        world = Perception(view_range=20, fov_deg=360, hear_range=20, memory_ms=1000)
        world.add("npc", 0, 0, team=0)
        for index in range(3000):
            world.add("m-%d" % index, 1000 + index, 0, team=1)
        for _ in range(3000):
            world.observe("npc", 0)
        print("scanned=%d" % world.scanned_count())
    else:
        raise SystemExit("需要 --sample cone|wall|hear|memory|scan")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
