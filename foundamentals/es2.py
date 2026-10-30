from ortools.sat.python import cp_model


def solve_production():

    model = cp_model.CpModel()

    a = model.new_bool_var("a")
    b = model.new_bool_var("b")
    c = model.new_bool_var("c")
    d = model.new_bool_var("d")
    e = model.new_bool_var("e")

    model.add_implication(a, b)
    model.add_at_most_one([c, d]) # at most one is true
    model.add_implication(e, d)

    model.add(5 * a + 4 * b + 3 * c + 2 * d + 6 * e <= 12)

    model.maximize((10 + 3) * a + 7 * b + 6 * c + 4 * d + 11 * e)

    solver = cp_model.CpSolver()

    # 6. Solve
    status = solver.solve(model)

    # 7. Print results
    if status == cp_model.FEASIBLE or status == cp_model.OPTIMAL:
        print("Status:", solver.status_name(status))
        print("Objective:", solver.objective_value)
        print("Best bound:", solver.best_objective_bound)
        print("Wall time:", solver.wall_time)
        print("Branches:", solver.num_branches)
        print("Conflicts:", solver.num_conflicts)
        
        print(f"A: {solver.value(a)}")
        print(f"B: {solver.value(b)}")
        print(f"C: {solver.value(c)}")
        print(f"D: {solver.value(d)}")
        print(f"E: {solver.value(e)}")

    else:
        print(f"Status: {status}")

    return model, solver
# Output
# A: 1
# B: 1
# C: 1
# D: 0
# E: 0

# What is the difference between add_implication(a, b) and add(a <= b)?
# there is no difference if a is 0 b can be 1 which is ok for implication, if a is 1 then b should be 1 and it's domain is in {0,1} so the implication is valid

# Can only_enforce_if() be used to model the same implication? How?
# model.add(b == 1).OnlyEnforceIf(a)

# Why might add_at_most_one() be preferable to manually creating a collection of pairwise constraints when you have many Boolean variables?
# is better for the propagation to use a global constraint, because it was built for it


# What happens if you remove the constraint e ⇒ d? It change nothing because in the optimal solution e and d are false
# removing a constraint enlarge the feasible region making a previously infeasible solution feasible

#One question to think about: Would you prefer to represent the bonus as a coefficient of variable A, or introduce a separate Boolean variable? Why?
# avoiding the introduction of new variables is better

if __name__ == "__main__":
    model, solver = solve_production()
