import API
import sys

# =====================================================================
# FLOODFILL ALGORITHM FOR MMS SIMULATOR
# =====================================================================
# HOW FLOODFILL WORKS:
#
# The CENTER cells get value 0.
# Every cell gets a number = its distance to the center.
# The mouse always moves to the neighbor with the LOWEST number.
# When it hits a wall it didn't know about, it RECALCULATES the numbers.
# This guarantees the mouse always finds the shortest known path.
# =====================================================================

# --- MAZE CONFIGURATION ---
MAZE_SIZE = API.mazeWidth()  # Auto-detects maze size

# --- FLOOD VALUES GRID ---
# This 2D list stores the "flood value" of every cell.
# Higher value = farther from center. We start everything at a high number.
flood = [[0] * MAZE_SIZE for _ in range(MAZE_SIZE)]

# --- WALL KNOWLEDGE GRID ---
# We store which walls the mouse has DISCOVERED so far.
# Format: walls[x][y] = {'N': bool, 'S': bool, 'E': bool, 'W': bool}
# True means there IS a wall on that side.
walls = [[{'N': False, 'S': False, 'E': False, 'W': False}
          for _ in range(MAZE_SIZE)]
         for _ in range(MAZE_SIZE)]

# --- DIRECTION HELPERS ---
# The mouse has a "facing" direction. We track it so we know which way is "front", "left", "right" relative to the maze.
DIRECTIONS = ['N', 'E', 'S', 'W']  

visited = [[0] * MAZE_SIZE for _ in range(MAZE_SIZE)]
INF = MAZE_SIZE * MAZE_SIZE

def log(string):
    """Print to stderr so the simulator shows it in logs."""
    print(string, file=sys.stderr, flush=True)

# =====================================================================
# STEP 1: INITIALIZE FLOOD VALUES
# Set every cell's flood value = Manhattan distance to the center.
# For a 16x16 maze, the center is cells (7,7), (7,8), (8,7), (8,8).
# =====================================================================
def initialize_flood():
    """Fill the flood grid with initial distance-to-center values."""
    # Center cells for 16x16 maze
    if MAZE_SIZE == 16:
        centers = [(7, 7), (7, 8), (8, 7), (8, 8)]
    else:  # 8x8 maze
        centers = [(3, 3), (3, 4), (4, 3), (4, 4)]

    for x in range(MAZE_SIZE):
        for y in range(MAZE_SIZE):
            # Distance = minimum Manhattan distance to any center cell
            flood[x][y] = min(abs(x - cx) + abs(y - cy)
                              for cx, cy in centers)

# =====================================================================
# STEP 2: GET VALID NEIGHBORS
# For a given cell, return neighbors that are NOT blocked by a wall.
# =====================================================================
def get_accessible_neighbors(x, y):
    """Return list of (nx, ny) cells reachable from (x, y) with no wall."""
    neighbors = []

    if not walls[x][y]['N'] and y + 1 < MAZE_SIZE:
        neighbors.append((x, y + 1))
    if not walls[x][y]['S'] and y - 1 >= 0:
        neighbors.append((x, y - 1))
    if not walls[x][y]['E'] and x + 1 < MAZE_SIZE:
        neighbors.append((x + 1, y))
    if not walls[x][y]['W'] and x - 1 >= 0:
        neighbors.append((x - 1, y))

    return neighbors

