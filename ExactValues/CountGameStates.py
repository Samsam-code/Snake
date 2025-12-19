"""
Functions to count the board states of an mxn grid.
"""
from GridSpecificTools.GridGraphAndSymmetries import (find_grid_adjacency, find_fixed_lists,
                                    find_preferred_lists, find_transformed_lists)


# TO DO: for any graph, count states from its adjacency list

def count_grid_board_states(m, n):

    A = m*n         # area
    counts = [0] * (A+1)

    TSMS   = 0      # total snakes, mod symmetries
    TSWAMS = 0      # total snakes with apples mod symmetries
    TS     = 0      # total snakes
    TSWA   = 0      # total snakes with apples

    # some O(A) memory to speed us up
    # slightly overkill but negligible
    adjacency         = find_grid_adjacency(m, n)
    # do not include the identity
    transformed_lists = find_transformed_lists(m, n)[1:]
    preferred_lists   = find_preferred_lists(transformed_lists)
    fixed_lists       = find_fixed_lists(transformed_lists)
    num_pref_cells    = [sum(pref_lst) for pref_lst in preferred_lists]

    SYMM      = 8 if m==n else 4
    HALF_SYMM = SYMM // 2


    # LENGTH ONE
    temp_stack = []
    apple_spaces = A-1
    for first_head in range(A):

        # only consider those preferred by every symmetry
        # ie. in NW quadrant of non-square rectangle, or NNW octant of square
        if not all(is_preferred[first_head] for is_preferred in preferred_lists):
            continue

        # the symmetries for which this is a fixed point
        symmetries = [i for i, is_fixed in enumerate(fixed_lists) if is_fixed[first_head]]

        if symmetries:
            # the symmetry factor is how many images it has under transformations
            images = [image[first_head] for image in transformed_lists]
            factor = len(set(images))

            # only count apples preferred by the child symmetries
            apples = 0
            for apple in range(A):
                if apple != first_head and all(preferred_lists[s][apple] for s in symmetries):
                    apples += 1
        else:
            factor = SYMM
            apples = apple_spaces

        TSMS   += 1
        TSWAMS += apples
        TS     += factor
        TSWA   += factor * apple_spaces
        temp_stack.append((first_head, symmetries))


    # LENGTH TWO
    stack = []
    while temp_stack:
        first_head, symmetries = temp_stack.pop()
        apple_spaces = A-2

        if symmetries:
            for new_head in adjacency[first_head]:
                
                # second head is allowed 
                # only if it is preferred by each symmetry of the first head
                if not all(preferred_lists[s][new_head] for s in symmetries):
                    continue
                
                # the symmetry of the snake is the one of the first head
                # for which the new head is also a fixed point
                child_symmetry = None
                for s in symmetries:
                    if fixed_lists[s][new_head]:
                        child_symmetry = s
                        break
                
                if child_symmetry is None:
                    factor = SYMM
                    apples = apple_spaces
                else:
                    factor = HALF_SYMM   
                    apples = num_pref_cells[child_symmetry] - 2
                    
                TSMS   += 1
                TSWAMS += apples
                TS     += factor
                TSWA   += factor * apple_spaces
                
                stack.append((first_head, new_head, child_symmetry))
        
        else:
            for new_head in adjacency[first_head]:
                TSMS   += 1
                TSWAMS += apple_spaces
                TS     += SYMM
                TSWA   += SYMM * apple_spaces
                stack.append((first_head, new_head, None))


    # MAIN LOOP 
    while stack:
        first_head, second_head, symmetry = stack.pop()

        # clear the board 
        occupied = [False] * A
        occupied[first_head] = True
        apple_spaces = A - 2      
        length = 2
        
        if symmetry is not None:
            # the snake lies along the vertical or horizontal fold line
            is_fixed     = fixed_lists[symmetry]
            is_preferred = preferred_lists[symmetry]
            pref_apples  = num_pref_cells[symmetry] - 2

            # we follow symmetry branch, breaking off to non-symmetry branches along the way
            symm_stack = [second_head]
            no_symm_stack = []
            while symm_stack:
                old_head = symm_stack.pop()
                occupied[old_head] = True
                length += 1
                apple_spaces -= 1
                pref_apples  -= 1
                for new_head in adjacency[old_head]:
                    # only consider states preferred by the symmetry
                    if occupied[new_head] or not is_preferred[new_head]:
                        continue
                    
                    if is_fixed[new_head]:
                        factor = HALF_SYMM   
                        apples = pref_apples
                        symm_stack.append(new_head)
                    else:
                        factor = SYMM
                        apples = apple_spaces
                        no_symm_stack.append(new_head)

                    TSMS   += 1
                    TSWAMS += apples
                    TS     += factor
                    TSWA   += factor * apple_spaces
                
                # non-symmetry branch
                while no_symm_stack:
                    old_head = no_symm_stack.pop()
                    if occupied[old_head]:
                        # seen before, marks end of branch
                        occupied[old_head] = False
                        apple_spaces += 1
                        length -= 1
                        continue
                    # add to stack to mark end of branch
                    no_symm_stack.append(old_head)
                    occupied[old_head] = True
                    apple_spaces -= 1
                    length += 1
                    for new_head in adjacency[old_head]:
                        if occupied[new_head]:
                            continue                
                        TSMS   += 1
                        TSWAMS += apple_spaces
                        TS     += SYMM
                        TSWA   += SYMM * apple_spaces
                        no_symm_stack.append(new_head)
                        counts[length] += 1

        else:
            # non-symmetry branch
            # THIS IS A VERY HOT LOOP, about 1 million a second
            no_symm_stack = [second_head]
            while no_symm_stack:
                old_head = no_symm_stack.pop()
                if occupied[old_head]:
                    # seen before, marks end of branch
                    occupied[old_head] = False
                    apple_spaces += 1
                    length -= 1
                    continue
                # add to stack to mark end of branch
                no_symm_stack.append(old_head)
                occupied[old_head] = True
                apple_spaces -= 1
                length += 1
                for new_head in adjacency[old_head]:
                    if occupied[new_head]:
                        continue
                    TSMS   += 1
                    TSWAMS += apple_spaces
                    TS     += SYMM
                    TSWA   += SYMM * apple_spaces
                    no_symm_stack.append(new_head)
                    counts[length] += 1

    print(counts)
    return TSMS, TSWAMS, TS, TSWA

