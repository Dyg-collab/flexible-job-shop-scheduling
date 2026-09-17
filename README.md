# FJSP Project - Beginner Baseline

This project implements a small experimental pipeline for the Flexible Job-Shop Scheduling Problem (FJSP).

## Pipeline

1. Generate an FJSP instance.
2. Produce a candidate schedule.
3. Validate the schedule independently.
4. Calculate makespan.
5. Repeat over multiple random seeds.
6. Compare algorithms on the same instances.

## Schedule representation

Each schedule entry is:

```text
(job_id, operation_id, machine_id, start_time)
```

## Algorithms

### `greedy_job_order`

This is the original project baseline. It processes jobs in input order and, for each operation, chooses the eligible machine that gives the earliest completion time.

### `greedy_global_dispatch`

This is the first improvement. At each decision point it considers the next unscheduled operation of every job and chooses the operation-machine pair with the earliest possible completion time.

## Run

From the project root:

```bash
python -m algorithms.main
```

The experiment runner compares both algorithms on the same generated instances and writes `results.csv`.

## Run tests

```bash
python -m unittest discover -s tests
```

## Important next improvements

- Add controlled instance classes for low/high flexibility, bottlenecks, high processing-time variance, and machine advantage.
- Add summary statistics by instance class.
- Add plots of makespan versus problem characteristics.
- Add a local-search algorithm that starts from a valid schedule and improves it.
