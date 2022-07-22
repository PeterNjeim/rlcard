''' An example of evluating the trained models in RLCard
'''
import os
import argparse

import rlcard
from rlcard.agents import (
    DQNAgent,
    RandomAgent,
)
from rlcard.utils import (
    get_device,
    set_seed,
    tournament,
)

def load_model(model_path, env=None, position=None, device=None):
    if os.path.isfile(model_path):  # Torch model
        import torch
        agent = torch.load(model_path, map_location=device)
        agent.set_device(device)
    elif os.path.isdir(model_path):  # CFR model
        from rlcard.agents import CFRAgent
        agent = CFRAgent(env, model_path)
        agent.load()
    elif model_path == 'random':  # Random model
        from rlcard.agents import RandomAgent
        agent = RandomAgent(num_actions=env.num_actions)
    elif model_path == 'human':  # Human model
        from rlcard.agents.human_agents.maria_human_agent import HumanAgent
        agent = HumanAgent(num_actions=env.num_actions)
    else:  # A model in the model zoo
        from rlcard import models
        agent = models.load(model_path).agents[position]

    return agent

def evaluate(args):

    # Check whether gpu is available
    device = get_device()

    # Seed numpy, torch, random
    set_seed(args.seed)

    # Make the environment with seed
    env = rlcard.make(args.env, config={'seed': args.seed})

    # Load models
    agents = []
    for position, model_path in enumerate(args.models):
        agents.append(load_model(model_path, env, position, device))
    env.set_agents(agents)

    # Evaluate
    rewards = tournament(env, args.num_games)
    for position, reward in enumerate(rewards):
        print(position, args.models[position], reward)

    # Make environment
    print(">> Maria Defender Novice Rule Model")

    while (True):
        print(">> Start a new game")

        trajectories, payoffs = env.run(is_training=False)
        # If the human does not take the final action, we need to print other players action
        final_state = trajectories[0][-1]
        action_record = final_state['action_record']
        state = final_state
        for i in range(1, len(action_record)+1):
            if action_record[-i][0] == state['current_player']:
                break
        print('===============     Result     ===============')
        for i, payoff in enumerate(payoffs):
            if i == 0:
                print('You have {} points'.format(-payoff))
            print('Player {} has {} points'.format(i, -payoff))
        if payoffs[0] == max(payoffs):
            print('You win!')
        else:
            print('You lose!')
        print('')
        input("Press any key to continue...")

if __name__ == '__main__':
    parser = argparse.ArgumentParser("Evaluation example in RLCard")
    parser.add_argument(
        '--env',
        type=str,
        default='maria',
        choices=[
            'maria'
        ],
    )
    parser.add_argument(
        '--models',
        nargs='*',
        default=[
            'human',
            'experiments/maria_dqn_result/model.pth',
            'random',
            'random'
        ],
    )
    parser.add_argument(
        '--cuda',
        type=str,
        default='',
    )
    parser.add_argument(
        '--seed',
        type=int,
        default=42,
    )
    parser.add_argument(
        '--num_games',
        type=int,
        default=1,
    )

    args = parser.parse_args()

    os.environ["CUDA_VISIBLE_DEVICES"] = args.cuda
    evaluate(args)
