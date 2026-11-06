from ortools.sat.python import cp_model


def solve_production():

    num_production_lines = 3
    speed_temperature_matrix  = [
        [1, 100],
        [1, 150],
        [2, 150],
        [2, 200],
        [3, 200],
    ]
    
    max_speed = max(row[0] for row in speed_temperature_matrix)
    max_temperature = max(row[1] for row in speed_temperature_matrix)
    
    num_levels = 3
    speed_available = [1, 2, 3]
    temperature_available = [100, 150, 200]

    model = cp_model.CpModel()

    production = [
        model.new_int_var(0, 30 * max_speed - (max_temperature // 10) , f"production_quantity_line_{i}")
        for i in range(num_production_lines)
    ]
    
    speed_level = [
        model.new_int_var(0, num_levels - 1, f"speed_line_{i}")
        for i in range(num_production_lines)
    ]
    
    temperature_level = [
        model.new_int_var(0, num_levels - 1, f"temperature_line_{i}")
        for i in range(num_production_lines)
    ]
    
    speed = [
            model.new_int_var(1, max(speed_available), f"speed_line_{i}")
            for i in range(num_production_lines)
        ]
        
    temperature = [
        model.new_int_var(100, max(temperature_available), f"temperature_line_{i}")
        for i in range(num_production_lines)
    ]
    
    for i in range(num_production_lines):
        division_result = model.new_int_var(0, max_temperature, f"division_res_production_{i}")
        
        model.add_element(speed_level[i], speed_available, speed[i])
        model.add_element(temperature_level[i], temperature_available, temperature[i])
        
        model.add_division_equality(division_result, temperature[i], 10)
        model.add(production[i] == 30 * speed[i] - division_result)
    
    model.add(sum(production) >= 80)
    
    for i in range(num_production_lines):
        model.add_allowed_assignments(
            [speed[i], temperature[i]], speed_temperature_matrix
        )
    
    model.minimize(sum(temperature))
    
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
            print(f"Line {i} production: {solver.value(production[i])} speed: {solver.value(speed[i])} temperature: {solver.value(temperature[i])}")
        
    else:
        print(f"Status: {status}")

    return model, solver


if __name__ == "__main__":
    model, solver = solve_production()

# Output
# Status: OPTIMAL
# Objective: 350.0
# Best bound: 350.0
# Wall time: 0.0150892
# Branches: 37
# Conflicts: 0
# Line 0 production: 45 speed: 2 temperature: 150
# Line 1 production: 20 speed: 1 temperature: 100
# Line 2 production: 20 speed: 1 temperature: 100