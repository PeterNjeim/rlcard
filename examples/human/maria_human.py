''' A toy example of playing against rule-based bot on MARIA
'''

import rlcard
from rlcard import models
from rlcard.agents.human_agents.maria_human_agent import HumanAgent
from rlcard.agents import RandomAgent

# Make environment
env = rlcard.make('maria')
human_agent = HumanAgent(env.num_actions)
cfr_agent = models.load('maria-defender-novice-rule').agents[1]
random_agent = RandomAgent(num_actions=env.num_actions)
random_agent = RandomAgent(num_actions=env.num_actions)
env.set_agents([
    human_agent,
    cfr_agent,
    random_agent,
    random_agent
])

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