# =====================================================================
# STEP 3: RECALCULATE FLOOD VALUES 
# After discovering a new wall, recalculate all flood values.
# This uses BFS starting from the center outward.
# =====================================================================
def recalculate_flood():
    """Recalculate all flood values using BFS from center cells."""
    # Reset all values to a large number first
    for x in range(MAZE_SIZE):
        for y in range(MAZE_SIZE):
            flood[x][y] = MAZE_SIZE * MAZE_SIZE  # infinity

    # Start BFS from center cells (value = 0)
    if MAZE_SIZE == 16:
        centers = [(7, 7), (7, 8), (8, 7), (8, 8)]
    else:
        centers = [(3, 3), (3, 4), (4, 3), (4, 4)]

    queue = []
    for cx, cy in centers:
        flood[cx][cy] = 0
        queue.append((cx, cy))

    # BFS: spread values outward through accessible neighbors
    i = 0
    while i < len(queue):
        x, y = queue[i]
        i += 1

        for nx, ny in get_accessible_neighbors(x, y):
            # If this neighbor hasn't been reached yet, set its value
            if flood[nx][ny] == MAZE_SIZE * MAZE_SIZE:
                flood[nx][ny] = flood[x][y] + 1
                queue.append((nx, ny))

# =====================================================================
# STEP 4: UPDATE WALLS FROM SENSOR READINGS
# Ask the simulator what walls the mouse currently sees, then store that info in our walls grid.
# =====================================================================
def update_walls(x, y, facing):
    """Read sensors and record any walls found around current cell."""
    # Check front, left, right sensors
    wall_front = API.wallFront()
    wall_left  = API.wallLeft()
    wall_right = API.wallRight()

    # Convert relative sensor directions to absolute maze directions based on which way the mouse is currently facing
    front_dir = facing
    left_dir  = DIRECTIONS[(DIRECTIONS.index(facing) - 1) % 4]
    right_dir = DIRECTIONS[(DIRECTIONS.index(facing) + 1) % 4]

    # Record walls in our knowledge grid
    if wall_front:
        walls[x][y][front_dir] = True
        # Also mark the NEIGHBOR's opposite wall (they share the same wall)
        nx, ny = neighbor_in_direction(x, y, front_dir)
        if nx is not None:
            walls[nx][ny][opposite(front_dir)] = True

    if wall_left:
        walls[x][y][left_dir] = True
        nx, ny = neighbor_in_direction(x, y, left_dir)
        if nx is not None:
            walls[nx][ny][opposite(left_dir)] = True

    if wall_right:
        walls[x][y][right_dir] = True
        nx, ny = neighbor_in_direction(x, y, right_dir)
        if nx is not None:
            walls[nx][ny][opposite(right_dir)] = True

def neighbor_in_direction(x, y, direction):
    """Return the (x, y) of the neighbor in a given direction, or (None, None)."""
    if direction == 'N' and y + 1 < MAZE_SIZE: return (x, y + 1)
    if direction == 'S' and y - 1 >= 0:        return (x, y - 1)
    if direction == 'E' and x + 1 < MAZE_SIZE: return (x + 1, y)
    if direction == 'W' and x - 1 >= 0:        return (x - 1, y)
    return (None, None)

def opposite(direction):
    """Return the opposite direction."""
    return {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}[direction]

# =====================================================================
# STEP 5: CHOOSE BEST MOVE
# Look at all accessible neighbors and move to the one with the LOWEST flood value, that's the best path toward center.
# =====================================================================
def get_best_neighbor(x, y):
    neighbors = get_accessible_neighbors(x, y)

    if not neighbors:
        return None, None

    # Prefer neighbors that are reachable by floodfill
    reachable = [pos for pos in neighbors if flood[pos[0]][pos[1]] < INF]

    if reachable:
        return min(reachable, key=lambda pos: (flood[pos[0]][pos[1]], visited[pos[0]][pos[1]]))

    # If all neighbors are INF, explore the least visited one
    return min(neighbors, key=lambda pos: (visited[pos[0]][pos[1]], flood[pos[0]][pos[1]]))

# =====================================================================
# STEP 6: MOVEMENT HELPERS
# Turn and move the mouse to reach a target cell.
# =====================================================================
def turn_to_face(current_facing, target_direction):
    """Turn the mouse until it faces target_direction. Returns new facing."""
    facing = current_facing
    # Keep turning right until we face the right way
    # Maximum 3 turns needed (never need to turn more than 3 times right)
    for _ in range(4):
        if facing == target_direction:
            break
        API.turnRight()
        facing = DIRECTIONS[(DIRECTIONS.index(facing) + 1) % 4]
    return facing

