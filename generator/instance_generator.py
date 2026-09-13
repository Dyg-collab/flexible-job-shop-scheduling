import random

def create_sample_instance():
    instance = {
        "num_jobs" : 2,
        "num_machines" : 2,
        "jobs" : [
            [
                {0:3, 1:4},
                {1:2}
            ],
            [
                {0:2},
                {0:2,1:3}
            ]
        ]
    }
    return instance

def create_test_instance():
    return {
        "num_jobs": 3,
        "num_machines": 3,
        "jobs": [
            [{0: 3, 1: 2}, {1: 4, 2: 3}, {0: 2, 2: 5}],
            [{1: 3, 2: 4}, {0: 2, 1: 5}, {2: 2}],
            [{0: 4, 2: 3}, {1: 2, 2: 4}, {0: 3, 1: 3}]
        ]
    }

def create_random_instance(
    num_jobs=3,
    num_machines=3,
    min_operations=2,
    max_operations=4,
    min_duration=1,
    max_duration=10
):
    jobs = []

    for _ in range(num_jobs):
        num_operations = random.randint(min_operations, max_operations)
        job = []

        for _ in range(num_operations):
            # Choose at least one eligible machine
            num_eligible = random.randint(1, num_machines)
            eligible_machines = random.sample(
                range(num_machines),
                num_eligible
            )

            # Store machine_id: processing_time
            operation = {}

            for machine_id in eligible_machines:
                operation[machine_id] = random.randint(
                    min_duration,
                    max_duration
                )

            job.append(operation)

        jobs.append(job)

    return {
        "num_jobs": num_jobs,
        "num_machines": num_machines,
        "jobs": jobs
    }

if __name__ == "__main__":
    random.seed(42)
    instance = create_random_instance(num_jobs=3,num_machines=3)
    print(instance)