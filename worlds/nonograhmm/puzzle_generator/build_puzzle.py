
import copy
# import json

# from tqdm import tqdm

from .generate_random_nonogram import generate_random_clues
from .nonogram_solver import solve_nonogram_simple






def build_up_game(clues, list_of_symbols, random):
    """
    Build up the game state from clues.
    Start with all clue entries replaced by "?" and report how many cells can be
    determined. Then repeatedly pick a random "?" and replace it with the actual
    number from `clues`, re-solve, and report the number of filled/empty cells
    after each replacement and which clue was changed.

    Returns a list of step records: dicts with keys
      - step: int (0 = initial masked state)
      - changed: None or (side, line_index, pos_index, value) where side 0=top,1=left
      - marked: number of marked cells after solving
      - masked_clues: deep copy of the current masked clues
    """

    # deep copy original clues to avoid mutating caller data
    orig = [ [list(cl) for cl in part] for part in (clues[0], clues[1]) ]
    
    sss = solve_nonogram_simple(orig)
    # print("Nonogram solved successfully")
    if sss is False:
        raise Exception("Nonogram: Original clues unsolvable")
    SOL, N = sss
    
    # if SOL doesn't contain any 0s:
    if N == len(clues[0]) * len(clues[1]):
        # print("The provided clues lead to a unique solution!")
        # showSolution(SOL)
        pass
    else:
        # print("The provided clues do not lead to a unique solution.")
        return False
    

    # create masked version: replace each entry in each clue-list with "?"
    masked = [ [ ["?" for _ in cl] for cl in part ] for part in orig ]

    def collect_positions(mask):
        pos = []
        for side in (0, 1):
            for li, cl in enumerate(mask[side]):
                for pi, val in enumerate(cl):
                    if val == "?" or val == 'Ω' or val == 'E':
                        pos.append((side, li, pi))
        return pos

    steps = []
    # initial solve with all "?"
    top_mask = [list(cl) for cl in masked[0]]
    left_mask = [list(cl) for cl in masked[1]]
    # print("Starting initial solve with all clues masked...")
    solution, marked = solve_nonogram_simple([top_mask, left_mask])
    steps.append({
        "step": 0,
        "changed": None,
        "marked": marked,
        "solution": copy.deepcopy(solution),
    })
    step = 1
    positions = collect_positions(masked)
    # print(f"Starting build-up: {marked} cells marked, {len(positions)} clues to reveal.")
    
    # with tqdm(total=len(positions), desc="Building up Nonogram puzzle") as pbar:
    while marked < len(clues[0]) * len(clues[1]):
        side, li, pi = random.choice(positions)
        # install the real value from orig into masked
        value = orig[side][li][pi]
        
        possible_other_clues = []
        if masked[side][li][pi] == '?':
            if value % 2 == 1 and 'Ω' in list_of_symbols:
                possible_other_clues.append('Ω')
            elif value % 2 == 0 and 'E' in list_of_symbols:
                possible_other_clues.append('E')

        if possible_other_clues:
            masked[side][li][pi] = random.choice(possible_other_clues)
        else:
            masked[side][li][pi] = value
            # pbar.update(1)

        # prepare solver input (deep copy to avoid accidental sharing)
        top_mask = [list(cl) for cl in masked[0]]
        left_mask = [list(cl) for cl in masked[1]]
        
        S = solve_nonogram_simple([top_mask, left_mask], grid=copy.deepcopy(solution))
        # print(solution)
        # print(S)
        # print("-")
        
        if not S:
            # print("Error: puzzle became unsolvable after revealing clue", (side, li, pi, value))
            raise Exception("Nonogram: Puzzle became unsolvable")
        solution, marked = S
        
        steps.append({
            "step": step,
            "changed": (side, li, pi, value),
            "marked": marked,
            "solution": copy.deepcopy(solution),
        })
        step += 1
        positions = collect_positions(masked)
    return steps, solution

def showSolution(solution):
    print()
    for row in solution:
        for cell in row:
            print(f"[{cell[0]:2} {cell[1]:3} {cell[2]:1}]", end="")
        print()
    print()

def build_puzzle(options, random):
    x = options.width_of_grid.value
    y = options.height_of_grid.value
    list_of_symbols = options.clue_types.value
    
    
    rando_clues, G = generate_random_clues(x, y, x*y/4, random)
    if not rando_clues:
        return False

    top_clues = rando_clues[0]
    left_clues = rando_clues[1]
    CLUES = [
        top_clues,
        left_clues
    ]

    # print(f"Generated {x}x{y} clues, starting build-up...")
    build_up = build_up_game(CLUES, list_of_symbols, random)
    if not build_up:
        return False
    
    steps = build_up[0]
    
    # print(steps)
    
    clue_order = []
    
    for info in steps:
        clue_order.append((info["changed"], info["marked"]))
    
    start_clues = [['?' for _ in cl] for cl in top_clues], [['?' for _ in cl] for cl in left_clues]
    
    # print(clue_order)
    # print(steps[-1]["solution"])
    
    output = {
        "C": start_clues,
        "G": clue_order,
        "S": steps[-1]["solution"],
    }
    # print(output)
    # showSolution(output["S"])
    
    return output
    