def move_to(x, y, facing, nx, ny):
    """
    Move from (x,y) to neighbor (nx,ny).
    Figures out which direction that neighbor is, turns to face it, moves.
    Returns new (x, y, facing).
    """
    # Figure out which direction the neighbor is
    if nx == x and ny == y + 1:   target_dir = 'N'
    elif nx == x and ny == y - 1: target_dir = 'S'
    elif nx == x + 1 and ny == y: target_dir = 'E'
    else:                          target_dir = 'W'

    # Turn to face that direction
    facing = turn_to_face(facing, target_dir)

    # Move forward one cell
    API.moveForward()

    return nx, ny, facing

# =====================================================================
# STEP 7: COLOR THE MAZE (Visual feedback in simulator)
# =====================================================================
def color_cell(x, y, color):
    """Color a cell in the simulator for visual debugging."""
    API.setColor(x, y, color)

def update_display():
    """Color cells based on flood values so you can see the gradient."""
    for x in range(MAZE_SIZE):
        for y in range(MAZE_SIZE):
            if visited[x][y] > 0:
                continue  # Don't overwrite visited cells
            v = flood[x][y]
            if v == 0:
                API.setColor(x, y, 'G')    # Green = center
            elif v <= 5:
                API.setColor(x, y, 'Y')    # Yellow = close
            elif v <= 10:
                API.setColor(x, y, 'O')    # Orange = medium
            # Others stay default (dark)

# =====================================================================
# MAIN FUNCTION — The mouse's brain loop
# =====================================================================
def main():
    log("=== Floodfill Algorithm Starting ===")

    # Initialize flood values before moving
    initialize_flood()
    update_display()

    # Mouse always starts at bottom-left corner (0, 0) facing North
    x, y = 0, 0
    facing = 'N'

    # Define center cells
    if MAZE_SIZE == 16:
        center_cells = {(7, 7), (7, 8), (8, 7), (8, 8)}
    else:
        center_cells = {(3, 3), (3, 4), (4, 3), (4, 4)}

    # Color the starting cell
    API.setColor(x, y, 'B')  # Blue = start

    # -------------------------------------------------------
    # MAIN NAVIGATION LOOP
    # Keeps running until the mouse reaches the center
    # -------------------------------------------------------
    while (x, y) not in center_cells:

        visited[x][y] += 1

        # 1. Read sensors and update our wall knowledge
        update_walls(x, y, facing)

        # 2. Recalculate flood values with new wall information
        recalculate_flood()
        update_display()

        # 3. Find the best neighbor to move to
        nx, ny = get_best_neighbor(x, y)

        if nx is None:
            # This should never happen in a valid maze
            log(f"ERROR: No accessible neighbors at ({x},{y})! Stopping.")
            break

        log(f"At ({x},{y}) facing {facing}, flood={flood[x][y]} → moving to ({nx},{ny})")

        # 4. Move to the best neighbor
        x, y, facing = move_to(x, y, facing, nx, ny)

        # 5. Mark visited cell
        API.setColor(x, y, 'C')  # Cyan = visited path

    # -------------------------------------------------------
    # REACHED THE CENTER!
    # -------------------------------------------------------
    # At the very start of main(), after x,y = 0,0:
    visited[x][y] += 1  # count starting cell

    # The center cell is already counted since the loop visits it last
    # so just add +1 for start:
    unique_cells = sum(1 for x in range(MAZE_SIZE) for y in range(MAZE_SIZE) if visited[x][y] > 0)
    log(f"=== CENTER REACHED at ({x},{y})! ===")
    log(f"=== Unique cells visited: {unique_cells} ===")
    API.setColor(x, y, 'G')


main()
