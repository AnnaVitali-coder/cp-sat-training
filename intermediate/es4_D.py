from ortools.sat.python import cp_model


def solve_production():

    model = cp_model.CpModel()

    num_jobs = 4
    job_duration = [3, 2, 4, 2]
    earliest_time = [0, 1, 0, 3]
    technicians_required = [2, 2, 1, 1]
    num_technicians = 3
    num_machines = 3

    horizon = sum(job_duration) + max(earliest_time)

    start_times = [
        model.new_int_var(0, horizon, f"start_time_{i}") for i in range(num_jobs)
    ]

    job_assignment = [
        [
            model.new_bool_var(f"job_{j}_assigned_to_machine_{i}")
            for j in range(num_jobs)
        ]
        for i in range(num_machines)
    ]

    job_schedule = [
        [
            model.new_optional_fixed_size_interval_var(
                start=start_times[j],
                size=job_duration[j],
                is_present=job_assignment[i][j],
                name=f"interval_time_{j}_machine_{i}",
            )
            for j in range(num_jobs)
        ]
        for i in range(num_machines)
    ]

    makespan = model.new_int_var(0, horizon, "makespan")

    for i in range(num_jobs):
        model.add(start_times[i] >= earliest_time[i])
        model.add_exactly_one([row[i] for row in job_assignment])

    for i in range(num_machines):
        model.add_no_overlap(job_schedule[i])

    flatten_schedule = [var for row in job_schedule for var in row]
    flatten_technicians_required = [
        technicians_required[j] for i in range(num_machines) for j in range(num_jobs)
    ]

    model.add_cumulative(
        flatten_schedule, flatten_technicians_required, num_technicians
    )

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

        for i in range(num_machines):
            for j in range(num_jobs):
                if solver.value(job_assignment[i][j]):
                    print(
                        f"Job {j} on machine {i} start: {solver.value(start_times[j])} end: {solver.value(start_times[j]) + job_duration[j]} technicians: {technicians_required[j]}"
                    )
    else:
        print(f"Status: {status}")

    return model, solver


if __name__ == "__main__":
    model, solver = solve_production()

# Output
# Status: OPTIMAL
# Objective: 6.0
# Best bound: 6.0
# Wall time: 0.02172
# Branches: 27
# Conflicts: 3
# Job 2 on machine 0 start: 0 end: 4 technicians: 1
# Job 1 on machine 1 start: 3 end: 5 technicians: 2
# Job 0 on machine 2 start: 0 end: 3 technicians: 2
# Job 3 on machine 2 start: 4 end: 6 technicians: 1

