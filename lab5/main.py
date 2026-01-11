from generator import generate_items, generate_population
from interfaces import Individual
import math
import random
import copy
import json

CAPACITY = 250
NUM_ITEMS = 100
POPULATION_SIZE = 100
CROSSOVER_RATE = 0.25
MUTATION_RATE = 0.05
MAX_ITERATIONS = 1000
SA_START_ITERATION = 200

def calculate_individual_value(individual, items):
    total_v = 0
    total_w = 0

    for i in range(NUM_ITEMS):
        if individual.genes[i] == 1:
            total_v += items[i]["v"]
            total_w += items[i]["w"]

    individual.weight = total_w
    if total_w > CAPACITY:
        individual.value = 0
    else:
        individual.value = total_v

def crossover(parent1, parent2):
    if random.random() > CROSSOVER_RATE:
        return copy.deepcopy(parent1)
    
    points = sorted(random.sample(range(1, NUM_ITEMS), 3))
    k1, k2, k3 = points
    
    child_genes = parent1.genes[:k1] + parent2.genes[k1:k2] + parent1.genes[k2:k3] + parent2.genes[k3:]
    
    return Individual(child_genes)

def mutate(individual, items):
    if random.random() < MUTATION_RATE:
        index = random.randint(0, NUM_ITEMS - 1)
        individual.genes[index] = 1 - individual.genes[index]
        calculate_individual_value(individual, items)

def simulated_annealing(individual, current_iter, items):
    T = 50.0 / (1 + 0.05 * (current_iter - SA_START_ITERATION))
    
    neighbor_genes = individual.genes[:]
    index = random.randint(0, NUM_ITEMS - 1)
    neighbor_genes[index] = 1 - neighbor_genes[index]
    neighbor = Individual(neighbor_genes)
    
    calculate_individual_value(neighbor, items)
    delta = neighbor.value - individual.value
    
    if delta > 0:
        individual.genes = neighbor_genes
        individual.value = neighbor.value
        individual.weight = neighbor.weight
    else:
        if T > 0.001:
            prob = math.exp(delta / T)
            if random.random() < prob:
                individual.genes = neighbor_genes
                individual.value = neighbor.value
                individual.weight = neighbor.weight

def main():
    items = generate_items(NUM_ITEMS, 22)
    population = generate_population(POPULATION_SIZE, NUM_ITEMS)

    best_global_value = 0

    print(f"{'Iterarion':<15} | {'Best value':<15} | {'Current weight':<15}")

    for iteration in range(MAX_ITERATIONS + 1):
        population.sort(key=lambda x: x.value, reverse=True)

        current_best = population[0]
        if current_best.value > best_global_value:
            best_global_value = current_best.value

        if iteration % 20 == 0:
            print(f"{iteration:<15} | {current_best.value:<15} | {current_best.weight}/{CAPACITY:<15}")
    
        new_population = copy.deepcopy(population[:10])

        while len(new_population) < POPULATION_SIZE:
            parent1 = max(random.sample(population, 5), key=lambda x: x.value)
            parent2 = max(random.sample(population, 5), key=lambda x: x.value)

            child = crossover(parent1, parent2)
            calculate_individual_value(child, items)
            mutate(child, items)

            if iteration >= SA_START_ITERATION:
                simulated_annealing(child, iteration, items)

            new_population.append(child)

        population = new_population

    print("-" * 50)
    print(f"Result: {best_global_value}\n")

main()
    