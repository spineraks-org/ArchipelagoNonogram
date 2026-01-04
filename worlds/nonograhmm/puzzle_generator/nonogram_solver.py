
from .figure_out_line import get_sure_squares

def showSolution(solution):
    print()
    for row in solution:
        for cell in row:
            print(f"[{cell[0]:2} {cell[1]:3} {cell[2]:1}]", end="")
        print()
    print()

def solve_nonogram_simple(all_clues, grid = None):    
    next_clue = (max(cell[1] for row in grid for cell in row) if grid else 0) + 1
    # print(next_clue)
    
    #  1 is filled, -1 is empty, 0 is unknown
    X = len(all_clues[0])
    Y = len(all_clues[1])
    if grid is None:
        grid = [[[0, 0, -1] for _ in range(X)] for _ in range(Y)]
    
    todo = []
    todo += [(0, c) for c in range(X)]
    todo += [(1, r) for r in range(Y)]
    
    steps = 0
    while todo:
        # pp(grid)
        # print()
        this_todo = todo.pop(0)
        side, index = this_todo
        if side == 0:
            c = index
            clues = all_clues[0][c]
            grid_part_1 = [grid[r][c][0] for r in range(Y)]
            
            sol = get_sure_squares(clues, grid_part_1)
            if sol is False:
                return False
            for r in range(Y):
                if grid[r][c][0] == 0 and sol[r] != 0:
                    todo.append((1, r))
                    grid[r][c] = [sol[r], next_clue, side]
                    # print("1 setting grid[",r,"][",c,"] to", sol[r] * next_clue)
                    next_clue += 1
                    # showSolution(grid)
                
        else:
            r = index
            clues = all_clues[1][r]
            grid_part = [cell[0] for cell in grid[r]]
            sol = get_sure_squares(clues, grid_part)
            if sol is False:
                print("Unsolvable line detected at row", r)
                return False
            for c in range(X):
                if grid[r][c][0] == 0 and sol[c] != 0:
                    todo.append((0, c))
                    grid[r][c] = [sol[c], next_clue, side]
                    # print("2 setting grid[",r,"][",c,"] to", sol[c] * next_clue)
                    next_clue += 1
                    # showSolution(grid)
    amount_sure = sum(1 for r in range(Y) for c in range(X) if grid[r][c][0] != 0)
    return grid, amount_sure

if __name__ == "__main__":
    top_clues = [[4],[3,1],[2,2],[2,1],[3]]
    left_clues = [[2],[5],[2,2],[1,1,1],[4]]
    clues = [top_clues, left_clues]
    
    grid = [[1, 1, 1, 1, -1],
        [1, 1, 1, 1, 1],
        [-1, -1, 1, -1, 1],
        [1, 1, 1, -1, 1],
        [-1, 1, 1, 1, 1]]
    
    s = solve_nonogram_simple(clues)
    print(s)