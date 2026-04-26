//left hand model code

#include <iostream>
#include <string>
#include "API.h"

using namespace std;

// Log to stderr (visible in simulator's Run Output tab)
void log(const string& text) {
    cerr << text << endl;
}

// Convert direction integer to character
char dirToChar(int direction) {
    if (direction == 0) return 'n';
    if (direction == 1) return 'e';
    if (direction == 2) return 's';
    return 'w';
}

// Mark walls around current cell — sensors read ONCE and passed in
void markWalls(int x, int y, int direction, bool front, bool left, bool right) {
    if (front) API::setWall(x, y, dirToChar(direction));
    if (left)  API::setWall(x, y, dirToChar((direction + 3) % 4));
    if (right) API::setWall(x, y, dirToChar((direction + 1) % 4));
}

// Update position based on current direction
void updatePosition(int& x, int& y, int direction) {
    if (direction == 0) y++;       // NORTH
    else if (direction == 1) x++;  // EAST
    else if (direction == 2) y--;  // SOUTH
    else if (direction == 3) x--;  // WEST
}

// Check if mouse reached center (works for both 8x8 and 16x16)
bool atCenter(int x, int y) {
    int w = API::mazeWidth();
    int h = API::mazeHeight();
    int cx1 = w / 2 - 1;
    int cx2 = w / 2;
    int cy1 = h / 2 - 1;
    int cy2 = h / 2;
    return (x == cx1 || x == cx2) && (y == cy1 || y == cy2);
}

int main() {
    log("Left-Hand Rule Starting...");

    API::setColor(0, 0, 'R');
    API::setText(0, 0, "S");

    int x = 0, y = 0;
    int direction = 0; // Start facing NORTH

    while (!atCenter(x, y)) {

        // Read all sensors ONCE per step
        bool front = API::wallFront();
        bool left  = API::wallLeft();
        bool right = API::wallRight();

        // Mark walls on the map
        markWalls(x, y, direction, front, left, right);

        // LEFT-HAND RULE:
        // Always try to turn left first.
        // If left is open -> turn left and go.
        // Then: while front is blocked -> turn right.
 

        if (!left) {
            // Left is open -> turn left
            API::turnLeft();
            direction = (direction + 3) % 4;
        }

        // After possibly turning left, keep turning right until front is clear
        while (API::wallFront()) {
            API::turnRight();
            direction = (direction + 1) % 4;
        }

        // Move forward
        API::moveForward();
        updatePosition(x, y, direction);

        // Color visited cells cyan and show coordinates
        if (!(x == 0 && y == 0)) {
            API::setColor(x, y, 'C');
            API::setText(x, y, to_string(x) + "," + to_string(y));
        }
    }

    // Reached center!
    API::setColor(x, y, 'G');
    API::setText(x, y, "END");

    log("Solved! Center at: " + to_string(x) + "," + to_string(y));
    return 0;
}