def get_sure_squares(clues, grid_line):
    n = len(clues)
    m = len(grid_line)

    possible_lengths = []
    for c in clues:
        if c == '?':
            possible_lengths.append(list(range(1, m + 1)))
        elif c == 'Ω':
            possible_lengths.append(list(range(1, m + 1, 2)))
        elif c == 'E':
            possible_lengths.append(list(range(2, m + 1, 2)))
        elif '/' in str(c):
            parts = str(c).split('/')
            possible_lengths.append([int(parts[0]), int(parts[1])])
        elif '-' in str(c):
            parts = str(c).split('-')
            max_c = int(parts[0])
            possible_lengths.append(list(range(1, min(max_c + 1, m + 1))))
        elif '+' in str(c):
            parts = str(c).split('+')
            min_c = int(parts[0])
            possible_lengths.append(list(range(min_c, m + 1)))
        else:
            possible_lengths.append([int(c)])

    black_ok_prefix = [0] * (m + 1)
    for j in range(m):
        black_ok_prefix[j + 1] = black_ok_prefix[j] + (1 if grid_line[j] >= 0 else 0)

    def can_place_black(a, b):
        return black_ok_prefix[b] - black_ok_prefix[a] == b - a

    # Forward check: F[i][j] = True if blocks 0..i-1 can be validly placed
    # such that position j is available (all cells before j are accounted for as
    # either part of a block or a valid white gap).
    F = [[False] * (m + 1) for _ in range(n + 1)]
    F[0][0] = True

    for j in range(m + 1):
        for i in range(n + 1):
            if not F[i][j]:
                continue
            if j < m and grid_line[j] <= 0:
                F[i][j + 1] = True
            if i < n:
                for L in possible_lengths[i]:
                    end = j + L
                    if end > m:
                        break
                    if not can_place_black(j, end):
                        continue
                    if end == m:
                        F[i + 1][end] = True
                    elif grid_line[end] <= 0:
                        F[i + 1][end + 1] = True

    if not F[n][m]:
        return False

    # Backward check: B[i][j] = True if blocks i..n-1 can be validly placed in [j, m).
    B = [[False] * (m + 1) for _ in range(n + 1)]
    B[n][m] = True

    for j in range(m - 1, -1, -1):
        for i in range(n, -1, -1):
            if grid_line[j] <= 0 and B[i][j + 1]:
                B[i][j] = True
            if i < n:
                for L in possible_lengths[i]:
                    end = j + L
                    if end > m:
                        break
                    if not can_place_black(j, end):
                        continue
                    if end == m:
                        if B[i + 1][end]:
                            B[i][j] = True
                            break
                    elif grid_line[end] <= 0 and B[i + 1][end + 1]:
                        B[i][j] = True
                        break

    can_be_white = [False] * m
    can_be_black = [False] * m

    for p in range(m):
        if grid_line[p] <= 0:
            for i in range(n + 1):
                if F[i][p] and B[i][p + 1]:
                    can_be_white[p] = True
                    break

    for i in range(n):
        for s in range(m):
            if not F[i][s]:
                continue
            for L in possible_lengths[i]:
                end = s + L
                if end > m:
                    break
                if not can_place_black(s, end):
                    continue
                ok = False
                if end == m:
                    ok = B[i + 1][end]
                elif grid_line[end] <= 0:
                    ok = B[i + 1][end + 1]
                if ok:
                    for p in range(s, end):
                        can_be_black[p] = True
                    if end < m:
                        can_be_white[end] = True

    answer = []
    for p in range(m):
        if grid_line[p] != 0:
            answer.append(grid_line[p])
        elif can_be_black[p] and not can_be_white[p]:
            answer.append(1)
        elif can_be_white[p] and not can_be_black[p]:
            answer.append(-1)
        else:
            answer.append(0)

    return answer


if __name__ == "__main__":
    q = [0, -2, 11, 0, 1]
    print(q)
    print(get_sure_squares([1, 1], q))
