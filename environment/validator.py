# sample schedule = (job_id, operation_id, machine_id, start_time)

'''
IDs => Does this job and operation exist?

Duplicate/missing => Is every operation scheduled exactly once?

Machine eligibility => Is this operation allowed on that machine?

Start time => Does it start at time ≥ 0?

Precedence => Does the previous operation finish before the next starts?

Machine overlap => Is the machine free when this operation starts?
'''

def validate_schedule(instance, schedule):
    jobs = instance["jobs"]
    errors = []

    # Track which operations are scheduled
    seen = set()
    machine_intervals = {}

    # Check each scheduled operation
    for job_id, op_id, machine_id, start in schedule:
        operation = (job_id, op_id)

        # Check job and operation IDs
        if job_id < 0 or job_id >= len(jobs):
            errors.append(f"Invalid job ID: {job_id}")
            continue

        if op_id < 0 or op_id >= len(jobs[job_id]):
            errors.append(f"Invalid operation ID: J{job_id} O{op_id}")
            continue

        # Check duplicate operation
        if operation in seen:
            errors.append(f"Duplicate operation: J{job_id} O{op_id}")
            continue
        seen.add(operation)

        # Check machine eligibility
        eligible = jobs[job_id][op_id]
        if machine_id not in eligible:
            errors.append(
                f"J{job_id} O{op_id} cannot run on M{machine_id}"
            )
            continue

        # Check start time
        if start < 0:
            errors.append(f"Negative start time: J{job_id} O{op_id}")

        duration = eligible[machine_id]
        end = start + duration

        machine_intervals.setdefault(machine_id, []).append(
            (start, end, job_id, op_id)
        )

    # Check that every operation appears exactly once
    for job_id, job in enumerate(jobs):
        for op_id in range(len(job)):
            if (job_id, op_id) not in seen:
                errors.append(f"Missing operation: J{job_id} O{op_id}")

    # Check precedence: each operation must finish before the next starts
    start_times = {
        (j, o): start
        for j, o, m, start in schedule
        if 0 <= j < len(jobs) and 0 <= o < len(jobs[j])
    }

    for job_id, job in enumerate(jobs):
        for op_id in range(len(job) - 1):
            current = (job_id, op_id)
            next_op = (job_id, op_id + 1)

            if current in start_times and next_op in start_times:
                current_machine = schedule[
                    next(i for i, item in enumerate(schedule)
                         if item[0] == job_id and item[1] == op_id)
                ][2]

                current_end = (
                    start_times[current]
                    + job[op_id].get(current_machine, 0)
                )

                if start_times[next_op] < current_end:
                    errors.append(
                        f"Precedence violation: J{job_id} O{op_id + 1}"
                    )

    # Check machine overlap
    for machine_id, intervals in machine_intervals.items():
        intervals.sort()

        for i in range(1, len(intervals)):
            previous_end = intervals[i - 1][1]
            current_start = intervals[i][0]

            if current_start < previous_end:
                errors.append(f"Machine overlap on M{machine_id}")

    return errors
