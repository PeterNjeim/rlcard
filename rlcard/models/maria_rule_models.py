'''
    File name: models/maria_rule_models.py
    Author: William Hale
    Date created: 11/27/2021

    Maria rule models
'''

import numpy as np
import rlcard

from rlcard.models.model import Model

class MariaDefenderNoviceRuleAgent(object):
    def __init__(self):
        self.use_raw = False

    @staticmethod
    def step(state) -> int:
        ''' Predict the action given the current state.
            Defender Novice strategy:
                Case during play card:
                    Choose a random action.

        Args:
            state (numpy.array): an numpy array that represents the current state

        Returns:
            action_id (int): the action_id predicted
        '''
        legal_action_ids = state['raw_legal_actions']
        return np.random.choice(legal_action_ids)

    def eval_step(self, state):
        ''' Predict the action given the current state for evaluation.
            Since the agents is not trained, this function is equivalent to step function.

        Args:
            state (numpy.array): an numpy array that represents the current state

        Returns:
            action_id (int): the action_id predicted by the agent
            probabilities (list): The list of action probabilities
        '''
        probabilities = []
        return self.step(state), probabilities

class MariaDefenderNoviceRuleModel(Model):
    ''' Maria Defender Novice Rule Model
    '''

    def __init__(self):
        ''' Load pretrained model
        '''
        env = rlcard.make('maria')

        rule_agent = MariaDefenderNoviceRuleAgent()
        self.rule_agents = [rule_agent for _ in range(env.num_players)]

    @property
    def agents(self):
        ''' Get a list of agents for each position in a the game

        Returns:
            agents (list): A list of agents

        Note: Each agent should be just like RL agent with step and eval_step
              functioning well.
        '''
        return self.rule_agents

    @property
    def use_raw(self):
        ''' Indicate whether use raw state and action

        Returns:
            use_raw (boolean): True if using raw state and action
        '''
        return True
