import random
try:
    import string
except ImportError:
    string = str

    # This is because a contributer wanted it to work in python 2 or something


def gen_maze():
    """
    This function returns a maze, with empty spaces being lists for tracking the contents of a space, and walls being
    integers 1 to 3.

    the empty space looks like this:
    [[# of team1 units, bool any holding flag], [# team2 units, bool any holding flag], bool unheld flag in space]

    a list with the artifacts coordinates is returned alongside for tracking, for scoring and stuff
    """
    EMPTY_SPACE = [[0, False], [0, False], False]

    length, height = 21, 25
    maze = []
    for j in range(height):
        row = []
        for i in range(length):
            cell = i % 2 if (j + 1) % 2 else (2 + i % 2)
            if cell == 0: cell = [[0, False], [0, False], False]
            row.append(cell)
        maze.append(row)

    # generate the initial walls and empty cells

    cell_sets = [i for i in range(length * height)]
    # generate the dictionary of sets

    order = list(range(height * length))
    random.shuffle(order)
    # Generate the random order for the walls
    # Run main part of algorithm
    for location in order:
        if maze[location // length][location % length] in (1, 2):      # if it is a wall dividing cells

            direction = length if maze[location // length][location % length] == 2 else 1
            # set the variable direction depending on whether it checks the cells to the side or above

            if cell_sets[location - direction] != cell_sets[location + direction] or random.randint(0, 5) == 5:
                # Check if the wall divides two distinct sets of cells, or if a random integer 0-5 is 5 (1/6 chance)

                maze[location // length][location % length] = [[0, False], [0, False], False]           # Remove the wall
                old_set = cell_sets[location - direction]                 # the set to be joined to the other set
                cell_sets[location] = cell_sets[location + direction]     # Set this cell to the other set
                for cell in filter(lambda x: x == old_set, cell_sets):    # Go through all the cells in the old set
                    cell_sets[cell] = cell_sets[location + direction]     # put them in the new set

        if all(cell_sets[i] == cell_sets[0] or maze[i // length + 1][i % length] != EMPTY_SPACE for i in cell_sets):
            # This will check whether all cells are connected, or are walls.
            break # If they are, we can exit loop early

    # In here, we will join up any loose middle columns,  the ones represented by 3 that initially side no space cells, by making another wall.
    # We know this won't seperate the maze into separate parts, because if it has 4 sides free, that means a bot can
    # walk around the three openings next to the column to get to the opposite side of wall.
    for location in order:
        #check if the cell is a 3, then check if all the cells siding it are space
        if maze[location // length][location % length] == 3 and all(cell == EMPTY_SPACE for cell in
              (maze[location // length + 1][location % length],
               maze[location // length - 1][location % length],
               maze[location // length][location % length + 1],
               maze[location // length][location % length - 1])):


            # generate random number switch, to determine which way the new wall should go.
            switch = random.randint(0, 3)
            if switch == 0:
                maze[location // length - 1][location % length] = 1   # set the wall above the cell to a 1 wall
            elif switch == 1:
                maze[location // length][location % length + 1] = 2   # set cell to the right a 2
            elif switch == 2:
                maze[location // length + 1][location % length] = 1   # beneath, a 1
            else:
                maze[location // length][location % length - 1] = 2   # the left, a 2

            # TBH, we don't really need the specific walls, but if we do decide to pretty it up into ascii art for the bots,
            # or we integrate a visual mode, this will make life easier if we want the fancy - | + arts:
            # +-+-+-+
            # |     |
            # +-+ +-+-+
            #   |     |
            #   +-+-+-+
    available_spaces = [] # we will be checking the available places the flag will be able to placed on the map, in the middle row
    middle = height // 2
    for possible_space in range(length):
        if maze[middle][possible_space] == EMPTY_SPACE:
            available_spaces.append(possible_space)
    location_x = random.choice(available_spaces)

    maze[middle][location_x][2] = True
    # Return, with surrounding walls, and the coordinates for the artifact
    return (
            [[3,2] * (length//2 + 1) + [3]]
           + [([3 if 3 in line else 1] + line + [3 if 3 in line else 1]) for line in maze]
           + [[3,2] * (length//2 + 1) + [3]]
           ), [location_x, middle]
# print("\n".join(''.join("+" if i in (1,2,3) else " " for i in line) for line in gen_maze()[0]))