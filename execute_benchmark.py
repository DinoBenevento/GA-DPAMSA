import subprocess
import os
import utils
import csv

dataset_name = 'dataset1_3x30bp'
dataset_folder = f'./datasets/fasta_files/{dataset_name}/'

files = os.listdir(dataset_folder)
files.sort()
csv_data = []
for file in files:
    file_path = dataset_folder + file
    command_clustalo = f'./clustalo/clustalo -i {file_path}'
    command_msaprobs = f"/workspaces/DPAMSA/MSAProbs/MSAProbs/msaprobs {file_path}"
    alignment_output_clustalo = subprocess.check_output(command_clustalo, shell=True,encoding='utf-8')
    alignment_output_msaprobs = subprocess.check_output(command_msaprobs, shell=True,encoding='utf-8')
    sum_of_pairs_clustalo = utils.sum_of_pairs_from_fasta(alignment_output_clustalo)
    sum_of_pairs_msaprobs = utils.sum_of_pairs_from_fasta(alignment_output_msaprobs)
    csv_data.append([file,sum_of_pairs_clustalo,sum_of_pairs_msaprobs])

with open(f'./result/benchmark/{dataset_name}_clustalo_msaprobs', mode='w', newline='') as file_csv:
    writer = csv.writer(file_csv)
    writer.writerow(["File name", "SP_ClustalOmega", "SP_MSAProbs"])
    writer.writerows(csv_data)
    