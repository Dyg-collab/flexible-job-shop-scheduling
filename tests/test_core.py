import unittest

from algorithms.main import greedy_global_dispatch, greedy_job_order
from environment.metrics import get_makespan
from environment.validator import validate_schedule
from generator.instance_generator import create_sample_instance


class TestFJSPCore(unittest.TestCase):
    def test_baseline_is_valid(self):
        instance = create_sample_instance()
        schedule = greedy_job_order(instance)
        self.assertEqual(validate_schedule(instance, schedule), [])
        self.assertEqual(get_makespan(instance, schedule), 7)

    def test_global_dispatch_is_valid(self):
        instance = create_sample_instance()
        schedule = greedy_global_dispatch(instance)
        self.assertEqual(validate_schedule(instance, schedule), [])

    def test_validator_catches_overlap(self):
        instance = create_sample_instance()
        schedule = [
            (0, 0, 0, 0),
            (0, 1, 1, 3),
            (1, 0, 0, 1),
            (1, 1, 0, 5),
        ]
        errors = validate_schedule(instance, schedule)
        self.assertTrue(any("overlap" in error.lower() for error in errors))

    def test_validator_catches_missing_operation(self):
        instance = create_sample_instance()
        schedule = [(0, 0, 0, 0)]
        errors = validate_schedule(instance, schedule)
        self.assertTrue(any("missing operation" in error.lower() for error in errors))

    def test_validator_catches_wrong_machine(self):
        instance = create_sample_instance()
        schedule = [
            (0, 0, 0, 0),
            (0, 1, 0, 3),
            (1, 0, 0, 3),
            (1, 1, 0, 5),
        ]
        errors = validate_schedule(instance, schedule)
        self.assertTrue(any("cannot run" in error.lower() for error in errors))


if __name__ == "__main__":
    unittest.main()
