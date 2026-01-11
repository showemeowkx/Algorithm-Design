import random
from interfaces import Individual

def generate_items(num_items, seed=-1):
    if seed != -1:
        random.seed(seed)

    items = []
    for _ in range(num_items):
        items.append({
            "v": random.randint(2, 30),
            "w": random.randint(1, 25)
        })

    return items

def generate_population(population_size, gen_size):
    population = [Individual() for _ in range(population_size)]

    for index, individual in enumerate(population):
        genes = [0] * gen_size
        if index < gen_size:
            genes[index] = 1
        individual.genes = genes

    return population
