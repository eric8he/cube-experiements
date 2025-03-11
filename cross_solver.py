from magiccube import Cube
from copy import deepcopy, copy
from pyTwistyScrambler import scrambler333

MOVES = ["R", "R'", "R2", "L", "L'", "L2", "U", "U'", "U2", "D", "D'", "D2", "F", "F'", "F2", "B", "B'", "B2"]
dummy = Cube()
dummy.rotate("Z2")
CROSS = deepcopy([dummy.find_piece("YO"), dummy.find_piece("YR"), dummy.find_piece("YG"), dummy.find_piece("YB")])
print(len(MOVES), "moves available")

def solve_cross(cube: Cube):
    def cross_solved(cube: Cube):
        # check if bottom 4 edges are solved
        return all(cube.find_piece(str(x[1]))[0] == x[0] for x in CROSS)

    visited = set()
    seen = set()
    queue = [(cube, [])]
    
    while queue:
        if len(visited) % 100 == 0:
            print("Queue size:", len(queue))
            print("Visited states:", len(visited))
            #print("sample position:", queue[0][0], queue[0][1])
            
        cube, moves = queue.pop(0)  # For DFS change this to queue.pop()
        state = str(cube)
        
        # Skip if we have already visited this state.
        if state in visited:
            continue
        visited.add(state)
        
        if cross_solved(cube):
            return moves
        
        for move in MOVES:
            new_cube = deepcopy(cube)
            new_cube.rotate(move)
            new_state = str(new_cube)
            if new_state not in visited and new_state not in seen:
                seen.add(new_state)
                queue.append((new_cube, moves + [move]))

cube = Cube(3, hist=False)
#cube.rotate("Z2")
scram = "B D' F R B2 R2 F L F' B2 R2 F' D2 L2 U2 B' L2 B' D2 R Z2"#scrambler333.get_WCA_scramble()
cube.rotate(scram)
print(cube)
solution = solve_cross(cube)
print("Solution moves:", solution)
