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

            #Mutation with the RL agent
            ga.random_mutation(model_path)
                
            #Calculate the fitness score for all individuals, based on the sum-of-pairs
            ga.calculate_fitness_score()

            #Execute the selection, get only the most fitted individual for the next iteration
            ga.selection()

            #Crossover, split board in two different part and create new individuals by merging each part by 
            #taking the first part from one individual and the second part from another individual
            ga.horizontal_crossover()
        
        most_fitted_chromosome,sum_pairs_score = ga.get_most_fitted_chromosome()
        most_fitted_chromosome_converted = ga.get_alignment(most_fitted_chromosome)
        print(f"SP:{sum_pairs_score}")
        print(f"Alignment:\n{most_fitted_chromosome_converted}")
            
if __name__ == "__main__":
    #inference(dataset=dataset,model_path='model_test.pth',tag=dataset.file_name)
    inference()