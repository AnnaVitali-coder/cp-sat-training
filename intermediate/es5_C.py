from ortools.sat.python import cp_model


def solve_production():

    num_jobs = 3
    num_machines = 1

    processing_time = [3, 2, 4]
    job_switching = [[0, 2, 1], [3, 0, 2], [2, 1, 0]]

    horizon = sum(processing_time) + (num_jobs - 1) * max(
        max(row) for row in job_switching
    )

    model = cp_model.CpModel()

    start_times = [
        model.new_int_var(0, horizon, f"start_time_job_{i}") for i in range(num_jobs)
    ]

    job_sequence = [
        model.new_int_var(0, num_jobs - 1, f"job_{i}_sequence") for i in range(num_jobs)
    ]

    job_position = [
        model.new_int_var(0, num_jobs - 1, f"position_job_{i}") for i in range(num_jobs)
    ]

    job_schedule = [
        model.new_fixed_size_interval_var(
            start=start_times[j],
            size=processing_time[j],
            name=f"interval_time_job_{j}",
        )
        for j in range(num_jobs)
    ]

    makespan = model.new_int_var(0, horizon, "makespan")

    model.add_all_different(job_sequence)
    model.add_all_different(job_position)
    model.add_no_overlap(job_schedule)

    for i in range(num_jobs):
        model.add_element(job_position[i], job_sequence, i)

    for i in range(num_jobs):
        for j in range(num_jobs):
            if i == j:
                continue
            i_before_j = model.new_bool_var(f"{i}_before_{j}")
            model.add(job_position[j] == job_position[i] + 1).only_enforce_if(
                i_before_j
            )
            model.add(job_position[j] != job_position[i] + 1).only_enforce_if(
                i_before_j.Not()
            )

            model.add(
                start_times[j]
                >= start_times[i] + processing_time[i] + job_switching[i][j]
            ).only_enforce_if(i_before_j)
            
    ends = [start_times[i] + processing_time[i] for i in range(num_jobs)]

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

        print("Schedule")
        for i in range(num_jobs - 1):
            print(f"{solver.value(job_sequence[i])} -> ", end="")

        print(f"{solver.value(job_sequence[num_jobs - 1])}")

        for i in range(num_jobs):
            print(
                f"Job {i} start: {solver.value(start_times[i])} end: {solver.value(start_times[i]) + processing_time[i]}"
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
# Wall time: 0.0205759
# Branches: 85
# Conflicts: 5
# Schedule
# 0 -> 2 -> 1
# Job 0 start: 0 end: 3
# Job 1 start: 9 end: 11
# Job 2 start: 4 end: 8

# Why isn't add_no_overlap alone sufficient to enforce setup times?
# because it don't consider the loading time just the start and the processing

# And one additional challenge: what would happen if setup times were asymmetric, for example, Job A → B takes 2 units, but Job B → A takes 3?
# it will probability choose the switch that take less
