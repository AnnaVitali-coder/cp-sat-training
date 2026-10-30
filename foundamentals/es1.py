from ortools.sat.python import cp_model
import sys

def main():

    # 1. Create the model
    model = cp_model.CpModel()

    # 2. Create decision variables
    x = model.new_int_var(0, 10, name="quantity_A")
    y = model.new_int_var(0, 10, name="quantity_B")

    # 3. Add constraints
    model.add(2 * x + 4 * y <= 40)
    model.add(3 * x + 2 * y <= 30)

    # 4. Define objective
    model.maximize(30 * x + 50 * y)

    # 5. Create solver
    solver = cp_model.CpSolver()

    # 6. Solve
    status = solver.solve(model)

    # 7. Print results
    if status == cp_model.FEASIBLE or status == cp_model.OPTIMAL:
        print(f"Quantity A: {solver.value(x)}")
        print(f"Quantity B: {solver.value(y)}")
    else:
        print(f"Status: {status}")
        

if __name__ == "__main__":
    main()
    
# Output
# Quantity A: 4
# Quantity B: 8 
    
# Q1. Why is it important to define tight variable domains in CP-SAT? because this reduces the search space

# Q2. What is the difference between a feasible solution and a proven optimal solution? a feasible
# solution means that maybe there is another which is better, an optimal solution means 
# that for the objective function considered this is the best value it can reach

# Q3. If you remove the raw-material constraint, how does the optimal solution change? The B product can be not produced since A allow us to earn more money