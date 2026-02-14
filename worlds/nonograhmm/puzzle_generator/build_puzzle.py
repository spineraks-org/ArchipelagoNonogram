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
    
    # print("7 Starting build-up game... ", time.time())

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
        raise Exception(f"The provided clues do not lead to a unique solution (only {N} cells determined), clues: {clues}")
    
    # print("Original clues verified, time: ", time.time())

    # create masked version: replace each entry in each clue-list with "?"
    masked = [ [ ["?" for _ in cl] for cl in part ] for part in orig ]

    def collect_positions(mask):
        pos = []
        for side in (0, 1):
            for li, cl in enumerate(mask[side]):
                for pi, val in enumerate(cl):
                    if val == "?" or val == 'Ω' or val == 'E' or '/' in str(val) or '-' in str(val) or '+' in str(val):
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
    })
    step = 1
    positions = collect_positions(masked)
    
    # print(f"Starting build-up: {marked} cells marked, {len(positions)} clues to reveal, time: ", time.time())
    
    # with tqdm(total=len(positions), desc="Building up Nonogram puzzle") as pbar:
    while positions:
        side, li, pi = random.choice(positions)
        # install the real value from orig into masked
        value = orig[side][li][pi]
        
        possible_other_clues = []
        if masked[side][li][pi] == '?':
            possible_directions = []
            if value % 2 == 1 and 'Ω' in list_of_symbols:
                possible_directions.append('Ω')
                possible_directions.append('Ω')
            if value % 2 == 0 and 'E' in list_of_symbols:
                possible_directions.append('E')
                possible_directions.append('E')
            if '/' in list_of_symbols:
                possible_directions.append('/')
            if '-' in list_of_symbols:
                possible_directions.append('-')
            if '+' in list_of_symbols:
                possible_directions.append('+')
            
            if possible_directions:
                direction = random.choice(possible_directions)
                
                if direction == 'Ω':
                    possible_other_clues.append('Ω')
                elif direction == 'E':
                    possible_other_clues.append('E')
                elif direction == '/':
                    if value == 1:
                        other_value = value + random.choice([1,2])
                    elif value == 2:
                        other_value = value + random.choice([-1,1,2])
                    else:
                        other_value = value + random.choice([-2,-1,1,2])
                    clue = f"{min(value, other_value)}/{max(value, other_value)}"
                    possible_other_clues.append(clue)
                elif direction == '-':
                    other_value = value + random.randint(1,3)
                    clue = f"{other_value}-"
                    possible_other_clues.append(clue)
                elif direction == '+':
                    other_value = max(1, value - random.randint(1,3))
                    clue = f"{other_value}+"
                    possible_other_clues.append(clue)
                else:
                    raise Exception("Nonogram: Unknown clue type selected")
                

        new_value = None
        if possible_other_clues:
            masked[side][li][pi] = random.choice(possible_other_clues)
            new_value = masked[side][li][pi]
        else:
            masked[side][li][pi] = value
            new_value = value
            # pbar.update(1)

        # prepare solver input (deep copy to avoid accidental sharing)
        top_mask = [list(cl) for cl in masked[0]]
        left_mask = [list(cl) for cl in masked[1]]
        
        # print(f"Re-solving after revealing clue {step}: side={side} line_index={li} pos_index={pi} value={new_value}, time: ", time.time())
        S = solve_nonogram_simple([top_mask, left_mask], grid=solution,
                                  new_clues=[(side, li)])
        # print(f"Solved after revealing clue {step}, time: ", time.time())
        # print(solution)
        # print(S)
        # print("-")
        
        if not S:
            # print("Error: puzzle became unsolvable after revealing clue", (side, li, pi, value))
            raise Exception("Nonogram: Puzzle became unsolvable")
        solution, marked = S
        
        steps.append({
            "step": step,
            "changed": (side, li, pi, masked[side][li][pi]),
            "marked": marked,
        })
        step += 1
        positions = collect_positions(masked)
        
    # print(f"Build-up completed: {marked} cells marked, time: ", time.time())
        
    return steps, solution

def showSolution(solution):
    print()
    for row in solution:
        for cell in row:
            print(f"[{cell[0]:2} {cell[1]:3} {cell[2]:1}]", end="")
        print()
    print()

def build_puzzle(options, random):
    # print("Start, time: ", time.time())
    x = options.width_of_grid.value
    y = options.height_of_grid.value
    list_of_symbols = set(options.clue_types.value)

    if 'O' in list_of_symbols:
        list_of_symbols.remove('O')
        list_of_symbols.add('Ω')
        
    if 'all' in list_of_symbols:
        list_of_symbols.discard('all')
        for sym in ['O', 'E', '/', '-', '+']:
            list_of_symbols.add(sym)
            if sym == 'O':
                list_of_symbols.add('Ω')
        
    if 'random' in list_of_symbols:
        list_of_symbols.discard('random')
        for sym in ['O', 'E', '/', '-', '+']:
            if random.choice([True, False]):
                list_of_symbols.add(sym)
    
    rando_clues, G = generate_random_clues(x, y, x*y/4, random)
    if not rando_clues:
        return False
    
    # print("Random clues generated, time: ", time.time())

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

    # print("Build-up completed, time: ", time.time())

    steps, final_solution = build_up
    
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
        "S": final_solution,
    }
    
    # print(output)
    # showSolution(output["S"])
    
    # print("Puzzle built, time: ", time.time())
    return output
