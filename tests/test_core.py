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


if __name__ == "__main__":
    unittest.main()
