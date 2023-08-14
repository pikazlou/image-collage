import unittest

from layout import partition, try_layout


class TestNumberPartition(unittest.TestCase):
    def test_sum_equal_number(self):
        res = partition(5, [3, 5])
        self.assertEqual([5], res)

    def test_all_numbers_greater_than_sum(self):
        res = partition(4, [5, 6])
        self.assertEqual([], res)

    def test_multiple_numbers_used_to_sum(self):
        res = partition(13, [4, 3])
        self.assertEqual([3, 3, 3, 4], sorted(res))

    def test_multiple_impossible_to_sum(self):
        res = partition(11, [5, 4])
        self.assertEqual([], res)

    def test_large_sum(self):
        res = partition(33, [4, 7])
        self.assertEqual([4, 4, 4, 7, 7, 7], sorted(res))

    def test_repeating_numbers(self):
        res = partition(14, [3, 3, 5, 5])
        self.assertEqual([3, 3, 3, 5], sorted(res))


class TestTryLayout(unittest.TestCase):
    def test_trivial_case(self):
        res = try_layout(4, 3, [(4, 3)])
        self.assertEqual([(0, 0, 4, 3)], res)

    def test_trivial_impossible_case(self):
        res = try_layout(4, 3, [(4, 4)])
        self.assertEqual([], res)

    def test_several_same_tiles(self):
        res = try_layout(8, 10, [(4, 5)])
        self.assertEqual([(0, 0, 4, 5), (0, 5, 4, 5), (4, 0, 4, 5), (4, 5, 4, 5)], sorted(res, key=lambda t: (t[0], t[1])))

    def test_several_different_tiles(self):
        res = try_layout(7, 7, [(3, 3), (4, 4), (3, 4), (4, 3)])
        self.assertEqual([(3, 3), (3, 4), (4, 3), (4, 4)], sorted([(t[2], t[3]) for t in res]))


if __name__ == '__main__':
    unittest.main()
