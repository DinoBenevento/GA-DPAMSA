import datasets.dataset1_3x30bp as dataset1
from env import Environment
from dqn import DQN
import config
from tqdm import tqdm
import os
import torch
import sys

dataset = dataset1


def main():
    config.device = torch.device(config.device_name)

    multi_train(dataset.file_name,model_path='model_3x30')


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


def multi_train(tag="", truncate_file=False,model_path='model'):
    output_parameters()
    print("Dataset number: {}".format(len(dataset.datasets)))

    report_file_name = os.path.join(config.report_path_DPAMSA, "{}.rpt".format(tag))

    if truncate_file:
        with open(report_file_name, 'w') as _:
            _.truncate()

    for dataset_name in dataset.datasets:
        if not hasattr(dataset, dataset_name):
            continue
        seqs = getattr(dataset, dataset_name)

        env = Environment(seqs)
        agent = DQN(env.action_number, env.row, env.max_len, env.max_len * env.max_reward)
        p = tqdm(range(config.max_episode))
        p.set_description(dataset_name)

        try:
            agent.load(model_path)
        except Exception as e:
            pass

        for _ in p:
            state = env.reset()
            while True:
                action = agent.select(state)
                reward, next_state, done = env.step(action)
                agent.replay_memory.push((state, next_state, action, reward, done))
                agent.update()
                if done == 0:
                    break
                state = next_state
            agent.update_epsilon()

        
        state = env.reset()

        while True:
            action = agent.predict(state)
            _, next_state, done = env.step(action)
            state = next_state
            if 0 == done:
                break
        
        env.padding()
        agent.save(model_path)
        report = "{}\n{}\n{}\n{}\n{}\n{}\n{}\n\n".format("NO: {}".format(dataset_name),
                                                         "AL: {}".format(len(env.aligned[0])),
                                                         "SP: {}".format(env.calc_score()),
                                                         "EM: {}".format(env.calc_exact_matched()),
                                                         "CS: {}".format(
                                                             env.calc_exact_matched() / len(env.aligned[0])),
                                                         "QTY: {}".format(len(env.aligned)),
                                                         "#\n{}".format(env.get_alignment()))

        with open(os.path.join(config.report_path_DPAMSA, "{}.rpt".format(tag)), 'a+') as report_file:
            report_file.write(report)


def train(index):
    output_parameters()

    assert hasattr(dataset, "dataset_{}".format(index)), "No such data called {}".format("dataset_{}".format(index))
    data = getattr(dataset, "dataset_{}".format(index))

    print("{}: dataset_{}: {}".format(dataset.file_name, index, data))

    env = Environment(data)
    agent = DQN(env.action_number, env.row, env.max_len, env.max_len * env.max_reward)
    p = tqdm(range(config.max_episode))

    for _ in p:
        state = env.reset()
        while True:
            action = agent.select(state)
            reward, next_state, done = env.step(action)
            agent.replay_memory.push((state, next_state, action, reward, done))
            agent.update()
            if done == 0:
                break
            state = next_state
        agent.update_epsilon()

    # Predict
    state = env.reset()
    while True:
        action = agent.predict(state)
        _, next_state, done = env.step(action)
        state = next_state
        if 0 == done:
            break

    env.padding()
    print("**********dataset: {} **********\n".format(data))
    print("total length : {}".format(len(env.aligned[0])))
    print("sp score     : {}".format(env.calc_score()))
    print("exact matched: {}".format(env.calc_exact_matched()))
    print("column score : {}".format(env.calc_exact_matched() / len(env.aligned[0])))
    print("alignment: \n{}".format(env.get_alignment()))
    print("********************************\n")


    report_file_name = os.path.join(config.report_path_DPAMSA, "{}.rpt".format(tag))

    for dataset_name in dataset.datasets:
        if not hasattr(dataset, dataset_name):
            continue
        seqs = getattr(dataset, dataset_name)

        env = Environment(seqs)
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
        report = "{}\n{}\n{}\n{}\n{}\n{}\n{}\n\n".format("NO: {}".format(dataset_name),
                                                            "AL: {}".format(len(env.aligned[0])),
                                                            "SP: {}".format(env.calc_score()),
                                                            "EM: {}".format(env.calc_exact_matched()),
                                                            "CS: {}".format(
                                                                env.calc_exact_matched() / len(env.aligned[0])),
                                                            "QTY: {}".format(len(env.aligned)),
                                                            "#\n{}".format(env.get_alignment()))

        with open(os.path.join(config.report_path_DPAMSA, "{}.rpt".format(tag)), 'a+') as report_file:
            report_file.write(report)

if __name__ == "__main__":
    main()

