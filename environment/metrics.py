"""Metrics for valid FJSP schedules."""

from __future__ import annotations


def get_job_completion_time(instance: dict, schedule: list[tuple]) -> dict[int, float]:
    completion: dict[int, float] = {}
    for job_id, operation_id, machine_id, start_time in schedule:
        duration = instance["jobs"][job_id][operation_id][machine_id]
        end_time = start_time + duration
        completion[job_id] = max(completion.get(job_id, 0), end_time)
    return completion


def get_makespan(instance: dict, schedule: list[tuple]) -> float:
    """Time when the last job finishes."""
    completion = get_job_completion_time(instance, schedule)
    return max(completion.values(), default=0)
