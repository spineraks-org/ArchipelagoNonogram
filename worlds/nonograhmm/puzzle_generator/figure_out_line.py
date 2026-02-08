def is_valid(clues_so_far, grid_line, only_conflict):
    if only_conflict:
        if not clues_so_far:
            return True
        last_p, last_s = clues_so_far[-1]
        if last_p + last_s > len(grid_line):
            return False
        # Check last block cells are fill-compatible
        for i in range(last_p, last_p + last_s):
            if grid_line[i] < 0:
                return False
        # Check gap before last block
        gap_start = (clues_so_far[-2][0] + clues_so_far[-2][1]) if len(clues_so_far) >= 2 else 0
        for i in range(gap_start, last_p):
            if grid_line[i] > 0:
                return False
        return True

    sol = [-1] * len(grid_line)
    for [p, s] in clues_so_far:
        for i in range(p, p + s):
            if i >= len(sol):
                return False
            sol[i] = 1
    return all(
        (g == 0 or (s > 0 and g > 0) or (s < 0 and g < 0))
        for s, g in zip(sol, grid_line)
    )

            
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
        elif '/' in str(c):
            parts = str(c).split('/')
            min_c = int(parts[0])
            max_c = int(parts[1])
            min_lengths.append(min_c)
            max_lengths.append(max_c)
            possible_lengths.append([min_c, max_c])
        elif '-' in str(c):
            parts = str(c).split('-')
            max_c = int(parts[0])
            possible_lengths.append(list(range(1, min(max_c + 1, m + 1))))
            min_lengths.append(1)
        elif '+' in str(c):
            parts = str(c).split('+')
            min_c = int(parts[0])
            possible_lengths.append(list(range(min_c, m + 1)))
            min_lengths.append(min_c)
        else:
            min_lengths.append(int(c))
            max_lengths.append(int(c))
            possible_lengths.append([int(c)])
    curr = []
    done = []

    # min_space_from[i] = minimum cells needed for blocks i..n-1 including gaps
    min_space_from = [0] * (n + 1)
    for i in range(n - 1, -1, -1):
        min_space_from[i] = min_lengths[i] + min_space_from[i + 1]
        if i < n - 1:
            min_space_from[i] += 1

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
        max_start = m - min_space_from[idx]

        for s in range(pos_min, max_start + 1):
            if clues[idx] not in ['?', 'Ω', 'E'] and '/' not in str(clues[idx]) and '-' not in str(clues[idx]) and '+' not in str(clues[idx]):
                length = int(clues[idx])
                curr.append([s, length])
                backtrack(idx + 1, s + length + 1)
                if done:
                    return curr
                curr.pop()
            else:
                # compute minimal total AFTER current block
                max_len = m - s - min_space_from[idx + 1]
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
            if possible_black[i] and possible_white[i]:
                continue
            for opt in [1,-1]:
                if opt == 1 and possible_black[i]:
                    continue
                if opt == -1 and possible_white[i]:
                    continue
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
