def find_any_solution(clues, grid_line):
    n = len(clues)
    m = len(grid_line)

    # minimal length for each clue ( '?' -> 1, otherwise numeric )
    possible_lengths = []
    min_lengths = []
    for c in clues:
        if c == '?':
            min_lengths.append(1)
            possible_lengths.append(list(range(1, m + 1)))
        elif c == 'Ω':
            min_lengths.append(1)
            possible_lengths.append(list(range(1, m + 1, 2)))
        elif c == 'E':
            min_lengths.append(2)
            possible_lengths.append(list(range(2, m + 1, 2)))
        elif '/' in str(c):
            parts = str(c).split('/')
            min_c = int(parts[0])
            min_lengths.append(min_c)
            possible_lengths.append([min_c, int(parts[1])])
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
            val = int(c)
            min_lengths.append(val)
            possible_lengths.append([val])

    # min_space_from[i] = minimum cells needed for blocks i..n-1 including gaps
    min_space_from = [0] * (n + 1)
    for i in range(n - 1, -1, -1):
        min_space_from[i] = min_lengths[i] + min_space_from[i + 1]
        if i < n - 1:
            min_space_from[i] += 1

    curr = []
    found = False

    def backtrack(idx, min_start):
        nonlocal found
        if found:
            return

        # Check mandatory gap cell after previous block (only if within grid bounds)
        if 0 < min_start <= m and grid_line[min_start - 1] > 0:
            return

        if idx == n:
            for i in range(min_start, m):
                if grid_line[i] > 0:
                    return
            found = True
            return

        # minimal total length required from idx..end (including 1-space between blocks)
        max_start = m - min_space_from[idx]
        # minimal total length required AFTER current block
        max_end = m - min_space_from[idx + 1]
        lengths = possible_lengths[idx]

        for s in range(min_start, max_start + 1):
            # Incremental gap check: if a filled cell is in the gap, no later start works either
            if s > min_start and grid_line[s - 1] > 0:
                break

            for length in lengths:
                end = s + length
                if end > max_end:
                    break
                ok = True
                for i in range(s, end):
                    if grid_line[i] < 0:
                        ok = False
                        break
                if not ok:
                    continue
                curr.append((s, length))
                backtrack(idx + 1, end + 1)
                if found:
                    return
                curr.pop()

    backtrack(0, 0)

    if not found:
        return False

    sol = [-1] * m
    for start, length in curr:
        for i in range(start, start + length):
            sol[i] = 1
    return sol


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
