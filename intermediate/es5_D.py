from ortools.sat.python import cp_model


def solve_production():

    num_jobs = 3
    num_machines = 1

    processing_time = [3, 2, 4]
    release_time = [0, 5, 0]
    job_switching = [[0, 2, 1], [3, 0, 2], [2, 1, 0]]

    horizon = (
        max(release_time)
        + sum(processing_time)
        + (num_jobs - 1) * max(max(row) for row in job_switching)
    )

    model = cp_model.CpModel()

    start_times = [
        model.new_int_var(0, horizon, f"start_time_job_{i}") for i in range(num_jobs)
    ]

    job_arcs = [
        [model.new_bool_var(f"arc_{i}_{j}") for j in range(num_jobs + 1)]
        for i in range(num_jobs + 1)
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

    model.add_no_overlap(job_schedule)

    for i in range(num_jobs):
        model.add(start_times[i] >= release_time[i])

    arcs = []

    for i in range(num_jobs + 1):
        for j in range(num_jobs + 1):
            if i == j:
                continue
            else:
                arcs.append((i, j, job_arcs[i][j]))

    model.add_circuit(arcs)

    for i in range(num_jobs):
        for j in range(num_jobs):
            if i == j:
                continue
            model.add(
                start_times[j]
                >= start_times[i] + processing_time[i] + job_switching[i][j]
            ).only_enforce_if(job_arcs[i + 1][j + 1])

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

            if previous_job is not None:
                setup = job_switching[previous_job][job]
                previous_end = (
                    solver.value(start_times[previous_job])
                    + processing_time[previous_job]
                )

                print(
                    f"Setup Job {previous_job} -> Job {job}: "
                    f"{previous_end} to {previous_end + setup}"
                )

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
# Objective: 11.0
# Best bound: 11.0
# Wall time: 0.026464900000000003
# Branches: 86
# Conflicts: 1
# Schedule:
# Job 0: 0 to 3
# Setup Job 0 -> Job 2: 3 to 4
# Job 2: 4 to 8
# Setup Job 2 -> Job 1: 8 to 9
# Job 1: 9 to 11