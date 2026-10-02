import unittest

from perception.core import Perception


class BasicTest(unittest.TestCase):
    def test_unknown_target_is_not_seen(self):
        world = Perception(20, 90, 20, 1000)
        world.add("npc", 0, 0)
        self.assertFalse(world.seen("npc", "ghost", 0))

    def test_unknown_target_is_not_heard(self):
        world = Perception(20, 90, 20, 1000)
        world.add("npc", 0, 0)
        self.assertFalse(world.heard("npc", "ghost", 0))

    def test_contacts_empty_before_observe(self):
        world = Perception(20, 90, 20, 1000)
        world.add("npc", 0, 0)
        world.add("mob", 1, 0, team=1)
        self.assertEqual(world.contacts("npc", 0), [])

    def test_move_updates_position(self):
        world = Perception(20, 90, 20, 1000)
        world.add("mob", 1, 2, team=1)
        world.move("mob", 5, 6)
        self.assertEqual((world.entities["mob"]["x"], world.entities["mob"]["y"]), (5, 6))

    def test_scanned_starts_at_zero(self):
        self.assertEqual(Perception(20, 90, 20, 1000).scanned_count(), 0)




class ConeTest(unittest.TestCase):
    def test_target_inside_cone_is_seen(self):
        world = Perception(20, 90, 0, 1000)
        world.add("npc", 0, 0, team=0, facing=0)
        world.add("mob", 10, 0, team=1)
        world.observe("npc", 0)
        self.assertTrue(world.seen("npc", "mob", 0))

    def test_target_outside_cone_is_not_seen(self):
        world = Perception(20, 90, 0, 1000)
        world.add("npc", 0, 0, team=0, facing=0)
        world.add("mob", 0, 10, team=1)
        world.observe("npc", 0)
        self.assertFalse(world.seen("npc", "mob", 0))

    def test_half_fov_boundary_is_seen(self):
        world = Perception(20, 90, 0, 1000)
        world.add("npc", 0, 0, team=0, facing=0)
        world.add("mob", 10, 10, team=1)  # 夹角正好 45 度
        world.observe("npc", 0)
        self.assertTrue(world.seen("npc", "mob", 0))

    def test_beyond_view_range_is_not_seen(self):
        world = Perception(20, 360, 0, 1000)
        world.add("npc", 0, 0, team=0)
        world.add("mob", 21, 0, team=1)
        world.observe("npc", 0)
        self.assertFalse(world.seen("npc", "mob", 0))

    def test_view_range_boundary_is_seen(self):
        world = Perception(20, 360, 0, 1000)
        world.add("npc", 0, 0, team=0)
        world.add("mob", 20, 0, team=1)
        world.observe("npc", 0)
        self.assertTrue(world.seen("npc", "mob", 0))


class OcclusionTest(unittest.TestCase):
    def test_wall_blocks_sight(self):
        world = Perception(20, 360, 0, 1000)
        world.add("npc", 0, 0, team=0)
        world.add("mob", 10, 0, team=1)
        world.add_wall(5, -5, 5, 5)
        world.observe("npc", 0)
        self.assertFalse(world.seen("npc", "mob", 0))

    def test_wall_off_line_does_not_block(self):
        world = Perception(20, 360, 0, 1000)
        world.add("npc", 0, 0, team=0)
        world.add("mob", 10, 0, team=1)
        world.add_wall(5, 3, 5, 8)
        world.observe("npc", 0)
        self.assertTrue(world.seen("npc", "mob", 0))

    def test_wall_does_not_block_hearing(self):
        world = Perception(5, 360, 20, 1000)
        world.add("npc", 0, 0, team=0)
        world.add("mob", 10, 0, team=1)
        world.add_wall(5, -5, 5, 5)
        world.observe("npc", 0)
        self.assertTrue(world.heard("npc", "mob", 0))


