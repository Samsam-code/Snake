def dive_cycle_even(n,dive_lengths):
    # There should be m//2 -1 dives
    path = []

    # Dives from left side
    nx = n
    for l in dive_lengths:
        path.extend(range(nx, nx+l+1))
        nx+=n
        path.extend(range(nx+l, nx-1, -1))
        nx+=n

    # Go to right side along the bottom edge
    path.extend(range(nx, nx+n))

    # Complementary dives from right side
    for l in reversed(dive_lengths):
        nx-=n
        path.extend(range(nx+n-1, nx+l, -1))
        nx-=n
        path.extend(range(nx+l+1, nx+n))

    # Go to left side along the top edge
    path.extend(range(n-1, -1, -1))

    return path

def double_comb_cycle(m, n):
    return dive_cycle_even(n, [n//2-1]*(m//2-1))

def zip_cycle(m, n):
    l = m//2 -1
    dive_lengths = [n-2, 0]*(l//2)
    if l%2 == 1:
        dive_lengths.append(n-2)
    return dive_cycle_even(n, dive_lengths)