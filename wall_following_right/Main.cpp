//right hand model code 

#include <iostream>
#include <string>
#include "API.h"

using namespace std;

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

// Mark walls around current cell based on current direction
// Sensors are read ONCE outside and passed in — avoids re-querying
void markWalls(int x, int y, int direction, bool front, bool left, bool right) {
    if (front) API::setWall(x, y, dirToChar(direction));
    if (left)  API::setWall(x, y, dirToChar((direction + 3) % 4));
    if (right) API::setWall(x, y, dirToChar((direction + 1) % 4));
}

// Update (x, y) position based on direction
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
    log("Right-Hand Rule Starting...");

    API::setColor(0, 0, 'R');
    API::setText(0, 0, "S");

    int x = 0, y = 0;
    int direction = 0; // 0=NORTH, 1=EAST, 2=SOUTH, 3=WEST

    while (!atCenter(x, y)) {

        // Read sensors ONCE per step
        bool front = API::wallFront();
        bool left  = API::wallLeft();
        bool right = API::wallRight();

        // Mark walls on the map
        markWalls(x, y, direction, front, left, right);

        // RIGHT-HAND RULE:
        // Always try to turn right first.
        // If right is open -> turn right.
        // Then: while front is blocked -> turn left.
        // This handles dead ends and corners correctly.

        if (!right) {
            // Right is open -> turn right
            API::turnRight();
            direction = (direction + 1) % 4;
        }

        // After possibly turning right, keep turning left until front is clear
        while (API::wallFront()) {
            API::turnLeft();
            direction = (direction + 3) % 4;
        }

        // Move forward
        API::moveForward();
        updatePosition(x, y, direction);

        // Color visited cells blue and show coordinates
        if (!(x == 0 && y == 0)) {
            API::setColor(x, y, 'B');
            API::setText(x, y, to_string(x) + "," + to_string(y));
        }
    }

    // when reaches center 
    API::setColor(x, y, 'G');
    API::setText(x, y, "END");

    log("Solved! Center at: " + to_string(x) + "," + to_string(y));
    return 0;
}