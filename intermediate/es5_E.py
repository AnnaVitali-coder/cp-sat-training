from ortools.sat.python import cp_model


def solve_production():

    num_jobs = 4
    processing_time = [3, 2, 4, 2]
    profit = [8, 5, 10, 6]
    

    horizon = 8

    model = cp_model.CpModel()

    start_times = [
        model.new_int_var(0, horizon, f"start_time_job_{i}") for i in range(num_jobs)
    ]
    
    job_selected = [
        model.new_bool_var("job_selected_{i}") for i in range(num_jobs)
    ]

    job_arcs = [
        [model.new_bool_var(f"arc_{i}_{j}") for j in range(num_jobs + 1)]
        for i in range(num_jobs + 1)
    ]

    job_schedule = [
        model.new_optional_fixed_size_interval_var(
            start=start_times[j],
            size=processing_time[j],
            is_present=job_selected[j],
            name=f"interval_time_job_{j}",
        )
        for j in range(num_jobs)
    ]

    end_time = model.new_int_var(0, horizon, "end_time")

    model.add_no_overlap(job_schedule)

    arcs = []

    for i in range(num_jobs + 1):
        for j in range(num_jobs + 1):
            if i == j:
                continue
            
            arcs.append((i, j, job_arcs[i][j]))  
    
    # in this way the node that are not selected are not part of the circuit        
    for i in range(num_jobs):
        node = i + 1
        arcs.append((node, node, job_selected[i].Not()))

    model.add_circuit(arcs)

    for i in range(num_jobs):
        for j in range(num_jobs):
            if i == j:
                continue
            model.add(
                start_times[j]
                >= start_times[i] + processing_time[i]
            ).only_enforce_if([job_arcs[i + 1][j + 1]])


    for i in range(num_jobs):
        model.add(start_times[i] + processing_time[i] <= horizon).only_enforce_if(job_selected[i])
    
    model.maximize(sum([job_selected[i] * profit[i] for i in range(num_jobs)]))

    solver = cp_model.CpSolver()
    status = solver.solve(model)

    if status == cp_model.FEASIBLE or status == cp_model.OPTIMAL:
        print("Status:", solver.status_name(status))
        print("Objective:", solver.objective_value)
        print("Best bound:", solver.best_objective_bound)
        print("Wall time:", solver.wall_time)
        print("Branches:", solver.num_branches)
        print("Conflicts:", solver.num_conflicts)

        print("Schedule:")

        current_node = 0  # Dummy starting node
        previous_job = None

        while True:
            # Find the selected outgoing arc
            next_node = next(
                j for j in range(num_jobs + 1)
                if solver.value(job_arcs[current_node][j])
            )

            # Returning to dummy node means the sequence is complete
            if next_node == 0:
                break

            job = next_node - 1
            start = solver.value(start_times[job])
            end = start + processing_time[job]

            print(f"Job {job}: {start} to {end}")

            current_node = next_node
            previous_job = job
    else:
        print(f"Status: {status}")

    return model, solver


if __name__ == "__main__":
    model, solver = solve_production()

# Output
# Status: OPTIMAL
# Objective: 21.0
# Best bound: 21.0
# Wall time: 0.038212800000000005
# Branches: 216
# Conflicts: 0
# Schedule:
# Job 1: 0 to 2
# Job 2: 2 to 6
# Job 3: 6 to 8