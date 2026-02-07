import os
from puzzle_generator.build_puzzle import build_puzzle
import random
from types import SimpleNamespace
import json
from tqdm import tqdm
import multiprocessing


list_value = [[], ['E', 'Ω'], ['/'], ['+', '-'], ['E', 'Ω', '/', '+', '-']]

sizes = [5,8,10,15,20]

number_of_cores = max(1, multiprocessing.cpu_count() - 3)

folder = "solo_puzzles"
if not os.path.exists(folder):
    os.makedirs(folder)

def _generate_task(args):
    width, height, c, clues, am = args
    options = SimpleNamespace(
        width_of_grid=SimpleNamespace(value=width),
        height_of_grid=SimpleNamespace(value=height),
        clue_types=SimpleNamespace(value=clues)
    )
    for i in range(1,am+1):
        filename = f"P_{width}_{height}_{c}_{i+1}.txt"
        with open(f"{folder}/{filename}", "w", encoding="utf-8") as f:
                puzzle = build_puzzle(options, random)
                puzzle_string = json.dumps(puzzle, separators=(',',':'))
                f.write(puzzle_string + "\n")
    return filename

if __name__ == "__main__":
    
    tasks = [
        (width, height, c, clues, 3)
        for width in sizes
        for height in sizes
        for c, clues in enumerate(list_value)
    ]
    
    with open(f"{folder}/ps.txt", "w", encoding="utf-8") as log_file:
        for (w,h,c,C,am) in tasks:
            log_file.write(f"{w} {h} {c} {am}\n")

    with multiprocessing.Pool(processes=number_of_cores) as pool, tqdm(total=len(tasks), desc="Generating Nonograhmm puzzles") as pbar:
        for _ in pool.imap_unordered(_generate_task, tasks):
            pbar.update()
