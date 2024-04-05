import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import RegularPolygon
import random
import time

class HexagonalGrid:
    def __init__(self, ax, radius, n_rows, n_cols):
        self.ax = ax
        self.radius = radius
        self.n_rows = n_rows
        self.n_cols = n_cols
        self.grid = np.empty((n_rows, n_cols), dtype=object)

        # Loop through each row and column
        for i in range(n_rows):
            for j in range(n_cols):
                # Calculate x and y coordinates for the center of each hexagon
                x = radius * np.sqrt(3) * j + (i % 2) * radius * np.sqrt(3) / 2
                y = 3 / 2 * radius * i

                # Create a hexagon patch at the calculated coordinates
                hexagon = RegularPolygon((x, y), numVertices=6, radius=radius,
                                         facecolor='white', edgecolor='black')
                # Add the hexagon patch to the plot
                self.ax.add_patch(hexagon)

                # Store the hexagon in the grid
                self.grid[i, j] = hexagon

        # Set aspect ratio, limits, and turn off axes
        self.ax.set_aspect('equal', 'box')
        self.ax.set_xlim(-radius / 2, (n_cols - 0.5) * radius * np.sqrt(3))  # Adjust x-axis limits
        self.ax.set_ylim(-radius / 2, (n_rows - 1) * 3 / 2 * radius + radius / 2)  # Adjust y-axis limits
        self.ax.axis('off')  # Turn off axes

    def set_color(self, i, j, color):
        # Set color of hexagon at given coordinates and its neighbors
        hexagon = self.grid[i, j]
        hexagon.set_facecolor(color)
        self.ax.figure.canvas.draw_idle()  # Redraw the canvas

    def get_hexagon(self, i, j):
        # Get hexagon at given coordinates
        return self.grid[i, j]

    def get_neighbors(self, i, j):
        # Get neighbors of the hexagon at given coordinates
        neighbors = []
        offsets = [(0, -1), (0, 1), (-1, 0), (1, 0), (1, 1), (-1, 1)]
        for di, dj in offsets:
            ni, nj = i + di, j + dj
            if 0 <= ni < self.n_rows and 0 <= nj < self.n_cols:
                neighbors.append([ni, nj])
        return neighbors

def count(i, j, grid,N):
    total = 0
    offsets = [(0, -1), (0, 1), (-1, 0), (1, 0), (1, 1), (-1, 1)]
    for di, dj in offsets:
        ni, nj = i + di, j + dj
        if 0 <= ni < N and 0 <= nj < N:
            if grid[ni, nj] == 255:
                total = total + 1

    return total



# Function to update the grid for each iteration
def update(frameNum, grid, N, gridHex, a, resur, dead, how, when):
    newGrid = grid.copy()
    for i in range(N):
        for j in range(N):
            # Count live neighbors
            total = count(i,j,newGrid, N)
            # Apply Conway's rules
            if grid[i, j] == ON:
                if (total < 2) or (total > 3):
                    if([i,j] in resur): #Check if the cell was resurrected and if yes, check if it is dying by the same cause
                        if((total<2 and how[i][j] >3) or ((total>3 and how[i][j] <2))): #Only let a cell that died by underpopulation previously die of overpopulation and vice versa
                            newGrid[i, j] = OFF
                            gridHex.set_color(i, j, 'purple')
                            dead.append([i,j])
                            how[i][j] = total
                            when[i][j] = a
                            resur.remove([i, j])
                    else: #If not a resurrected cell
                        newGrid[i, j] = OFF
                        gridHex.set_color(i, j, 'purple')
                        dead.append([i, j])
                        how[i][j] = total
                        when[i][j] = a

            else: #Revive a cell with 3 neighbours
                if (total == 3):
                    newGrid[i, j] = ON
                    gridHex.set_color(i, j, 'yellow')
                    if ([i,j] in dead): dead.remove([i,j])
                    resur.append([i,j])


    if(a%4 == 0): #Resurrect a random cell every 4 generations
        i = random.randint(0, len(dead)-1)
        newGrid[dead[i][0], dead[i][1]] = ON
        gridHex.set_color(dead[i][0], dead[i][1], 'yellow')
        resur.append(dead[i])
        dead.pop(i)

    for [i, j] in dead: #Resurrect a cell after 6 generations
        if (a - when[i][j]) % 6 == 0:
            newGrid[i, j] = ON
            gridHex.set_color(i, j, 'yellow')
            if ([i, j] in dead): dead.remove([i, j])
            resur.append([i, j])

    fig.savefig(f'generation_{a}.png')

    grid[:] = newGrid[:]
    a = a+1
    return newGrid, a

# Constants
ON= 255
OFF = 0
N = 20
a = 0
resur = []
dead = []
how = [[0 for a in range(N)] for b in range(N)]
when = [[0 for j in range(N)] for k in range(N)]




updateInterval = 500

# Create a random grid
grid = np.random.choice([ON, OFF], N*N, p=[0.1, 0.9]).reshape(N, N)

for i, row in enumerate(grid):
    for j, element in enumerate(row):
        if(grid[i][j] == OFF):
            dead.append([i,j])

# Set up the animation
fig, ax = plt.subplots()
gridHex = HexagonalGrid(ax, radius=20, n_rows=N, n_cols=N)

ani = animation.FuncAnimation(fig=fig, func=update, fargs=(grid, N, gridHex, a, resur, dead, how, when), frames=1, interval=updateInterval)
time.sleep(0.001)
# Display the animation
plt.show()
