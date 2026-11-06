from ortools.sat.python import cp_model


def solve_production():

    num_jobs = 3
    num_machines = 2
    num_operations = 2
    # operations_machine = [[0, 1, 0], [1, 0, 1], [0, 1, 0]]
    operations_duration = [
        [[3, 4], [2, 3]],
        [[2, 3], [4, 2]],
        [[3, 2], [2, 4]],
    ]

    horizon = sum(max(inner) for row in operations_duration for inner in row)

    model = cp_model.CpModel()

    start_times = [
        [
            model.new_int_var(0, horizon, f"start_time_job_{i}_operation{j}")
            for j in range(num_operations)
        ]
        for i in range(num_jobs)
    ]

    durations = [
        [
            model.new_int_var(0, horizon, f"duration_job_{i}_operation{j}")
            for j in range(num_operations)
        ]
        for i in range(num_jobs)
    ]

    end_times = [
        [
            model.new_int_var(0, horizon, f"end_time_job_{i}_operation{j}")
            for j in range(num_operations)
        ]
        for i in range(num_jobs)
    ]

    operations_on_machine = [
        [
            [
                model.new_bool_var(f"is_operation_{o}_for_job_{j}_on_machine_{i}")
                for o in range(num_operations)
            ]
            for j in range(num_jobs)
        ]
        for i in range(num_machines)
    ]

    job_schedule = [
        [
            [
                model.new_optional_interval_var(
                    start=start_times[j][o],
                    size=durations[j][o],
                    end=end_times[j][o],
                    is_present=operations_on_machine[i][j][o],
                    name=f"interval_time_job_{j}_operation_{o}_machine_{i}",
                )
                for o in range(num_operations)
            ]
            for j in range(num_jobs)
        ]
        for i in range(num_machines)
    ]

    makespan = model.new_int_var(0, horizon, "makespan")
    
    for i in range(num_jobs):
        for o in range(num_operations):
            model.add_exactly_one(
                [operations_on_machine[m][i][o] for m in range(num_machines)]
            )
    
    # operations on machine can not overlap
    for m in range(num_machines):
        machine_intervals = [
            job_schedule[m][i][j]
            for i in range(num_jobs)
            for j in range(num_operations)
        ]
        
        model.add_no_overlap(machine_intervals)
        
    # operations should respect the duration of the machine assigned
    for m in range(num_machines):
        for i in range(num_jobs):
            for j in range(num_operations):
                model.add(durations[i][j] == operations_duration[i][j][m]).only_enforce_if(operations_on_machine[m][i][j])

    for i in range(num_jobs):
        for j in range(num_operations - 1):
            model.add(
                start_times[i][j + 1] >= start_times[i][j] + durations[i][j]
            )
            
    for i in range(num_jobs):
        for j in range(num_operations): 
            model.add(end_times[i][j] == start_times[i][j] + durations[i][j])

    ends = [
        end_times[i][j]
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

        for m in range(num_machines):
            for i in range(num_jobs):
                for j in range(num_operations):
                    if solver.value(operations_on_machine[m][i][j]):
                        print(
                            f"Operation {j} for job {i} on machine {m} start: {solver.value(start_times[i][j])} end: {solver.value(end_times[i][j])}"
                        )

    else:
        print(f"Status: {status}")

    return model, solver


if __name__ == "__main__":
    model, solver = solve_production()

# Output
# Status: OPTIMAL
# Objective: 7.0
# Best bound: 7.0
# Wall time: 0.0129607
# Branches: 38
# Conflicts: 0
# Operation 0 for job 0 on machine 0 start: 0 end: 3
# Operation 1 for job 0 on machine 0 start: 5 end: 7
# Operation 1 for job 2 on machine 0 start: 3 end: 5
# Operation 0 for job 1 on machine 1 start: 2 end: 5
# Operation 1 for job 1 on machine 1 start: 5 end: 7
# Operation 0 for job 2 on machine 1 start: 0 end: 2

#Why is it perfectly valid to have multiple optional intervals sharing the same start, 
# duration, and end variables, even though they represent different machine alternatives?

# because since there are optional variables only if they are true the constraints will be enforced