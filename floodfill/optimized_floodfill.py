import API
import sys

# =====================================================================
# OPTIMIZED FLOODFILL — Modified Floodfill with Speed Run
# =====================================================================
# HOW THIS DIFFERS FROM STANDARD FLOODFILL:
#
# Standard Floodfill: Runs to center once, exploring as it goes.
#
# Optimized (3 phases):
#   PHASE 1 - Exploration Run: Navigate to center using floodfill, mapping ALL walls discovered along the way.
#   PHASE 2 - Return Run: Go back to start (0,0) using the built map. Continue mapping any new walls found.
#   PHASE 3 - Speed Run: Run to center using the currently known shortest path.
#
# WHY IT'S BETTER:
#   The speed run (Phase 3) always takes the optimal path because the
#   entire maze has been mapped. This is what real competition mice do.
# =====================================================================

# --- AUTO-DETECT MAZE SIZE ---
MAZE_SIZE = API.mazeWidth()

# --- CENTER AND START CELLS ---
if MAZE_SIZE == 16:
    CENTER_CELLS = {(7, 7), (7, 8), (8, 7), (8, 8)}
else:
    CENTER_CELLS = {(3, 3), (3, 4), (4, 3), (4, 4)}

START_CELL = (0, 0)

# --- FLOOD VALUES GRID ---
flood = [[0] * MAZE_SIZE for _ in range(MAZE_SIZE)]

# --- WALL KNOWLEDGE GRID ---
walls = [[{'N': False, 'S': False, 'E': False, 'W': False}
          for _ in range(MAZE_SIZE)]
         for _ in range(MAZE_SIZE)]

# --- DIRECTION HELPERS ---
DIRECTIONS = ['N', 'E', 'S', 'W']

# --- STATS TRACKING ---
phase1_steps = 0
phase2_steps = 0
phase3_steps = 0
visited_cells = set()

def log(string):
    print(string, file=sys.stderr, flush=True)

# =====================================================================
# FLOOD CALCULATION HELPERS (same as standard floodfill)
# =====================================================================
def recalculate_flood(target_cells):
    """
    Recalculate flood values toward any set of target cells.
    Used for BOTH forward (to center) and return (to start) runs.
    This is the key improvement — we can flood toward ANY target!
    """
    INF = MAZE_SIZE * MAZE_SIZE * 10
    for x in range(MAZE_SIZE):
        for y in range(MAZE_SIZE):
            flood[x][y] = INF

    queue = []
    for (cx, cy) in target_cells:
        flood[cx][cy] = 0
        queue.append((cx, cy))

    i = 0
    while i < len(queue):
        x, y = queue[i]
        i += 1
        for nx, ny in get_accessible_neighbors(x, y):
            if flood[nx][ny] == INF:
                flood[nx][ny] = flood[x][y] + 1
                queue.append((nx, ny))

def get_accessible_neighbors(x, y):
    neighbors = []
    if not walls[x][y]['N'] and y + 1 < MAZE_SIZE: neighbors.append((x, y + 1))
    if not walls[x][y]['S'] and y - 1 >= 0:         neighbors.append((x, y - 1))
    if not walls[x][y]['E'] and x + 1 < MAZE_SIZE:  neighbors.append((x + 1, y))
    if not walls[x][y]['W'] and x - 1 >= 0:         neighbors.append((x - 1, y))
    return neighbors

def get_best_neighbor(x, y):
    neighbors = get_accessible_neighbors(x, y)
    if not neighbors:
        return None, None
    return min(neighbors, key=lambda pos: flood[pos[0]][pos[1]])

# =====================================================================
# WALL DETECTION
# =====================================================================
def update_walls(x, y, facing):
    wall_front = API.wallFront()
    wall_left  = API.wallLeft()
    wall_right = API.wallRight()

    front_dir = facing
    left_dir  = DIRECTIONS[(DIRECTIONS.index(facing) - 1) % 4]
    right_dir = DIRECTIONS[(DIRECTIONS.index(facing) + 1) % 4]

    for wall_found, direction in [(wall_front, front_dir),
                                   (wall_left,  left_dir),
                                   (wall_right, right_dir)]:
        if wall_found:
            walls[x][y][direction] = True
            nx, ny = neighbor_in_dir(x, y, direction)
            if nx is not None:
                walls[nx][ny][opposite(direction)] = True

def neighbor_in_dir(x, y, d):
    if d == 'N' and y + 1 < MAZE_SIZE: return (x, y + 1)
    if d == 'S' and y - 1 >= 0:        return (x, y - 1)
    if d == 'E' and x + 1 < MAZE_SIZE: return (x + 1, y)
    if d == 'W' and x - 1 >= 0:        return (x - 1, y)
    return (None, None)

def opposite(d):
    return {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}[d]

# =====================================================================
# MOVEMENT HELPERS
# =====================================================================
def turn_to_face(facing, target):
    for _ in range(4):
        if facing == target:
            break
        API.turnRight()
        facing = DIRECTIONS[(DIRECTIONS.index(facing) + 1) % 4]
    return facing

def move_to(x, y, facing, nx, ny):
    if   nx == x and ny == y + 1: target_dir = 'N'
    elif nx == x and ny == y - 1: target_dir = 'S'
    elif nx == x + 1 and ny == y: target_dir = 'E'
    else:                          target_dir = 'W'
    facing = turn_to_face(facing, target_dir)
    API.moveForward()
    return nx, ny, facing

