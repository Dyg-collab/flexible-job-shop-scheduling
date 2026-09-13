import random

from generator.instance_generator import create_random_instance
from environment.validator import validate_schedule
from environment.metrics import get_makespan, get_job_completion_time


def create_schedule(instance):
    jobs = instance["jobs"]
    num_machines = instance["num_machines"]

    # Initially, all machines are available at time 0
    machine_available = [0] * num_machines

    # Tracks when each job's previous operation finishes
    job_available = [0] * len(jobs)

    schedule = []

    for job_id, job in enumerate(jobs):
        for operation_id, eligible_machines in enumerate(job):

            best_machine = None
            best_start = None
            best_end = None

            # Choose the eligible machine that finishes this operation earliest
            for machine_id, duration in eligible_machines.items():
                start_time = max(
                    job_available[job_id],
                    machine_available[machine_id]
                )

                end_time = start_time + duration

                if best_end is None or end_time < best_end:
                    best_machine = machine_id
                    best_start = start_time
                    best_end = end_time

            # Add operation to the schedule
            schedule.append(
                (job_id, operation_id, best_machine, best_start)
            )

            # Update availability
            job_available[job_id] = best_end
            machine_available[best_machine] = best_end

    return schedule


def run_experiments():
    configurations = [
        (3, 3),
        (5, 3),
        (5, 5),
        (8, 5),
    ]

    num_seeds = 10

    for num_jobs, num_machines in configurations:
        makespans = []
        invalid_count = 0

        print(f"\nTesting {num_jobs} jobs × {num_machines} machines")

        for seed in range(num_seeds):
            random.seed(seed)

            instance = create_random_instance(
                num_jobs=num_jobs,
                num_machines=num_machines
            )

            schedule = create_schedule(instance)
            errors = validate_schedule(instance, schedule)

            if errors:
                invalid_count += 1
                print(f"Seed {seed}: INVALID - {errors}")
                continue

            makespan = get_makespan(instance, schedule)
            makespans.append(makespan)

        print("Valid:", len(makespans))
        print("Invalid:", invalid_count)

        if makespans:
            print("Average makespan:", sum(makespans) / len(makespans))
            print("Best makespan:", min(makespans))
            print("Worst makespan:", max(makespans))


if __name__ == "__main__":
    run_experiments()
