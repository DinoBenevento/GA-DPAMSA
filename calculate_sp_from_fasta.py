import utils
def parse_fasta_to_matrix(fasta_file):
    sequences = {}
    max_length = 0

    nucleotides_map = {'A': 1, 'T': 2, 'C': 3, 'G': 4, 'a': 1, 't': 2, 'c': 3, 'g': 4, '-': 5}

    # Read FASTA file
    with open(fasta_file, 'r') as f:
        lines = f.readlines()
        seq = ''
        seq_name = ''
        for line in lines:
            if line.startswith('>'):
                if seq_name != '':
                    sequences[seq_name] = seq
                    max_length = max(max_length, len(seq))
                seq_name = line.strip().lstrip('>')
                seq = ''
            else:
                seq += line.strip()
        if seq_name != '':
            sequences[seq_name] = seq
            max_length = max(max_length, len(seq))

    # Align sequence in the list
    aligned_sequences = {}
    for seq_name, seq in sequences.items():
        aligned_seq = seq + '-' * (max_length - len(seq))
        aligned_sequences[seq_name] = aligned_seq

    # Create matrix
    matrix = []
    for seq_name in sorted(aligned_sequences.keys()):  # Sort sequence
        row = []
        for char in aligned_sequences[seq_name]:
            row.append(nucleotides_map.get(char, 0))  # Default 0 if char not in the map
        matrix.append(row)

    return matrix

# Fasta file path
fasta_file = './test.fasta'  
matrix = parse_fasta_to_matrix(fasta_file)

print(utils.get_sum_of_pairs(matrix,0,len(matrix),0,len(matrix[0])))
