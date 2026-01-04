
from pprint import pp

def sign(num):
    if num > 0:
        return 1
    elif num < 0:
        return -1
    else:
        return 0

def is_valid(clues_so_far, grid_line, only_conflict):
    sol = [-1] * len(grid_line)
    for [p, s] in clues_so_far:
        for i in range(p, p + s):
            sol[i] = 1
    # print(grid_line)
    # print(sol)
    if not only_conflict:
        return all([s == sign(g) or g == 0 for s, g in zip(sol, grid_line)])
    if not clues_so_far:
        return True
    check_until = clues_so_far[-1][0] + clues_so_far[-1][1]
    return all([s == sign(g) or g == 0 for s, g in zip(sol[0:check_until], grid_line[0:check_until])])
            
def find_any_solution(clues, grid_line):
    # print("find_any_solution called with:", clues, grid_line)
    n = len(clues)
    m = len(grid_line)
    
    # minimal length for each clue ( '?' -> 1, otherwise numeric )
    min_lengths = []
    max_lengths = []
    possible_lengths = []
    for c in clues:
        if c == '?':
            min_lengths.append(1)
            max_lengths.append(m)  # theoretically unbounded
            possible_lengths.append(list(range(1, m + 1)))
        elif c == 'Ω':
            min_lengths.append(1)
            max_lengths.append(m)
            possible_lengths.append(list(range(1, m + 1, 2)))
        elif c == 'E':
            min_lengths.append(2)
            max_lengths.append(m)
            possible_lengths.append(list(range(2, m + 1, 2)))
        else:
            min_lengths.append(int(c))
            max_lengths.append(int(c))
            possible_lengths.append([int(c)])
    curr = []
    done = []

    def backtrack(idx, pos_min):
        if done:
            return curr
        if idx == n:
            if is_valid(curr, grid_line, False):
                done.append(True)
                return curr
            return
        else:
            if not is_valid(curr, grid_line, True):
                return

        # minimal total length required from idx..end (including 1-space between blocks)
        remaining_blocks = n - idx
        min_total_from_idx = sum(min_lengths[idx:]) + max(0, remaining_blocks - 1)
        max_start = len(grid_line) - min_total_from_idx

        for s in range(pos_min, max_start + 1):
            if clues[idx] not in ['?', 'Ω', 'E']:
                length = int(clues[idx])
                curr.append([s, length])
                backtrack(idx + 1, s + length + 1)
                if done:
                    return curr
                curr.pop()
            else:
                # compute minimal total AFTER current block
                if idx == n - 1:
                    min_after = 0
                else:
                    min_after = sum(min_lengths[idx + 1:]) + max(0, (n - idx - 1) - 1)
                max_len = len(grid_line) - s - min_after
                for length in possible_lengths[idx]:
                    if length > max_len:
                        break
                    curr.append([s, length])
                    backtrack(idx + 1, s + length + 1)
                    if done:
                        return curr
                    curr.pop()
                    
    def write_out_configuration(config, m):
        line = [-1] * m
        for start, length in config:
            for i in range(start, start + length):
                line[i] = 1
        return line

    sol = backtrack(0, 0)
    if not done:
        return False
    # print("Solution found:", sol)
    return write_out_configuration(sol, m)


def update_lists(possible_black, possible_white, sol):
    for i in range(len(sol)):
        if sol[i] == 1:
            possible_black[i] = True
        elif sol[i] == -1:
            possible_white[i] = True
    
def get_sure_squares(clues, grid_line):
    first_solution = find_any_solution(clues, grid_line)
    if not first_solution:
        print("No solution found for line:", clues, grid_line)
        return False
    
    # print("First solution found:", first_solution)
    
    possible_black = [i == 1 for i in first_solution]
    possible_white = [i == -1 for i in first_solution]
    
    for i in range(len(grid_line)):
        if grid_line[i] == 1:
            possible_black[i] = True
            possible_white[i] = False
            continue
        if grid_line[i] == -1:
            possible_black[i] = False
            possible_white[i] = True
            continue
        # print(possible_black, possible_white)
        
        if grid_line[i] == 0:
            for opt in [1,-1]:
                test_line = grid_line.copy()
                test_line[i] = opt
                test_solution = find_any_solution(clues, test_line)
                if test_solution:
                    update_lists(possible_black, possible_white, test_solution)
    # print(possible_black)
    # print(possible_white)
    answer = []
    for i in range(len(grid_line)):
        if grid_line[i] != 0:
            answer.append(grid_line[i])
            continue
        
        if possible_black[i] and not possible_white[i]:
            answer.append(1)
        elif possible_white[i] and not possible_black[i]:
            answer.append(-1)
        else:
            answer.append(0)
    # pp(clues)
    # pp(grid_line)
    # pp(answer)
    # print()
    return answer

if __name__ == "__main__":
    q = [0,-2,11,0,1]
    print(q)
    print(get_sure_squares([1,1], q))