import random

BP = 20
NUM_SEQUENCES = 6
NUM_DATASET = 20
FILE_NAME_REPORT = './dataset1'
FILE_NAME_SCRIPT_OUTPUT = './datasets/dataset1.py'
nucleotides_map = {'A': 1, 'T': 2, 'C': 3, 'G': 4}

datasets = []
for i in range(NUM_DATASET):
    sequences = []  
    for j in range(NUM_SEQUENCES):
        sequence = ''
        for k in range(BP):
          sequence = sequence + random.choice(list(nucleotides_map.keys()))
        sequences.append(sequence)
    datasets.append(sequences)

with open(FILE_NAME_SCRIPT_OUTPUT, 'w') as file:
    file.write(f"file_name = '{FILE_NAME_REPORT}'\n\n")
    file.write(f"datasets = [")
    for index,dataset in enumerate(datasets):
        file.write(f"'dataset{index}',")
    file.write("]\n\n")
    for index,dataset in enumerate(datasets):
        file.write(f"dataset{index} = [\n")
        for sequence in dataset:
            file.write(f'        "{sequence}",\n')
        file.write("    ]\n\n")