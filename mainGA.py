import datasets.dataset3 as dataset1
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
        
        for i in range(config.GA_NUM_ITERATION):
            
            used_ranges = []

            #Mutation
            for individual in ga.population:

                #Define sub-board size (where RL agent perform mutation)

                #If we have explored all the zone in the Game board, go to the next iteration
                if(len(used_ranges) == config.NUM_TOTAL_RANGES):
                    break

                #On every individual, we want to use the RL agent in a different position on the game board
                #Continue to generate number until a range not explored is found
                while True:
                    from_row = random.randint(0, len(individual) - config.AGENT_WINDOW_ROW)
                    from_column = random.randint(0,sequence_min_length - config.AGENT_WINDOW_COLUMN)

                    to_row = from_row + config.AGENT_WINDOW_ROW
                    to_column = from_column + config.AGENT_WINDOW_COLUMN

                    if(utils.check_overlap((from_row,to_row,from_column,to_column),used_ranges) == False):
                        used_ranges.append((from_row,to_row,from_column,to_column))
                        break

                #Construct the sub-board
                sub_board = []
                row_selected = []
                for index,genes in enumerate(individual):
                    if index >= from_row and index <= to_row:   #Get only element with index beetwen the range (number of sequence)
                        sub_genes = genes[from_column:to_column]  #Select only the number of nucleotides beetwen the column range
                        row_selected.append(index)          #Save index of row selected
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
                for index,sequence in enumerate(env.aligned):
                    index_gene = row_selected[index]  #Recover the right genes from the individual
                    genes_to_mutate = individual[index_gene]
                    genes_to_mutate[from_column:to_column+1] = sequence
                    individual[index_gene] = genes_to_mutate
            
            #Calculate the fitness score for all individuals
            ga.calculate_fitness_score()

            #Select the most fitted individuals and perform crossover
            ga.selection_and_crossover()
        

            most_fitted_chromosome,sum_pairs_score = ga.get_most_fitted_chromosome()
            most_fitted_chromosome_converted = ga.get_alignment(most_fitted_chromosome)
            print(f"SP:{sum_pairs_score}")
            print(f"Alignment:\n{most_fitted_chromosome_converted}")
            
if __name__ == "__main__":
    #inference(dataset=dataset,model_path='model_test.pth',tag=dataset.file_name)
    inference()