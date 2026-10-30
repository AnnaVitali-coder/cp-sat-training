from ortools.sat.python import cp_model


def solve_production():

    model = cp_model.CpModel()

    num_workers = 4
    num_tasks = 4

    task_assignment = [
        model.new_int_var(0, num_tasks -1, f"task_assigned_to_worker_{i}")
        for i in range(num_workers)
    ]
    
    task_cost = [
        model.new_int_var(
            min(cost_matrix[i]),
            max(cost_matrix[i]),
            f"task_cost_{i}"
        )
        for i in range(num_workers)
    ]

    cost_matrix = [[9, 2, 7, 8], [6, 4, 3, 7], [5, 8, 1, 8], [7, 6, 9, 4]]
    
    model.add_all_different(task_assignment)
    
    for i in range(num_workers):
        costs = cost_matrix[i]
        model.add_element(task_assignment[i], costs, task_cost[i])

    model.minimize(
        sum(
            task_cost
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
            print(f"Worker {i} assigned to task {solver.value(task_assignment[i])}")
    else:
        print(f"Status: {status}")

    return model, solver


if __name__ == "__main__":
    model, solver = solve_production()

# Output
# Status: OPTIMAL
# Objective: 13.0
# Best bound: 13.0
# Wall time: 0.024003100000000003
# Branches: 40
# Conflicts: 0
# Worker 0 assigned to task 1
# Worker 1 assigned to task 0
# Worker 2 assigned to task 2
# Worker 3 assigned to task 3

# What is the fundamental difference between Formulation A and Formulation B in terms of decision variables?
# we have less decision variables in formulation B


# Why is add_all_different() a natural fit for this problem?
# because it implies the forced assignment to the workers


# What is the purpose of add_element()?
# compute the objective function without becoming mad, associating to the cost variable the cost of the value assigned


# Which formulation do you expect to perform better, and why? Don't just guess based on the number of variables: consider propagation and the internal representation of constraints.
# actually looking at the solving time I think boolean variables is better, even if I know that all_different is strong because the solution is a permutation of the element