# Micromouse Maze Simulation

**Course:** Interfacing Techniques - ENCS4380  
Birzeit University — Electrical and Computer Engineering Department  


---

## Project Overview

This repository contains the simulation phase of the Micromouse project. Three navigation algorithms were implemented and tested in the [mms simulator](https://github.com/mackorone/mms) on both 8×8 and 16×16 mazes. The goal is to compare algorithm performance in terms of distance to center and unique cells visited.

---

## Repository Structure

```
micromouse-maze-simulation/
├── Micromouse_Simulation_Report.pdf   ← Full simulation report
├── floodfill/
│   ├── API.py                         ← mms Python API
│   ├── floodfill.py                   ← Standard Floodfill algorithm
│   └── optimized_floodfill.py         ← Optimized Floodfill (3-phase)
├── wall_following_left/
│   ├── API.cpp                        ← mms C++ API
│   ├── API.h
│   └── Main.cpp                       ← Left-hand wall following
├── wall_following_right/
│   ├── API.cpp
│   ├── API.h
│   └── Main.cpp                       ← Right-hand wall following
├── maze_8x8_test1.txt                 ← 8×8 maze file
└── maze_8x8_test2.txt                 ← 8×8 maze file
```

---

## Algorithms

### 1. Wall-Following (Left & Right Hand Rule) — C++
The simplest navigation strategy. The mouse keeps one hand touching a wall and follows it. Works on simple mazes but fails on 16×16 mazes with isolated wall structures where the start and center are not connected to the same continuous wall.

### 2. Standard Floodfill — Python
Assigns a distance value to every cell based on its distance to the center. The mouse always moves to the neighbor with the lowest flood value. When a new wall is discovered, all flood values are recalculated using BFS. Successfully solves all maze sizes.

### 3. Optimized Floodfill (3-Phase) — Python
Extends standard Floodfill with three phases:
- **Phase 1:** Navigate to center while mapping all walls
- **Phase 2:** Return to start, continuing to map walls
- **Phase 3 (Speed Run):** Navigate to center on the fully known optimal path

The Phase 3 speed run is up to 79% faster than standard Floodfill on complex mazes.

---

## Setup & Running

### Requirements
- [mms simulator](https://github.com/mackorone/mms) (Windows)
- Python 3.x (for floodfill algorithms)
- A C++ compiler (for wall following) — or use the pre-compiled `myMouse.exe`

### Running Python Algorithms (Floodfill)
1. Open the mms simulator
2. Click **"+"** next to the Mouse dropdown
3. Set:
   - **Directory:** path to the `floodfill/` folder
   - **Run Command:** `python floodfill.py` or `python optimized_floodfill.py`
4. Click **Build** then **Run**

### Running C++ Algorithms (Wall Following)
1. Compile `Main.cpp` with `API.cpp` and `API.h`, or use the provided executable
2. In the mms simulator, click **"+"** next to Mouse
3. Set:
   - **Directory:** path to `wall_following_left/` or `wall_following_right/`
   - **Run Command:** `.\myMouse.exe`
4. Click **Run**

### Loading 8×8 Mazes
1. In the simulator, click the **folder icon** next to the Maze dropdown
2. Navigate to and select `maze_8x8_test1.txt` or `maze_8x8_test2.txt`

---

## Results Summary

| Algorithm | Maze | Size | Distance to Center | Unique Cells Visited |
|---|---|---|---|---|
| Wall-Following Left | Example 1-3 | 16×16 | DNF | — |
| Wall-Following Left | Test 1 | 8×8 | 20 | 12 |
| Standard Floodfill | Example 1 | 16×16 | 276 | 118 |
| Standard Floodfill | Example 4 | 16×16 | 576 | 199 |
| Optimized Floodfill | Example 4 | 16×16 | 120 (speed run) | 143 |

For full results see `Micromouse_Simulation_Report.pdf`.

---

## Notes
- The mms simulator executable is not included in this repository. Download it from [github.com/mackorone/mms](https://github.com/mackorone/mms)
- 8×8 maze files are in text format (`.txt`) — load them directly via the simulator's folder browser
