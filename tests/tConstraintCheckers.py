import unittest
from ConstraintCheckers import (
    LowerBoundChecker,
    UpperBoundChecker,
    CompositeConstraintChecker,
)


class TestConstraintCheckers(unittest.TestCase):
    def test_lower_bound_checker(self):
        # Test strict lower bound
        checker = LowerBoundChecker(3, strict=True)
        self.assertEqual(checker(5), 5)
        with self.assertRaises(ValueError):
            checker(3)
        with self.assertRaises(ValueError):
            checker(2)

        # Test non-strict lower bound
        checker = LowerBoundChecker(3, strict=False)
        self.assertEqual(checker(5), 5)
        self.assertEqual(checker(3), 3)
        with self.assertRaises(ValueError):
            checker(2)

    def test_upper_bound_checker(self):
        # Test strict upper bound
        checker = UpperBoundChecker(5, strict=True)
        self.assertEqual(checker(3), 3)
        with self.assertRaises(ValueError):
            checker(5)
        with self.assertRaises(ValueError):
            checker(6)

        # Test non-strict upper bound
        checker = UpperBoundChecker(5, strict=False)
        self.assertEqual(checker(3), 3)
        self.assertEqual(checker(5), 5)
        with self.assertRaises(ValueError):
            checker(6)

    def test_composite_constraint_checker(self):
        # Test compatible constraints
        checker = CompositeConstraintChecker([
            LowerBoundChecker(3, strict=False),
            UpperBoundChecker(10, strict=False)
        ])
        self.assertEqual(checker(5), 5)
        self.assertEqual(checker(3), 3)
        self.assertEqual(checker(10), 10)
        with self.assertRaises(ValueError):
            checker(2)
        with self.assertRaises(ValueError):
            checker(11)

        # Test incompatible constraints: lower bound > upper bound
        with self.assertRaises(ValueError):
            CompositeConstraintChecker([
                LowerBoundChecker(5, strict=True),
                UpperBoundChecker(3, strict=False)
            ])

        # Test incompatible constraints: lower bound >= upper bound (both strict)
        with self.assertRaises(ValueError):
            CompositeConstraintChecker([
                LowerBoundChecker(5, strict=True),
                UpperBoundChecker(5, strict=True)
            ])

        # Test incompatible constraints: lower bound >= upper bound (one non-strict)
        with self.assertRaises(ValueError):
            CompositeConstraintChecker([
                LowerBoundChecker(5, strict=False),
                UpperBoundChecker(5, strict=True)
            ])

        # Test combined constraints

        checker = CompositeConstraintChecker([
            LowerBoundChecker(3, strict=False),
            UpperBoundChecker(11, strict=True),
            UpperBoundChecker(7, strict=False),
            LowerBoundChecker(5, strict=True),
            UpperBoundChecker(10, strict=False)
        ])
        self.assertEqual(checker(6.1), 6.1)
        self.assertEqual(checker(7), 7)
        with self.assertRaises(ValueError):
            checker(4)
        with self.assertRaises(ValueError):
            checker(8)


if __name__ == '__main__':
    unittest.main()
