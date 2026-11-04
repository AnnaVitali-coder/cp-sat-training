from ortools.sat.python import cp_model


def solve_production():

    model = cp_model.CpModel()

    num_jobs = 4
    job_duration = [3, 2, 4, 2]
    earliest_time = [0, 1, 0, 3]
    
    horizon = sum(job_duration) + max(earliest_time)

    start_times = [
        model.new_int_var(0, horizon, f"start_time_{i}")
        for i in range(num_jobs)
    ]
    
    job_assigned_to_1 = [
        model.new_bool_var(f"job_{i}_assigned_to_machine_1")
            for i in range(num_jobs)
    ]
    
    job_assigned_to_2 = [
        model.new_bool_var(f"job_{i}_assigned_to_machine_2")
            for i in range(num_jobs)
    ]

    job_schedule_machine_1 = [
        model.new_optional_fixed_size_interval_var(
            start=start_times[i], size=job_duration[i], is_present=job_assigned_to_1[i], name=f"interval_time_{i}_machine_1"
        )
        for i in range(num_jobs)
    ]
    
    job_schedule_machine_2 = [
        model.new_optional_fixed_size_interval_var(
            start=start_times[i], size=job_duration[i], is_present=job_assigned_to_2[i], name=f"interval_time_{i}_machine_2"
        )
        for i in range(num_jobs)
    ]

    makespan = model.new_int_var(0, horizon, "waiting")

    for i in range(num_jobs):
        model.add(start_times[i] >= earliest_time[i])
        model.add_exactly_one([job_assigned_to_1[i], job_assigned_to_2[i]])   
    
    model.add_no_overlap(job_schedule_machine_1)
    model.add_no_overlap(job_schedule_machine_2)

    ends = [start_times[i] + job_duration[i] for i in range(num_jobs)]

    model.add_max_equality(makespan, ends)

    model.minimize(makespan)

    solver = cp_model.CpSolver()
    status = solver.solve(model)

    if status == cp_model.FEASIBLE or status == cp_model.OPTIMAL:
        print("Status:", solver.status_name(status))
        print("Objective:", solver.objective_value)
        print("Best bound:", solver.best_objective_bound)
        print("Wall time:", solver.wall_time)
        print("Branches:", solver.num_branches)
        print("Conflicts:", solver.num_conflicts)

        for i in range(num_jobs):
            if solver.value(job_assigned_to_1[i]):
                print(
                    f"Job {i} on machine 1 start: {solver.value(start_times[i])} end: {solver.value(start_times[i]) + job_duration[i]}"
                )
            elif solver.value(job_assigned_to_2[i]):
                print(
                    f"Job {i} on machine 2 start: {solver.value(start_times[i])} end: {solver.value(start_times[i]) + job_duration[i]}"
                )
            else:
                print(f"Job {i} not assigned")
    else:
        print(f"Status: {status}")

    return model, solver


if __name__ == "__main__":
    model, solver = solve_production()

# Output
# Status: OPTIMAL
# Objective: 6.0
# Best bound: 6.0
# Wall time: 0.0182977
# Branches: 23
# Conflicts: 0
# Job 0 on machine 2 start: 3 end: 6
# Job 1 on machine 2 start: 1 end: 3
# Job 2 on machine 1 start: 0 end: 4
# Job 3 on machine 1 start: 4 end: 6

#Why do we need two optional intervals per job, rather than one ordinary interval shared between the two machines?
# cause otherwise the jobs can't start simultaneously on the different machines