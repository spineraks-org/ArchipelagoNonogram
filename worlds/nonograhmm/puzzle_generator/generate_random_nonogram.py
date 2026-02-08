
from .nonogram_solver import solve_nonogram_simple

def get_clues_from_grid(grid):
    x = len(grid[0])
    y = len(grid)
    # Function to calculate clues for a single line (row or column)
    def calculate_clues(line):
        clues = []
        count = 0
        for cell in line:
            if cell == 1:
                count += 1
            else:
                if count > 0:
                    clues.append(count)
                    count = 0
        if count > 0:
            clues.append(count)
        return clues if clues else []

    # Calculate row clues
    row_clues = [calculate_clues(row) for row in grid]

    # Calculate column clues
    column_clues = [calculate_clues([grid[row][col] for row in range(y)]) for col in range(x)]
    
    return [column_clues, row_clues]

def generate_random_clues(x, y, n_white, random):
    # print("Generating random clues for grid size", x, "x", y, "with desired white", n_white)
    grid = [[1 for _ in range(x)] for _ in range(y)]
    W = 0

    number_to_change = x*y/8 + 1
    for _ in range(100000):
        int_number_to_change = int(max(1, number_to_change))
        indcs = [(random.randrange(y), random.randrange(x)) for _ in range(int_number_to_change)]
        if all(grid[Y][X] == -1 for Y, X in indcs):
            continue
        for Y, X in indcs:
            grid[Y][X] = -1
        clues = get_clues_from_grid(grid)
            
        sol = solve_nonogram_simple(clues)  # have to start with empty grid!

        g, am_s = sol
        if not g or am_s < x * y:  # no unique solution, reset
            for Y, X in indcs:
                grid[Y][X] = 1
            number_to_change -= 1
            continue
        else:
            W += int_number_to_change
            last_solution = g
        
        if W > n_white:
            return clues, grid
    
    return clues, grid
  