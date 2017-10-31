assignments = []

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    # Find all instances of naked twins
    for unit in unitlist:
        # find boxes with value length 2
        len_2_boxes = [box for box in unit if len(values[box])==2]
        # if there are less than two boxes with length 2 go to next unit
        if len(len_2_boxes) < 2:
            continue
        # find length 2 boxes with identical value -> twins
        len_2_box_vals = [values[box] for box in len_2_boxes]
        twins = [box for box in len_2_boxes if len_2_box_vals.count(values[box])>1]
        # if there are no twins go to next unit
        if len(twins) < 2:
            continue
        # find possible digits in twins
        twin_digits = list(values[twins[0]])
        # for every box in the same unit delete the twin digits
        neighbors = list(set(unit)-set(twins))
        for box in neighbors:
            values = assign_value(values, box, values[box].replace(twin_digits[0], ""))
            values = assign_value(values, box, values[box].replace(twin_digits[1], ""))
    return values



    # Eliminate the naked twins as possibilities for their peers

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [s + t for s in A for t in B]

rows = 'ABCDEFGHI'
cols = '123456789'

boxes = cross(rows, cols)

# Define units of different shapes
# row and column units first
row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
# square units
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
# diagonal units needed for diagonal sudokus
diag1 = [a+b for a, b in zip(rows,cols)]
diag2 = [a+b for a, b in zip(rows[::-1],cols)]
diag_units = [diag1, diag2]
# consolidate units into unitlist and determine peers
unitlist = row_units + column_units + square_units + diag_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    assert len(grid) == 81
    all_digits = "123456789"
    gridvals = {b: (v if v != "." else all_digits) for (b, v) in zip(boxes, grid)}
    return gridvals

def display(values):
    """
    Display the values as a 2-D grid.
    Input: The sudoku in dictionary form
    Output: None
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return

def eliminate(values):
    """
    Go through all the boxes, and whenever there is a box with a value, eliminate this value from the values of all its peers.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    for b in values.keys():
        if len(values[b]) == 1:
            for peer in peers[b]:
                #values[peer] = values[peer].replace(values[b], "")
                values = assign_value(values, peer, values[peer].replace(values[b], ""))

    return values

def only_choice(values):
    """
    Go through all the units, and whenever there is a unit with a value that only fits in one box, assign the value to this box.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    all_digits = "123456789"
    for unit in unitlist:
        for d in all_digits:
            d_indicator = [box for box in unit if values[box].count(d) > 0]
            if len(d_indicator) == 1:
                #values[d_indicator[0]] = d
                values = assign_value(values, d_indicator[0], d)
    return values

def reduce_puzzle(values):
    """
    Iterate eliminate() and only_choice(). If at some point, there is a box with no available values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same, return the sudoku.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        # Use the Eliminate Strategy
        values = eliminate(values)
        # Use the Only Choice Strategy
        values = only_choice(values)
        # Use the naked twin
        values = naked_twins(values)
        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values


def search(values):
    "Using depth-first search and propagation, create a search tree and solve the sudoku."
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values is False:
        return False
    n_poss_values = {box: (len(values[box]) if len(values[box]) > 1 else 10) for box in boxes}
    min_poss_values = min(n_poss_values.values())
    if min_poss_values == 10:
        return values
    # Choose one of the unfilled squares with the fewest possibilities
    box_choices = [box for box in boxes if n_poss_values[box] == min_poss_values]
    trial_box = box_choices[0]
    # Now use recursion to solve each one of the resulting sudokus, and if one returns a value (not False), return that answer!
    for val in values[trial_box]:
        new_sudoku = values.copy()
        new_sudoku = assign_value(new_sudoku, trial_box, val)
        new_sudoku = search(new_sudoku)
        if new_sudoku:
            return new_sudoku

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    values = grid_values(grid)
    solution = search(values)
    return solution



if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
