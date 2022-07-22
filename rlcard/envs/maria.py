'''
    File name: envs/maria.py
    Author: William Hale
    Date created: 11/26/2021
'''

import numpy as np
from collections import OrderedDict

from rlcard.envs import Env

from rlcard.games.maria import Game

from rlcard.games.maria.game import MariaGame
from rlcard.games.maria.utils.action_event import ActionEvent
from rlcard.games.maria.utils.maria_card import MariaCard
from rlcard.games.maria.utils.move import PlayCardMove, TradeCardMove

#   [] Why current_player_rep ?
#       Explanation here.
#
#   [] Note: hands_rep maintain the hands by N, E, S, W.
#
#   [] Note: trick_rep maintains the trick cards by N, E, S, W.
#      The trick leader can be deduced since play is in clockwise direction.


class MariaEnv(Env):
    ''' Maria Environment
    '''
    def __init__(self, config):
        self.name = 'maria'
        self.game = Game()
        super().__init__(config=config)
        self.mariaPayoffDelegate = DefaultMariaPayoffDelegate()
        self.mariaStateExtractor = DefaultMariaStateExtractor()
        state_shape_size = self.mariaStateExtractor.get_state_shape_size()
        self.state_shape = [[1, state_shape_size] for _ in range(self.num_players)]
        self.action_shape = [None for _ in range(self.num_players)]

    def get_payoffs(self):
        ''' Get the payoffs of players.

        Returns:
            (list): A list of payoffs for each player.
        '''
        return self.mariaPayoffDelegate.get_payoffs(game=self.game)

    def get_perfect_information(self):
        ''' Get the perfect information of the current state

        Returns:
            (dict): A dictionary of all the perfect information of the current state
        '''
        return self.game.round.get_perfect_information()

    def _extract_state(self, state):  # wch: don't use state 211126
        ''' Extract useful information from state for RL.

        Args:
            state (dict): The raw state

        Returns:
            (numpy.array): The extracted state
        '''
        extracted_state = self.mariaStateExtractor.extract_state(game=self.game)
        extracted_state['action_record'] = self.action_recorder
        extracted_state['raw_obs'] = state
        return extracted_state

    def _decode_action(self, action_id):
        ''' Decode Action id to the action in the game.

        Args:
            action_id (int): The id of the action

        Returns:
            (ActionEvent): The action that will be passed to the game engine.
        '''
        return ActionEvent.from_action_id(action_id=action_id)

    def _get_legal_actions(self):
        ''' Get all legal actions for current state.

        Returns:
            (list): A list of legal actions' id.
        '''
        raise NotImplementedError  # wch: not needed


class MariaPayoffDelegate(object):

    def get_payoffs(self, game: MariaGame):
        ''' Get the payoffs of players. Must be implemented in the child class.

        Returns:
            (list): A list of payoffs for each player.

        Note: Must be implemented in the child class.
        '''
        raise NotImplementedError


class DefaultMariaPayoffDelegate(MariaPayoffDelegate):

    def get_payoffs(self, game: MariaGame):
        ''' Get the payoffs of players.

        Returns:
            (list): A list of payoffs for each player.
        '''
        payoffs = []
        for player_id in range(4):
            payoff = game.won_points[player_id]
            payoffs.append(payoff)
        return np.array(payoffs)


class MariaStateExtractor(object):  # interface

    def get_state_shape_size(self) -> int:
        raise NotImplementedError

    def extract_state(self, game: MariaGame):
        ''' Extract useful information from state for RL. Must be implemented in the child class.

        Args:
            game (MariaGame): The game

        Returns:
            (numpy.array): The extracted state
        '''
        raise NotImplementedError

    @staticmethod
    def get_legal_actions(game: MariaGame):
        ''' Get all legal actions for current state.

        Returns:
            (OrderedDict): A OrderedDict of legal actions' id.
        '''
        legal_actions = game.judger.get_legal_actions()
        legal_actions_ids = {action_event.action_id: None for action_event in legal_actions}
        return OrderedDict(legal_actions_ids)


class DefaultMariaStateExtractor(MariaStateExtractor):

    def __init__(self):
        super().__init__()

    def get_state_shape_size(self) -> int:
        state_shape_size = 0
        state_shape_size += 4 * 52  # hands_rep_size
        state_shape_size += 4 * 52  # trick_rep_size
        state_shape_size += 4  # dealer_rep_size
        state_shape_size += 4  # current_player_rep_size
        return state_shape_size

    def extract_state(self, game: MariaGame):
        ''' Extract useful information from state for RL.

        Args:
            game (MariaGame): The game

        Returns:
            (numpy.array): The extracted state
        '''
        extracted_state = {}
        legal_actions: OrderedDict = self.get_legal_actions(game=game)
        raw_legal_actions = list(legal_actions.keys())
        current_player = game.round.get_current_player()
        current_player_id = current_player.player_id

        # construct hands_rep of hands of players
        hands_rep = [np.zeros(52, dtype=int) for _ in range(4)]
        if not game.round.is_over():
            for card in game.round.players[current_player_id].hand:
                hands_rep[current_player_id][card.card_id] = 1

        # construct trick_pile_rep
        trick_pile_rep = [np.zeros(52, dtype=int) for _ in range(4)]
        if not game.round.is_over():
            trick_moves = game.round.get_trick_moves()
            for move in trick_moves:
                player = move.player
                card = move.card
                trick_pile_rep[player.player_id][card.card_id] = 1

        # construct dealer_rep
        dealer_rep = np.zeros(4, dtype=int)
        dealer_rep[game.round.tray.dealer_id] = 1

        # construct current_player_rep
        current_player_rep = np.zeros(4, dtype=int)
        current_player_rep[current_player_id] = 1

        rep = []
        rep += hands_rep
        rep += trick_pile_rep
        rep.append(dealer_rep)
        rep.append(current_player_rep)

        obs = np.concatenate(rep)
        extracted_state['hand'] = game.round.players[current_player_id].hand
        extracted_state['played_cards'] = *map(lambda e: e.card, game.round.get_trick_moves()),
        extracted_state['num_players'] = game.num_players
        extracted_state['obs'] = obs
        extracted_state['legal_actions'] = legal_actions
        extracted_state['current_player'] = current_player_id
        extracted_state['raw_legal_actions'] = raw_legal_actions
        extracted_state['round_number'] = game.round_number
        extracted_state['won_piles'] = game.round.won_pile
        extracted_state['trade_piles'] = game.round.trade_pile

        return extracted_state
