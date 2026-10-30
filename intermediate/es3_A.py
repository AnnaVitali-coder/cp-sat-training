from ortools.sat.python import cp_model


def solve_production():

    model = cp_model.CpModel()

    num_workers = 4
    num_tasks = 4

    task_assignment = [
        [model.new_bool_var(f"worker_{i}_task_{j}") for j in range(num_tasks)]
        for i in range(num_workers)
    ]

    cost_matrix = [[9, 2, 7, 8], [6, 4, 3, 7], [5, 8, 1, 8], [7, 6, 9, 4]]

    for i in range(num_workers):
        model.add_exactly_one([task_assignment[i][j] for j in range(num_tasks)])

    # my implementation but we could do the same as before but with the columns
    # for w1 in range(num_workers):
    #     for w2 in range(num_workers):
    #         if w1 == w2:
    #             continue
    #         for t in range(num_tasks):
    #             model.add_implication(
    #                 task_assignment[w1][t], task_assignment[w2][t].Not()
    # )
    
    for j in range(num_tasks):
        model.add_exactly_one([task_assignment[i][j] for i in range(num_workers)])


    model.minimize(
        sum(
            cost_matrix[i][j] * task_assignment[i][j]
            for j in range(num_tasks)
            for i in range(num_workers)
        )
    )

    solver = cp_model.CpSolver()

    status = solver.solve(model)

    if status == cp_model.FEASIBLE or status == cp_model.OPTIMAL:
        print("Status:", solver.status_name(status))
        print("Objective:", solver.objective_value)
        print("Best bound:", solver.best_objective_bound)
        print("Wall time:", solver.wall_time)
        print("Branches:", solver.num_branches)
        print("Conflicts:", solver.num_conflicts)

        for i in range(num_workers):
            for j in range(num_tasks):
                if solver.value(task_assignment[i][j]):
                    print(f"Worker {i} assigned to task {j}")
    else:
        print(f"Status: {status}")

    return model, solver


if __name__ == "__main__":
    model, solver = solve_production()

# Output
# Status: OPTIMAL
# Objective: 13.0
# Best bound: 13.0
# Wall time: 0.0134409
# Branches: 41
# Conflicts: 0
# Worker 0 assigned to task 1
# Worker 1 assigned to task 0
# Worker 2 assigned to task 2
# Worker 3 assigned to task 3 