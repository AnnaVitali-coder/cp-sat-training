from ortools.sat.python import cp_model


def solve_production():

    num_levels = 4
    num_production_lines = 3
    production_quantity = [0, 10, 20, 30]
    production_cost = [0, 7, 12, 20]

    model = cp_model.CpModel()

    production = [
        model.new_int_var(0, max(production_quantity), f"production_quantity_line_{i}")
        for i in range(num_production_lines)
    ]
    
    cost = [
        model.new_int_var(0, max(production_cost), f"cost_line_{i}")
        for i in range(num_production_lines)
    ]
    
    level = [
        model.new_int_var(0, num_levels - 1, f"level_production_line_{i}")
        for i in range(num_production_lines)
    ]
    
    for i in range(num_production_lines):
        model.add_element(level[i], production_quantity, production[i])
        model.add_element(level[i], production_cost, cost[i])
        
    model.add(sum(production) >= 50)
    
    model.minimize(sum(cost))
    
    solver = cp_model.CpSolver()
    status = solver.solve(model)

    if status == cp_model.FEASIBLE or status == cp_model.OPTIMAL:
        print("Status:", solver.status_name(status))
        print("Objective:", solver.objective_value)
        print("Best bound:", solver.best_objective_bound)
        print("Wall time:", solver.wall_time)
        print("Branches:", solver.num_branches)
        print("Conflicts:", solver.num_conflicts)

        for i in range(num_production_lines):
            print(f"Line {i} production: {solver.value(production[i])} cost: {solver.value(cost[i])}")
        
    else:
        print(f"Status: {status}")

    return model, solver


if __name__ == "__main__":
    model, solver = solve_production()

# Output
# Status: OPTIMAL
# Objective: 31.0
# Best bound: 31.0
# Wall time: 0.0388909
# Branches: 23
# Conflicts: 1
# Line 0 production: 20 cost: 12
# Line 1 production: 20 cost: 12
# Line 2 production: 10 cost: 7

# Why is add_element useful here compared with writing several only_enforce_if constraints for each possible level?
# because we can have a correspondence of the level with cost and production directly and even for the objective is useful. We don't need to check 
# the level to know the quantity we already have this mapping