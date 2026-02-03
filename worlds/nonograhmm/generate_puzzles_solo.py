from puzzle_generator.build_puzzle import build_puzzle
import random
from types import SimpleNamespace
import json
from tqdm import tqdm
import multiprocessing


list_value = [[], ['E', 'Ω'], ['/'], ['+', '-'], ['E', 'Ω', '/', '+', '-']]

# sizes = [5, 8, 10, 15]
sizes = [20]

number_of_cores = multiprocessing.cpu_count()

def _generate_task(args):
    width, height, c, clues = args
    options = SimpleNamespace(
        width_of_grid=SimpleNamespace(value=width),
        height_of_grid=SimpleNamespace(value=height),
        clue_types=SimpleNamespace(value=clues)
    )
    num = 1 # 00 / (width/5 * height/5)
    filename = f"P_{width}_{height}_{c}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        for i in range(int(num)):
            puzzle = build_puzzle(options, random)
            puzzle_string = json.dumps(puzzle, separators=(',',':'))
            f.write(puzzle_string + "\n")
    return filename

if __name__ == "__main__":
    tasks = [
        (width, height, c, clues)
        for width in sizes
        for height in sizes
        for c, clues in enumerate(list_value)
    ]

    with multiprocessing.Pool(processes=number_of_cores) as pool, tqdm(total=len(tasks), desc="Generating Nonograhmm puzzles") as pbar:
        for _ in pool.imap_unordered(_generate_task, tasks):
            pbar.update()