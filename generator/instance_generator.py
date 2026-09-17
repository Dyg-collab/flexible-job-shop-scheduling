"""FJSP instance generation utilities.

Representation used throughout the project:
    instance = {
        "num_jobs": int,
        "num_machines": int,
        "jobs": [
            [
                {machine_id: processing_time, ...},
                ...
            ],
            ...
        ]
    }

For each operation, the dictionary maps every eligible machine to the
processing time on that machine.
"""

from __future__ import annotations

import random
from typing import Optional


def create_sample_instance() -> dict:
    return {
        "num_jobs": 2,
        "num_machines": 2,
        "jobs": [
            [{0: 3, 1: 4}, {1: 2}],
            [{0: 2}, {0: 2, 1: 3}],
        ],
    }


def create_test_instance() -> dict:
    return {
        "num_jobs": 3,
        "num_machines": 3,
        "jobs": [
            [{0: 3, 1: 2}, {1: 4, 2: 3}, {0: 2, 2: 5}],
            [{1: 3, 2: 4}, {0: 2, 1: 5}, {2: 2}],
            [{0: 4, 2: 3}, {1: 2, 2: 4}, {0: 3, 1: 3}],
        ],
    }


def _validate_parameters(
    num_jobs: int,
    num_machines: int,
    min_operations: int,
    max_operations: int,
    min_duration: int,
    max_duration: int,
    flexibility: Optional[float],
    bottleneck_probability: float,
) -> None:
    if num_jobs <= 0:
        raise ValueError("num_jobs must be positive")
    if num_machines <= 0:
        raise ValueError("num_machines must be positive")
    if min_operations <= 0 or max_operations < min_operations:
        raise ValueError("operation bounds are invalid")
    if min_duration <= 0 or max_duration < min_duration:
        raise ValueError("duration bounds are invalid")
    if flexibility is not None and not 0.0 <= flexibility <= 1.0:
        raise ValueError("flexibility must be between 0 and 1")
    if not 0.0 <= bottleneck_probability <= 1.0:
        raise ValueError("bottleneck_probability must be between 0 and 1")


def create_random_instance(
    num_jobs: int = 3,
    num_machines: int = 3,
    min_operations: int = 2,
    max_operations: int = 4,
    min_duration: int = 1,
    max_duration: int = 10,
    flexibility: Optional[float] = None,
    bottleneck_probability: float = 0.0,
    bottleneck_machine: Optional[int] = None,
    bottleneck_multiplier: float = 2.0,
    rng: Optional[random.Random] = None,
) -> dict:
    """Generate a reproducible random FJSP instance.

    flexibility is the approximate fraction of machines that each operation
    can use. If None, the original project behaviour is used: each operation
    gets a random number of eligible machines.

    bottleneck_probability controls how often an operation includes the
    designated bottleneck machine when it is not selected naturally.
    bottleneck_multiplier > 1 makes the bottleneck machine slower; values
    below 1 can be used to model a machine with an advantage instead.
    """
    _validate_parameters(
        num_jobs,
        num_machines,
        min_operations,
        max_operations,
        min_duration,
        max_duration,
        flexibility,
        bottleneck_probability,
    )

    rng = rng or random.Random()

    if bottleneck_machine is not None and not 0 <= bottleneck_machine < num_machines:
        raise ValueError("bottleneck_machine is outside the machine range")
    if bottleneck_multiplier <= 0:
        raise ValueError("bottleneck_multiplier must be positive")

    jobs = []

    for _ in range(num_jobs):
        num_operations = rng.randint(min_operations, max_operations)
        job = []

        for _ in range(num_operations):
            if flexibility is None:
                num_eligible = rng.randint(1, num_machines)
            else:
                num_eligible = max(1, round(flexibility * num_machines))

            eligible_machines = rng.sample(range(num_machines), num_eligible)

            # Optionally force the designated bottleneck machine to appear.
            if (
                bottleneck_machine is not None
                and rng.random() < bottleneck_probability
                and bottleneck_machine not in eligible_machines
            ):
                eligible_machines[-1] = bottleneck_machine

            operation = {}
            for machine_id in eligible_machines:
                duration = rng.randint(min_duration, max_duration)
                if machine_id == bottleneck_machine:
                    duration = max(1, round(duration * bottleneck_multiplier))
                operation[machine_id] = duration

            job.append(operation)

        jobs.append(job)

    return {
        "num_jobs": num_jobs,
        "num_machines": num_machines,
        "jobs": jobs,
    }