# due to the exponential time complexity, 
# here is a version that only works modulo symmetry

def count_grid_board_states_mod_symmetry(m, n):
    A = m*n         # area
    counts = [0] * (A+1)

    TSMS   = 0      # total snakes, mod symmetries
    TSWAMS = 0      # total snakes with apples mod symmetries

    # some O(A) memory to speed us up
    # slightly overkill but negligible
    adjacency         = find_grid_adjacency(m, n)
    # do not include the identity
    transformed_lists = find_transformed_lists(m, n)[1:]
    preferred_lists   = find_preferred_lists(transformed_lists)
    fixed_lists       = find_fixed_lists(transformed_lists)
    num_pref_cells    = [sum(pref_lst) for pref_lst in preferred_lists]

    # LENGTH ONE
    temp_stack = []
    apple_spaces = A-1
    for first_head in range(A):

        # only consider those preferred by every symmetry
        # ie. in NW quadrant of non-square rectangle, or NNW octant of square
        if not all(is_preferred[first_head] for is_preferred in preferred_lists):
            continue

        # the symmetries for which this is a fixed point
        symmetries = [i for i, is_fixed in enumerate(fixed_lists) if is_fixed[first_head]]

        if symmetries:
            # only count apples preferred by the child symmetries
            apples = 0
            for apple in range(A):
                if apple != first_head and all(preferred_lists[s][apple] for s in symmetries):
                    apples += 1
        else:
            apples = apple_spaces

        TSMS   += 1
        TSWAMS += apples
        temp_stack.append((first_head, symmetries))


    # LENGTH TWO
    stack = []
    while temp_stack:
        first_head, symmetries = temp_stack.pop()
        apple_spaces = A-2

        if symmetries:
            for new_head in adjacency[first_head]:
                
                # second head is allowed 
                # only if it is preferred by each symmetry of the first head
                if not all(preferred_lists[s][new_head] for s in symmetries):
                    continue
                
                # the symmetry of the snake is the one of the first head
                # for which the new head is also a fixed point
                child_symmetry = None
                for s in symmetries:
                    if fixed_lists[s][new_head]:
                        child_symmetry = s
                        break
                
                if child_symmetry is None:
                    apples = apple_spaces
                else:
                    apples = num_pref_cells[child_symmetry] - 2
                    
                TSMS   += 1
                TSWAMS += apples
                stack.append((first_head, new_head, child_symmetry))
        
        else:
            for new_head in adjacency[first_head]:
                TSMS   += 1
                TSWAMS += apple_spaces
                stack.append((first_head, new_head, None))

    # MAIN LOOP 
    while stack:
        first_head, second_head, symmetry = stack.pop()

        # clear the board 
        occupied = [False] * A
        occupied[first_head] = True
        apple_spaces = A - 2      
        length = 2
        
        if symmetry is not None:
            # the snake lies along the vertical or horizontal fold line
            is_fixed     = fixed_lists[symmetry]
            is_preferred = preferred_lists[symmetry]
            pref_apples  = num_pref_cells[symmetry] - 2

            # we follow symmetry branch, breaking off to non-symmetry branches along the way
            symm_stack = [second_head]
            no_symm_stack = []
            while symm_stack:
                old_head = symm_stack.pop()
                occupied[old_head] = True
                length += 1
                apple_spaces -= 1
                pref_apples  -= 1
                for new_head in adjacency[old_head]:
                    # only consider states preferred by the symmetry
                    if occupied[new_head] or not is_preferred[new_head]:
                        continue
                    if is_fixed[new_head]: 
                        apples = pref_apples
                        symm_stack.append(new_head)
                    else:
                        apples = apple_spaces
                        no_symm_stack.append(new_head)
                    TSMS   += 1
                    TSWAMS += apples
                
                # non-symmetry branch
                while no_symm_stack:
                    old_head = no_symm_stack.pop()
                    if occupied[old_head]:
                        # seen before, marks end of branch
                        occupied[old_head] = False
                        apple_spaces += 1
                        length -= 1
                        continue
                    # add to stack to mark end of branch
                    no_symm_stack.append(old_head)
                    occupied[old_head] = True
                    apple_spaces -= 1
                    length += 1
                    for new_head in adjacency[old_head]:
                        if occupied[new_head]:
                            continue                
                        TSMS   += 1
                        TSWAMS += apple_spaces
                        no_symm_stack.append(new_head)
                        counts[length] += 1

        else:
            # non-symmetry branch
            # THIS IS A VERY HOT LOOP, about 1 million a second
            no_symm_stack = [second_head]
            while no_symm_stack:
                old_head = no_symm_stack.pop()
                if occupied[old_head]:
                    # seen before, marks end of branch
                    occupied[old_head] = False
                    apple_spaces += 1
                    length -= 1
                    continue
                # add to stack to mark end of branch
                no_symm_stack.append(old_head)
                occupied[old_head] = True
                apple_spaces -= 1
                length += 1
                for new_head in adjacency[old_head]:
                    if occupied[new_head]:
                        continue
                    TSMS   += 1
                    TSWAMS += apple_spaces
                    no_symm_stack.append(new_head)
                    counts[length] += 1

    print(counts)
    return TSMS, TSWAMS


if __name__ == "__main__":
    import time
    m = 5
    n = 5
    start = time.time()
    print(count_grid_board_states_mod_symmetry(m, n))
    print(time.time()-start)