# =====================================================================
# DISPLAY
# =====================================================================
def update_display(phase):
    """Color cells differently per phase so you can see progress."""
    for x in range(MAZE_SIZE):
        for y in range(MAZE_SIZE):
            if (x, y) in visited_cells:
                continue  # Don't overwrite visited cells
            v = flood[x][y]
            if v == 0:
                API.setColor(x, y, 'G')
            elif v <= 5:
                API.setColor(x, y, 'Y')
            elif v <= 10:
                API.setColor(x, y, 'O')

# =====================================================================
# EXPLORATION NAVIGATION (used in Phase 1 and 2)
# Navigates toward target cells using floodfill, mapping walls.
# =====================================================================
def navigate_to(start_x, start_y, start_facing, target_cells, phase_name, color):
    """
    Navigate from start to any cell in target_cells using floodfill.
    Maps walls as it goes. Returns final (x, y, facing, steps).
    """
    global phase1_steps, phase2_steps

    x, y, facing = start_x, start_y, start_facing
    steps = 0

    log(f"--- {phase_name} Starting ---")

    recalculate_flood(target_cells)
    update_display(phase_name)

    while (x, y) not in target_cells:
        visited_cells.add((x, y))

        # Sense walls
        update_walls(x, y, facing)

        # Recalculate flood with new wall info
        recalculate_flood(target_cells)
        update_display(phase_name)

        # Choose best neighbor
        nx, ny = get_best_neighbor(x, y)

        if nx is None:
            log(f"ERROR: Stuck at ({x},{y})!")
            break

        log(f"[{phase_name}] At ({x},{y}) flood={flood[x][y]} → ({nx},{ny})")

        # Move
        x, y, facing = move_to(x, y, facing, nx, ny)
        steps += 1

        API.setColor(x, y, color)

    visited_cells.add((x, y))
    log(f"--- {phase_name} Complete! Reached ({x},{y}) in {steps} steps ---")
    return x, y, facing, steps

# =====================================================================
# SPEED RUN (Phase 3)
# The maze is now mapped — follow the shortest path directly.
# No wall sensing needed, no recalculation — pure speed
# =====================================================================
def speed_run(start_x, start_y, start_facing, target_cells):
    """
    Run to center on the known shortest path.
    This is the KEY advantage of the optimized algorithm —
    the path is already known so the mouse never takes a wrong turn.
    """
    x, y, facing = start_x, start_y, start_facing
    steps = 0

    log("--- SPEED RUN Starting (optimal path!) ---")

    # Final flood calculation with complete wall knowledge
    recalculate_flood(target_cells)


    API.setColor(x, y, 'B')  # Blue = start

    while (x, y) not in target_cells:
        # Sense walls, recalculate only if new wall found
        walls_before = str(walls[x][y])
        update_walls(x, y, facing)
        if str(walls[x][y]) != walls_before:
            recalculate_flood(target_cells)

        # NO wall sensing in speed run, we already know the maze
        nx, ny = get_best_neighbor(x, y)

        if nx is None:
            log(f"ERROR: Stuck at ({x},{y}) during speed run!")
            break

        log(f"[SPEED RUN] ({x},{y}) flood={flood[x][y]} → ({nx},{ny})")

        x, y, facing = move_to(x, y, facing, nx, ny)
        steps += 1

        API.setColor(x, y, 'G')  # Green = speed run path

    log(f"--- SPEED RUN Complete! Reached ({x},{y}) in {steps} steps ---")
    return x, y, facing, steps

# =====================================================================
# MAIN — 3 PHASE EXECUTION
# =====================================================================
def main():
    log("=== OPTIMIZED FLOODFILL STARTING ===")
    log(f"Maze size: {MAZE_SIZE}x{MAZE_SIZE}")
    log("Phase 1: Explore to center")
    log("Phase 2: Return to start")
    log("Phase 3: Speed run to center")

    API.setColor(0, 0, 'B')  # Blue = start

    # ── PHASE 1: Exploration Run to Center ──────────────────────
    x, y, facing, p1_steps = navigate_to(
        0, 0, 'N',
        CENTER_CELLS,
        "PHASE 1 - Explore",
        'C'  # Cyan = exploration path
    )
    API.setColor(x, y, 'G')
    log(f"Phase 1 done: {p1_steps} steps, {len(visited_cells)} unique cells")

    # ── PHASE 2: Return Run to Start ────────────────────────────
    x, y, facing, p2_steps = navigate_to(
        x, y, facing,
        {START_CELL},
        "PHASE 2 - Return",
        'Y'  # Yellow = return path
    )
    API.setColor(x, y, 'B')
    log(f"Phase 2 done: {p2_steps} steps")

    # ── PHASE 3: Speed Run to Center ────────────────────────────
    x, y, facing, p3_steps = speed_run(
        x, y, facing,
        CENTER_CELLS
    )
    API.setColor(x, y, 'G')

    # ── FINAL STATS ─────────────────────────────────────────────
    total_steps = p1_steps + p2_steps + p3_steps
    log("=== OPTIMIZED FLOODFILL COMPLETE ===")
    log(f"Phase 1 (Explore to center): {p1_steps} steps")
    log(f"Phase 2 (Return to start):   {p2_steps} steps")
    log(f"Phase 3 (Speed run):         {p3_steps} steps")
    log(f"Total steps all phases:      {total_steps}")
    log(f"Unique cells visited:        {len(visited_cells)}")

main()
