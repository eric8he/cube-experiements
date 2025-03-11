import threading
import time
from queue import Queue
from copy import deepcopy
from magiccube import Cube
from pyTwistyScrambler import scrambler333

# Define available moves.
MOVES = ["R", "R'", "R2", "L", "L'", "L2", "U", "U'", "U2",
         "D", "D'", "D2", "F", "F'", "F2", "B", "B'", "B2"]

# Pre-calculate the cross pieces.
dummy = Cube()
dummy.rotate("Z2")
CROSS = deepcopy([dummy.find_piece("YO"), dummy.find_piece("YR"),
                  dummy.find_piece("YG"), dummy.find_piece("YB")])
print(len(MOVES), "moves available")

def solve_cross(cube: Cube, num_threads=4):
    def cross_solved(cube: Cube):
        # Check if bottom 4 edges are solved.
        return all(cube.find_piece(str(x[1]))[0] == x[0] for x in CROSS)

    # Thread-safe queue for states; each entry is (cube, moves list).
    state_queue = Queue()
    state_queue.put((cube, []))
    
    # A set to record visited states.
    visited = set()
    visited_lock = threading.Lock()
    
    # Event to signal that a solution has been found.
    solution_event = threading.Event()
    solution = [None]  # To store the solution moves.

    def worker():
        while True:
            current_cube, moves = state_queue.get()
            # Check for termination signal.
            if current_cube is None:
                state_queue.task_done()
                break

            # If a solution is already found, skip further processing.
            if solution_event.is_set():
                state_queue.task_done()
                continue

            state = str(current_cube)
            with visited_lock:
                if state in visited:
                    state_queue.task_done()
                    continue
                visited.add(state)
            
            if cross_solved(current_cube):
                solution[0] = moves
                solution_event.set()
                state_queue.task_done()
                print("Solution found!", moves)
                break  # Exit this worker.
            
            # Enqueue all children states.
            for move in MOVES:
                new_cube = deepcopy(current_cube)
                new_cube.rotate(move)
                new_state = str(new_cube)
                with visited_lock:
                    if new_state not in visited:
                        state_queue.put((new_cube, moves + [move]))
            state_queue.task_done()

    # Progress monitor: prints visited count and queue size periodically.
    def progress_monitor():
        while not solution_event.is_set():
            with visited_lock:
                visited_count = len(visited)
            queue_size = state_queue.qsize()
            print(f"Visited states: {visited_count}, Queue size: {queue_size}")
            time.sleep(1)

    # Start the progress monitor thread.
    progress_thread = threading.Thread(target=progress_monitor)
    progress_thread.daemon = True
    progress_thread.start()

    # Start worker threads.
    threads = []
    for _ in range(num_threads):
        t = threading.Thread(target=worker)
        t.daemon = True  # Daemon threads exit when main thread exits.
        t.start()
        threads.append(t)

    # Wait for a solution to be found.
    solution_event.wait()

    # Signal all worker threads to exit by sending stop signals.
    for _ in range(num_threads):
        state_queue.put((None, None))

    # Wait for all tasks in the queue to be marked as done.
    state_queue.join()

    # Join all worker threads.
    for t in threads:
        t.join()

    return solution[0]

# Create a 3x3 cube, scramble it, and try to solve the cross.
cube = Cube(3, hist=False)
scram = "B D' F R B2 R2 F L F' B2 R2 F' D2 L2 U2 B' L2 B' D2 R Z2"
cube.rotate(scram)
print("Scrambled Cube:\n", cube)

solution_moves = solve_cross(cube, num_threads=3)
print("Solution moves:", solution_moves)
