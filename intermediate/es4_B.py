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

    job_schedule = [
        model.new_fixed_size_interval_var(
            start=start_times[i], size=job_duration[i], name="interval_time_{i}"
        )
        for i in range(num_jobs)
    ]

    waiting = model.new_int_var(0, horizon, "waiting")

    for i in range(num_jobs):
        model.add(start_times[i] >= earliest_time[i])

    model.add_no_overlap(job_schedule)

    waitings = [start_times[i] - earliest_time[i] for i in range(num_jobs)]

    model.add(waiting == sum(waitings))

    model.minimize(waiting)

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
            print(
                f"Job {i} start: {solver.value(start_times[i])} end: {solver.value(start_times[i]) + job_duration[i]}"
            )
    else:
        print(f"Status: {status}")

    return model, solver


if __name__ == "__main__":
    model, solver = solve_production()

# Output
# Status: OPTIMAL
# Objective: 11.0
# Best bound: 11.0
# Wall time: 0.0203505
# Branches: 1
# Conflicts: 0
# Job 0 start: 0 end: 3
# Job 1 start: 5 end: 7
# Job 2 start: 7 end: 11
# Job 3 start: 3 end: 5

# Why do we use an interval variable instead of just a start-time variable?
# Because the jobs have a duration we should consider that for the non overlap constraint


# Does add_no_overlap decide the order of jobs, or do we need to create ordering Boolean variables ourselves?
# it does


# If two jobs have the same release time, does that mean they must start at the same time?
# no just that they can start before that time but after that time they can start and the machine
# can't handle one job at the time so they can't be simultaneous
