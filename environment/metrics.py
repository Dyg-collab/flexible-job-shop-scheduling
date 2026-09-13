def get_job_completion_time(instance,schedule):

    job_completion_time = {}

    for operation in schedule:
        job_id,operation_id,machine_id,start_time = operation

        duration = instance["jobs"][job_id][operation_id][machine_id]
        end_time = start_time + duration

        job_completion_time[job_id] = max(job_completion_time.get(job_id,0),end_time)

    return job_completion_time

def get_makespan(instance,schedule):
    job_completion_time = get_job_completion_time(instance,schedule)

    return max(job_completion_time.values(),default=0)