from random import randint

def generateWeightedMatrix(size, weight_range):
    output_matrix = [[0]*size for _ in range(size)]
    for i in range (size):
        for j in range(i+1, size):
            value = randint(weight_range[0], weight_range[1])
            output_matrix[i][j] = value
            output_matrix[j][i] = value

    return output_matrix