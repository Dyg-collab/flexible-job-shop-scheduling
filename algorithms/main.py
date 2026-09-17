"""Baseline and improved greedy FJSP algorithms plus experiments."""

from __future__ import annotations

import csv
import random
import time
from pathlib import Path

from generator.instance_generator import create_random_instance
from environment.metrics import get_makespan
from environment.validator import validate_schedule


def greedy_job_order(instance: dict) -> list[tuple[int, int, int, float]]:
    """Your original baseline: finish jobs in input order.

    For each operation, choose the eligible machine that gives the earliest
    finish time for that operation.
    """
    jobs = instance["jobs"]
    num_machines = instance["num_machines"]
    machine_available = [0] * num_machines
    job_available = [0] * len(jobs)
    schedule = []

    for job_id, job in enumerate(jobs):
        for operation_id, eligible_machines in enumerate(job):
            best_machine = None
            best_start = None
            best_end = None

            for machine_id, duration in eligible_machines.items():
                start_time = max(job_available[job_id], machine_available[machine_id])
                end_time = start_time + duration
                candidate = (end_time, start_time, machine_id)
                if best_end is None or candidate < (best_end, best_start, best_machine):
                    best_machine = machine_id
                    best_start = start_time
                    best_end = end_time

            schedule.append((job_id, operation_id, best_machine, best_start))
            job_available[job_id] = best_end
            machine_available[best_machine] = best_end

    return schedule


def greedy_global_dispatch(instance: dict) -> list[tuple[int, int, int, float]]:
    """Improved constructive heuristic.

    Instead of finishing Job 0, then Job 1, etc., repeatedly choose among the
    next unscheduled operation of every job. The chosen job-operation-machine
    triple is the one with the earliest possible completion time.
    """
    jobs = instance["jobs"]
    num_machines = instance["num_machines"]
    machine_available = [0] * num_machines
    job_available = [0] * len(jobs)
    next_operation = [0] * len(jobs)
    schedule = []

    remaining = sum(len(job) for job in jobs)
    while remaining:
        best = None

        for job_id, job in enumerate(jobs):
            operation_id = next_operation[job_id]
            if operation_id >= len(job):
                continue

            for machine_id, duration in job[operation_id].items():
                start_time = max(job_available[job_id], machine_available[machine_id])
                end_time = start_time + duration
                candidate = (
                    end_time,
                    start_time,
                    duration,
                    job_id,
                    operation_id,
                    machine_id,
                )
                if best is None or candidate < best:
                    best = candidate

        if best is None:
            raise RuntimeError("No schedulable operation remained")

        end_time, start_time, _, job_id, operation_id, machine_id = best
        schedule.append((job_id, operation_id, machine_id, start_time))

        job_available[job_id] = end_time
        machine_available[machine_id] = end_time
        next_operation[job_id] += 1
        remaining -= 1

    return schedule


def evaluate_algorithm(algorithm, instance: dict) -> dict:
    """Run an algorithm, validate it, and return comparable metrics."""
    start = time.perf_counter()
    schedule = algorithm(instance)
    runtime = time.perf_counter() - start
    errors = validate_schedule(instance, schedule)

    result = {
        "valid": not errors,
        "runtime_seconds": runtime,
        "makespan": None,
        "errors": errors,
    }
    if not errors:
        result["makespan"] = get_makespan(instance, schedule)
    return result


def run_experiments(
    output_csv: str = "results.csv",
    seeds=range(10),
) -> None:
    """Compare both greedy algorithms on exactly the same instances."""
    configurations = [
        (3, 3),
        (5, 3),
        (5, 5),
        (8, 5),
    ]
    algorithms = {
        "job_order_greedy": greedy_job_order,
        "global_dispatch_greedy": greedy_global_dispatch,
    }

    output_path = Path(output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    for num_jobs, num_machines in configurations:
        for seed in seeds:
            rng = random.Random(seed)
            instance = create_random_instance(
                num_jobs=num_jobs,
                num_machines=num_machines,
                rng=rng,
            )

            for name, algorithm in algorithms.items():
                result = evaluate_algorithm(algorithm, instance)
                rows.append({
                    "algorithm": name,
                    "jobs": num_jobs,
                    "machines": num_machines,
                    "seed": seed,
                    "valid": result["valid"],
                    "makespan": result["makespan"],
                    "runtime_seconds": result["runtime_seconds"],
                    "error_count": len(result["errors"]),
                })

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved {len(rows)} rows to {output_path}")
    for name in algorithms:
        valid = [r for r in rows if r["algorithm"] == name and r["valid"]]
        avg = sum(r["makespan"] for r in valid) / len(valid) if valid else None
        print(f"{name}: valid={len(valid)}, average_makespan={avg}")


if __name__ == "__main__":
    run_experiments()


# Backward-compatible name used by the original project.
def create_schedule(instance: dict) -> list[tuple[int, int, int, float]]:
    return greedy_job_order(instance)
