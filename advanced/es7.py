from ortools.sat.python import cp_model


def solve_production():

    num_states = 3
    num_periods = 5
    starting_state = 0
    final_state = [0, 2]
    state_transition  = [
        (0, 0, 0), (0, 1, 1),
        (1, 0, 0), (1, 1, 1), (1, 2, 2),
        (2, 1, 1), (2, 2, 2)
    ]

    model = cp_model.CpModel()

    state = [
        model.new_int_var(0, num_states - 1, f"state_in_period_{i}")
        for i in range(num_periods)
    ]
    
    is_high_production = [model.new_bool_var(f"is_high_production_{i}") for i in range(num_periods)]
    
    model.add_automaton(
        state,
        starting_state,
        final_state,
        state_transition
    )
    
    
    for i in range(num_periods):
        model.add(state[i] == 2).only_enforce_if(is_high_production[i])
        model.add(state[i] != 2).only_enforce_if(is_high_production[i].Not())

    model.add(sum(is_high_production) >= 2)    
    
    model.minimize(sum(is_high_production))
    
    solver = cp_model.CpSolver()
    status = solver.solve(model)

    if status == cp_model.FEASIBLE or status == cp_model.OPTIMAL:
        print("Status:", solver.status_name(status))
        print("Objective:", solver.objective_value)
        print("Best bound:", solver.best_objective_bound)
        print("Wall time:", solver.wall_time)
        print("Branches:", solver.num_branches)
        print("Conflicts:", solver.num_conflicts)

        for i in range(num_periods):
            print(f"State in period {i}: {solver.value(state[i])}")
        
    else:
        print(f"Status: {status}")

    return model, solver


if __name__ == "__main__":
    model, solver = solve_production()

# Output
# Status: OPTIMAL
# Objective: 2.0
# Best bound: 2.0
# Wall time: 0.0157597
# Branches: 41
# Conflicts: 0
# State in period 0: 1
# State in period 1: 1
# State in period 2: 1
# State in period 3: 2
# State in period 4: 2