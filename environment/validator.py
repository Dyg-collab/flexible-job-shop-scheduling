"""Independent FJSP schedule validator."""

from __future__ import annotations

from typing import Iterable


def validate_schedule(instance: dict, schedule: Iterable[tuple]) -> list[str]:
    """Return a list of errors. An empty list means the schedule is valid."""
    jobs = instance.get("jobs", [])
    num_machines = instance.get("num_machines", 0)
    errors: list[str] = []
    seen: set[tuple[int, int]] = set()
    machine_intervals: dict[int, list[tuple[float, float, int, int]]] = {}

    # Materialize once so later checks see exactly the same schedule.
    schedule_list = list(schedule)

    for index, item in enumerate(schedule_list):
        if not isinstance(item, (tuple, list)) or len(item) != 4:
            errors.append(f"Malformed schedule entry at index {index}: {item!r}")
            continue

        job_id, op_id, machine_id, start = item

        if not all(isinstance(x, int) for x in (job_id, op_id, machine_id)):
            errors.append(f"Non-integer ID in schedule entry {index}: {item!r}")
            continue
        if not isinstance(start, (int, float)):
            errors.append(f"Non-numeric start time in schedule entry {index}: {item!r}")
            continue

        if not 0 <= job_id < len(jobs):
            errors.append(f"Invalid job ID: {job_id}")
            continue
        if not 0 <= op_id < len(jobs[job_id]):
            errors.append(f"Invalid operation ID: J{job_id} O{op_id}")
            continue

        operation_key = (job_id, op_id)
        if operation_key in seen:
            errors.append(f"Duplicate operation: J{job_id} O{op_id}")
            continue
        seen.add(operation_key)

        eligible = jobs[job_id][op_id]
        if not 0 <= machine_id < num_machines:
            errors.append(f"Invalid machine ID: {machine_id}")
            continue
        if machine_id not in eligible:
            errors.append(f"J{job_id} O{op_id} cannot run on M{machine_id}")
            continue
        if start < 0:
            errors.append(f"Negative start time: J{job_id} O{op_id}")
            continue

        duration = eligible[machine_id]
        end = start + duration
        machine_intervals.setdefault(machine_id, []).append(
            (start, end, job_id, op_id)
        )

    # Every operation must appear exactly once.
    for job_id, job in enumerate(jobs):
        for op_id in range(len(job)):
            if (job_id, op_id) not in seen:
                errors.append(f"Missing operation: J{job_id} O{op_id}")

    # Build a direct mapping only from well-formed, valid entries.
    entries = {}
    for item in schedule_list:
        if not isinstance(item, (tuple, list)) or len(item) != 4:
            continue
        job_id, op_id, machine_id, start = item
        if not all(isinstance(x, int) for x in (job_id, op_id, machine_id)):
            continue
        if not isinstance(start, (int, float)):
            continue
        if not (0 <= job_id < len(jobs) and 0 <= op_id < len(jobs[job_id])):
            continue
        if not (0 <= machine_id < num_machines):
            continue
        if machine_id not in jobs[job_id][op_id] or start < 0:
            continue
        key = (job_id, op_id)
        if key not in entries:
            entries[key] = (machine_id, start)

    # Precedence: operation i+1 cannot start before operation i finishes.
    for job_id, job in enumerate(jobs):
        for op_id in range(len(job) - 1):
            current = (job_id, op_id)
            next_op = (job_id, op_id + 1)
            if current not in entries or next_op not in entries:
                continue
            current_machine, current_start = entries[current]
            _, next_start = entries[next_op]
            current_duration = job[op_id][current_machine]
            current_end = current_start + current_duration
            if next_start < current_end:
                errors.append(
                    f"Precedence violation: J{job_id} O{op_id + 1} "
                    f"starts at {next_start} before J{job_id} O{op_id} finishes at {current_end}"
                )

    # No two operations may overlap on the same machine.
    for machine_id, intervals in machine_intervals.items():
        intervals.sort(key=lambda x: (x[0], x[1], x[2], x[3]))
        for previous, current in zip(intervals, intervals[1:]):
            previous_end = previous[1]
            current_start = current[0]
            if current_start < previous_end:
                errors.append(
                    f"Machine overlap on M{machine_id}: "
                    f"J{previous[2]} O{previous[3]} overlaps J{current[2]} O{current[3]}"
                )

    return errors
