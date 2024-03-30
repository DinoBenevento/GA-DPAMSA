import config

def is_overlap(range1, range2):
    from_row1, to_row1, from_column1, to_column1 = range1
    from_row2, to_row2, from_column2, to_column2 = range2

    # Check overlap
    overlap_row = from_row1 < to_row2 and to_row1 > from_row2
    overlap_column = from_column1 < to_column2 and to_column1 > from_column2

    return overlap_row and overlap_column

#TODO: can generate error in case the sub-board is not a multiple of the main-board in terms of number of row and column
def get_sum_of_pairs(chromosome,from_row,to_row,from_column,to_column):
    score = 0
    for i in range(from_column, to_column):
        for j in range(from_row,to_row):
            for k in range(j + 1, to_row):
                if chromosome[j][i] == 5 or chromosome[k][i] == 5:
                    score += config.GAP_PENALTY
                elif chromosome[j][i] == chromosome[k][i]:
                    score += config.MATCH_REWARD
                elif chromosome[j][i] != chromosome[k][i]:
                    score += config.MISMATCH_PENALTY
    return score

def check_overlap(new_range,used_ranges):
    for existing_range in used_ranges:
        if is_overlap(new_range, existing_range):
            return True  # range overlap
    return False  # no overlap

def get_all_different_sub_range(individual,m_prime,n_prime):
    m = len(individual)
    #give as n the minimum length of a sequence, this in case we have to align sequence of different size
    n = min(len(genes) for genes in individual)

    m_prime = config.AGENT_WINDOW_ROW
    n_prime = config.AGENT_WINDOW_COLUMN

    #Calculate all the possible sub-board of size m_prime, n_prime from the main board
    unique_ranges = []
    for i in range(m):
        for j in range(n):
            from_row = i 
            to_row = i + m_prime
            from_column = j
            to_column = j + n_prime
            #Check if the range is a range already covered by another interval (we want all different sub-board)
            if(check_overlap((from_row,to_row,from_column,to_column),unique_ranges) == False):
                        unique_ranges.append((from_row,to_row,from_column,to_column))
    
    return unique_ranges

def calculate_worst_fitted_sub_board(individual):
    #Get all the possible sub-board from the individual (the main board)
    unique_ranges = get_all_different_sub_range(individual,config.AGENT_WINDOW_ROW,config.AGENT_WINDOW_COLUMN)
    sub_board_score = []

    #For every sub-board, calculate che sum of pair
    for from_row,to_row,from_column,to_column in unique_ranges:
        score = get_sum_of_pairs(individual,from_row,to_row, from_column, to_column)
        sub_board_score.append(((score),(from_row,to_row,from_column,to_column)))
    
    #Find the sub-board with the worst sum-of-pairs score
    worst_score_subboard = min(sub_board_score, key=lambda x: x[0])

    return worst_score_subboard
    
    ''' This is util for the mainGA to get the sub board in the correct way and also for replace after the mutation
    row_genes = individual[from_row:to_row]
    for genes in row_genes:
        sub_genes = genes[from_column:to_column]      
        sub_board.append(sub_genes)

    all_sub_board.append(sub_board)
    '''    

'''
#Test

matrx = [[1,2,3,4,5,2,1,3,4,5,5,5,1,2,3,4,5,2,1,3,4,1,2,2],
        [1,2,3,4,5,2,1,3,4,5,5,5,2,3,4,5,2,1,3,4,5,1,5,3],
        [1,2,3,4,5,2,1,3,4,5,5,5,2,3,4,5,2,1,3,4,5,1,2,5],
        [1,2,3,4,5,2,1,3,4,5,5,5,2,3,4,5,2,1,3,4,5,1,1,5],
        [1,2,3,4,5,2,1,3,4,5,5,5,2,3,4,5,2,1,3,4,5,1,1,5],
        [1,2,3,4,5,2,1,3,4,5,5,5,2,3,4,5,2,1,3,4,5,1,1,5]]

print(calculate_worst_fitted_sub_board(matrx))
'''