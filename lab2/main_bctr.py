import time
from generate import generateWeightedMatrix

SIZE = 100
WEIGHT_RANGE = [10, 30]
MAX_COST = 2000

def solve_tsp_bctr():
    global stats
    stats = {"status": None, "processing_time": 0, "iterations": 0, "dead_ends": 0, "generated_nodes": 0, "max_memory": 0}

    visited = [False]*SIZE
    visited[0] = True
    matrix  = generateWeightedMatrix(SIZE, WEIGHT_RANGE)

    start_time = time.time()
    found = backtrack(matrix, 0, 0, 1, visited)

    stats["processing_time"] = time.time() - start_time
    stats["status"] = "Found" if found else "Fail"

    return stats

def backtrack(matrix, u, current_cost, count, visited):
    global stats
    stats["iterations"] += 1

    if count > stats["max_memory"]:
        stats["max_memory"] = count

    if count == SIZE:
        if matrix[u][0]:
            total_cost = current_cost + matrix[u][0]
            if total_cost <= MAX_COST:
                return True
            
        stats["dead_ends"] += 1
        return False

    for v in range(SIZE):
        if not visited[v]:
            stats["generated_nodes"] += 1
            new_cost = current_cost + matrix[u][v]

            if new_cost <= MAX_COST:
                visited[v] = True
                
                if backtrack(matrix, v, new_cost, count + 1, visited):
                    return True
                
                visited[v] = False
            else:
                stats["dead_ends"] += 1

    stats["dead_ends"] += 1
    return False

for i in range(1, 21):
    print(f"{i}. Stats:\n{solve_tsp_bctr()}\n")