class HearingTest(unittest.TestCase):
    def test_behind_target_is_heard(self):
        world = Perception(5, 90, 20, 1000)
        world.add("npc", 0, 0, team=0, facing=0)
        world.add("mob", -10, 0, team=1)
        world.observe("npc", 0)
        self.assertTrue(world.heard("npc", "mob", 0))

    def test_hear_range_boundary_is_heard(self):
        world = Perception(5, 90, 20, 1000)
        world.add("npc", 0, 0, team=0)
        world.add("mob", 20, 0, team=1)
        world.observe("npc", 0)
        self.assertTrue(world.heard("npc", "mob", 0))

    def test_beyond_hear_range_is_not_heard(self):
        world = Perception(5, 90, 20, 1000)
        world.add("npc", 0, 0, team=0)
        world.add("mob", 21, 0, team=1)
        world.observe("npc", 0)
        self.assertFalse(world.heard("npc", "mob", 0))

    def test_same_team_is_never_heard(self):
        world = Perception(5, 90, 20, 1000)
        world.add("npc", 0, 0, team=0)
        world.add("ally", 1, 0, team=0)
        world.observe("npc", 0)
        self.assertFalse(world.heard("npc", "ally", 0))


class MemoryTest(unittest.TestCase):
    def test_memory_kept_within_window(self):
        world = Perception(20, 360, 0, 1000)
        world.add("npc", 0, 0, team=0)
        world.add("mob", 10, 0, team=1)
        world.observe("npc", 0)
        world.move("mob", 10000, 0)
        world.observe("npc", 1000)
        self.assertTrue(world.seen("npc", "mob", 1000))

    def test_memory_expires_after_window(self):
        world = Perception(20, 360, 0, 1000)
        world.add("npc", 0, 0, team=0)
        world.add("mob", 10, 0, team=1)
        world.observe("npc", 0)
        world.move("mob", 10000, 0)
        world.observe("npc", 1001)
        self.assertFalse(world.seen("npc", "mob", 1001))

    def test_expired_contact_is_removed(self):
        world = Perception(20, 360, 0, 1000)
        world.add("npc", 0, 0, team=0)
        world.add("mob", 10, 0, team=1)
        world.observe("npc", 0)
        self.assertEqual(world.contacts("npc", 0), ["mob"])
        world.move("mob", 10000, 0)
        world.observe("npc", 1001)
        self.assertEqual(world.contacts("npc", 1001), [])

    def test_heard_memory_expires(self):
        world = Perception(5, 90, 20, 1000)
        world.add("npc", 0, 0, team=0)
        world.add("mob", 10, 0, team=1)
        world.observe("npc", 0)
        world.move("mob", 10000, 0)
        world.observe("npc", 1001)
        self.assertFalse(world.heard("npc", "mob", 1001))


class InvariantTest(unittest.TestCase):
    def test_same_team_never_seen(self):
        world = Perception(20, 360, 20, 1000)
        world.add("npc", 0, 0, team=0)
        world.add("ally", 1, 0, team=0)
        world.observe("npc", 0)
        self.assertFalse(world.seen("npc", "ally", 0))
        self.assertEqual(world.contacts("npc", 0), [])

    def test_repeated_observation_is_deterministic(self):
        def run():
            world = Perception(20, 90, 20, 1000)
            world.add("npc", 0, 0, team=0, facing=0)
            world.add("a", 10, 0, team=1)
            world.add("b", 0, 10, team=1)
            world.add("c", -10, 0, team=1)
            out = []
            for t in (0, 500, 1001):
                world.observe("npc", t)
                out.append((world.contacts("npc", t),
                            world.seen("npc", "a", t),
                            world.heard("npc", "c", t)))
            return out

        self.assertEqual(run(), run())

    def test_scanned_does_not_grow_with_unit_count(self):
        world = Perception(20, 360, 20, 1000)
        world.add("npc", 0, 0, team=0)
        for index in range(3000):
            world.add("m-%d" % index, 1000 + index, 0, team=1)
        for _ in range(3000):
            world.observe("npc", 0)
        self.assertLessEqual(world.scanned_count(), 6000)


if __name__ == "__main__":
    unittest.main()
