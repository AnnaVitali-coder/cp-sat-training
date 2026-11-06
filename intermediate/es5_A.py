from ortools.sat.python import cp_model


def solve_production():

    num_jobs = 3
    num_machines = 2
    num_operations = 3
    operations_machine = [[0, 1, 0], [1, 0, 1], [0, 1, 0]]
    operations_duration_precedence = [[3, 2, 2], [2, 4, 3], [2, 3, 1]]

    horizon = sum(sum(row) for row in operations_duration_precedence)

    model = cp_model.CpModel()

    start_times = [
        [
            model.new_int_var(0, horizon, f"start_time_{i}_operation{j}")
            for j in range(num_operations)
        ]
        for i in range(num_jobs)
    ]

    job_schedule = [
        [
            model.new_fixed_size_interval_var(
                start=start_times[i][j],
                size=operations_duration_precedence[i][j],
                name=f"interval_time_{j}_machine_{i}",
            )
            for j in range(num_operations)
        ]
        for i in range(num_jobs)
    ]

    makespan = model.new_int_var(0, horizon, "makespan")
    
    for m in range(num_machines):
        intervals_on_machine = [
            job_schedule[i][j] for i in range(num_jobs) for j in range(num_operations) if operations_machine[i][j] == m
        ]
        model.add_no_overlap(intervals_on_machine)

    for i in range(num_jobs):
        for j in range(num_operations - 1):
            model.add(
                start_times[i][j + 1]
                >= start_times[i][j] + operations_duration_precedence[i][j]
            )

    ends = [
        start_times[i][j] + operations_duration_precedence[i][j]
        for i in range(num_jobs)
        for j in range(num_operations)
    ]

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
            for j in range(num_operations):
                print(
                    f"Operation {j} for job {i} on machine {operations_machine[i][j]} start: {solver.value(start_times[i][j])} end: {solver.value(start_times[i][j] + operations_duration_precedence[i][j])}"
                )

    else:
        print(f"Status: {status}")

    return model, solver


if __name__ == "__main__":
    model, solver = solve_production()

# Output 
# Status: OPTIMAL
# Objective: 12.0
# Best bound: 12.0
# Wall time: 0.0247882
# Branches: 17
# Conflicts: 0
# Operation 0 for job 0 on machine 0 start: 0 end: 3
# Operation 1 for job 0 on machine 1 start: 3 end: 5
# Operation 2 for job 0 on machine 0 start: 9 end: 11
# Operation 0 for job 1 on machine 1 start: 0 end: 2
# Operation 1 for job 1 on machine 0 start: 5 end: 9
# Operation 2 for job 1 on machine 1 start: 9 end: 12
# Operation 0 for job 2 on machine 0 start: 3 end: 5
# Operation 1 for job 2 on machine 1 start: 5 end: 8
# Operation 2 for job 2 on machine 0 start: 11 end: 12

# Why is add_no_overlap alone insufficient to model this problem?
# Because there is also a precedence to respect between the various tasks