import datasets.dataset1 as dataset1
from GA import GA
import torch
import os
from env_GA import Environment
from dqn import DQN
import config
from tqdm import tqdm
import random
import utils

dataset = dataset1

def main():
    #config.device_name = "cuda:{}".format(sys.argv[1])
    config.device = torch.device(config.device_name)
    #multi_train(dataset.file_name, 0, 25, truncate_file=True)


def output_parameters():
    print("Gap penalty: {}".format(config.GAP_PENALTY))
    print("Mismatch penalty: {}".format(config.MISMATCH_PENALTY))
    print("Match reward: {}".format(config.MATCH_REWARD))
    print("Episode: {}".format(config.max_episode))
    print("Batch size: {}".format(config.batch_size))
    print("Replay memory size: {}".format(config.replay_memory_size))
    print("Alpha: {}".format(config.alpha))
    print("Epsilon: {}".format(config.epsilon))
    print("Gamma: {}".format(config.gamma))
    print("Delta: {}".format(config.delta))
    print("Decrement iteration: {}".format(config.decrement_iteration))
    print("Update iteration: {}".format(config.update_iteration))
    print("Device: {}".format(config.device_name))
    print(f"Window size:{config.AGENT_WINDOW_ROW}x{config.AGENT_WINDOW_COLUMN}")


def inference(tag='',start=0, end=1, truncate_file=False, model_path='model'):
    output_parameters()
    print("Dataset number: {}".format(len(dataset.datasets)))

    report_file_name = os.path.join(config.report_path_DPAMSA_GA, "{}.rpt".format(tag))

    if truncate_file:
        with open(report_file_name, 'w') as _:
            _.truncate()

    for index, name in enumerate(dataset.datasets[start:end if end != -1 else len(dataset.datasets)], start):
        if not hasattr(dataset, name):
            continue
        seqs = getattr(dataset, name)
        
        ga = GA(seqs)
        ga.generate_population()

        #Check the correct size of the window in which the RL agent operate
        first_individual = ga.population[0]
        if config.AGENT_WINDOW_ROW > len(first_individual):
            print("Window row grater than the number of a sequence")

            return 
        
        sequence_min_length = min(len(genes) for genes in first_individual)
        if config.AGENT_WINDOW_COLUMN > sequence_min_length:
            print("Window column grater than the min length of a sequence")

            return 
        
        #Calculate all the possible different sub-boards from the main board (we want to run the RL agent in diefferent sub-board for different individual)
        unique_ranges = utils.get_all_different_sub_range(first_individual,config.AGENT_WINDOW_ROW,config.AGENT_WINDOW_COLUMN)
        
        for i in range(config.GA_NUM_ITERATION):
            
            used_ranges = []

            #Mutation
            for individual in ga.population:

                #Define sub-board size (where RL agent perform mutation)

                #If we have explored all the zone in the Game board, go to the next iteration
                if(len(used_ranges) == len(unique_ranges)):
                    break

                #Choose a range in a random way
                #We want to use the RL agent in a different position on the sub-game board
                range_founded = False
                while range_founded == False: 
                    range_index = random.randint(0,len(unique_ranges) - 1)
                    range_selected = unique_ranges[range_index]
                    if range_selected not in used_ranges:
                        used_ranges.append(range_selected)
                        range_founded = True

                #Construct the sub-board
                from_row, to_row, from_column, to_column = range_selected
                #Get only the selected row
                row_genes = individual[from_row:to_row]
                sub_board = []


                ##To prevent to fill the space with all gaps is better to have that the sub-board is a multiple of the main board in terms of row x column
                ##If the main board can't be perfectly divide in slice of size AGENT_WINDOW_ROW, a raw with all GAP is added to fill the space (the RL agent won't work if size is less than the size in the training)
                fake_row_counter = 0
                while (len(row_genes) < config.AGENT_WINDOW_ROW):
                    all_gap_row = []
                    while (len(all_gap_row) < config.AGENT_WINDOW_COLUMN):
                        all_gap_row.append(5)
                    fake_row_counter = fake_row_counter + 1
                    row_genes.append(all_gap_row)

                for genes in row_genes:
                    sub_genes = genes[from_column:to_column]  
                    #If the main board can't be perfectly divide in slice of size AGENT_WINDOW_COLUMN, GAP is added to fill the space (the RL agent won't work if size is less than the size in the training) 
                    while len(sub_genes) < config.AGENT_WINDOW_COLUMN:
                        sub_genes.append(5)
                    sub_board.append(sub_genes)

                #Perform Mutation on the sub-board with RL
                env = Environment(sub_board)
                agent = DQN(env.action_number, env.row, env.max_len, env.max_len * env.max_reward)
                agent.load(model_path)
                state = env.reset()

                while True:
                    action = agent.predict(state)
                    _, next_state, done = env.step(action)
                    state = next_state
                    if 0 == done:
                        break
                
                env.padding()
                #Put mutated genes in the right position in the individual
                genes_to_mutate = individual[from_row:to_row]
                for index,sequence in enumerate(env.aligned):
                        #if(index < len(genes_to_mutate) - 1): #This is necessary due to the row with all GAP added in case the number of row for the window is not multiple of the main board rows
                        genes_to_mutate[index][from_column:to_column] = sequence
                individual[from_row:to_row] = genes_to_mutate
                
            #Calculate the fitness score for all individuals
            ga.calculate_fitness_score()

            ga.selection()

            ga.horizontal_crossover()
        

            most_fitted_chromosome,sum_pairs_score = ga.get_most_fitted_chromosome()
            most_fitted_chromosome_converted = ga.get_alignment(most_fitted_chromosome)
            print(f"SP:{sum_pairs_score}")
            print(f"Alignment:\n{most_fitted_chromosome_converted}")
            
if __name__ == "__main__":
    #inference(dataset=dataset,model_path='model_test.pth',tag=dataset.file_name)
    inference()