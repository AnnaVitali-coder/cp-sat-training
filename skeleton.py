from ortools.sat.python import cp_model


def solve_production():

    model = cp_model.CpModel()

    # TODO 1: Define variables

    # TODO 2: Add resource constraints

    # TODO 3: Define objective

    solver = cp_model.CpSolver()

    # TODO 4: Solve

    # TODO 5: Extract solution

    return model, solver


if __name__ == "__main__":
    model, solver = solve_production()