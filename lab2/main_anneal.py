import time
import math
from random import randint, random
from generate import generateWeightedMatrix

SIZE = 100
WEIGHT_RANGE = [10, 30]
MAX_COST = 2000
INITIAL_TEMP = 1000
MIN_TEMP = 0.001
MAX_ITERATIONS = 100000

def solve_tsp_anneal():
    global stats
    stats = {
        "status": None,
        "processing_time": 0,
        "iterations": 0,
        "dead_ends": 0,
        "generated_nodes": 0,
        "max_memory": 0
    }

    matrix = generateWeightedMatrix(SIZE, WEIGHT_RANGE)

    start_time = time.time()

    current_path = init_path(matrix)
    current_cost = calculate_cost(matrix, current_path)

    stats["max_memory"] = SIZE 

    best_cost = current_cost

    k = INITIAL_TEMP / MAX_ITERATIONS
    t = 0
    current_temp = INITIAL_TEMP

    while current_temp >= MIN_TEMP and t < MAX_ITERATIONS:
        t += 1
        stats["iterations"] += 1
        stats["generated_nodes"] += 1

        new_path = list(current_path)

        i = randint(0, SIZE-1)
        j = randint(0, SIZE-1)
        while i == j:
            j = randint(0, SIZE-1)

        i, j = sorted([i, j])
        new_path[i:j+1] = reversed(new_path[i:j+1])

        new_cost = calculate_cost(matrix, new_path)
        delta = new_cost - current_cost

        accepted = False
        
        if delta < 0:
            accepted = True
        else:
            prob = math.exp(-delta / current_temp)
            if random() < prob:
                accepted = True

        if accepted:
            current_path = new_path
            current_cost = new_cost

            if current_cost < best_cost:
                best_cost = current_cost
        else:
            stats["dead_ends"] += 1

        current_temp = INITIAL_TEMP - (k * t)

    stats["processing_time"] = time.time() - start_time
    stats["status"] = "Found" if best_cost <= MAX_COST else "Fail"

    return stats

def calculate_cost(matrix, path):
    cost = 0
    for i in range(len(matrix) - 1):
        cost += matrix[path[i]][path[i+1]]

    cost += matrix[path[-1]][path[0]]
    return cost

def init_path(matrix, start=0):
    unvisited = set(range(len(matrix)))
    unvisited.remove(start)

    cur = start
    path = [start]

    while unvisited:
        next_node = min(unvisited, key=lambda node: matrix[cur][node])

        path.append(next_node)
        unvisited.remove(next_node)
        cur = next_node

    return path

for i in range(1, 21):
    print(f"{i}. Stats:\n{solve_tsp_anneal()}\n")