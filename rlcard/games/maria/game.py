'''
    File name: maria/game.py
    Author: William Hale
    Date created: 11/25/2021
'''

from copy import deepcopy
from typing import List

import numpy as np

from rlcard.games.maria.utils.maria_card import MariaCard

from .judger import MariaJudger
from .round import MariaRound
from .utils.action_event import ActionEvent, PlayCardAction, TradeCardAction


class MariaGame:
    ''' Game class. This class will interact with outer environment.
    '''

    def __init__(self, allow_step_back=False):
        '''Initialize the class MariaGame
        '''
        self.allow_step_back: bool = allow_step_back
        self.np_random = np.random.RandomState()
        self.judger: MariaJudger = MariaJudger(game=self)
        self.actions: List[ActionEvent] = []  # must reset in init_game
        self.round: MariaRound or None = None  # must reset in init_game
        self.num_players: int = 4
        self.won_points = [0, 0, 0, 0]

    def init_game(self):
        ''' Initialize all characters in the game and starts a round
        '''
        self.actions: List[ActionEvent] = []
        self.won_points = [0, 0, 0, 0]
        self.round_number = 1
        self.round = MariaRound(num_players=self.num_players, round_number=self.round_number, dealer_id=0, np_random=self.np_random)
        for player_id in range(4):
            player = self.round.players[player_id]
            self.round.dealer.deal_cards(player=player, num=13)
            player.order_cards()
        first_player = self.round.current_player_id
        for player in self.round.players:
            if MariaCard('C', '2') in player.hand:
                first_player = player.player_id
                break
        current_player_id = first_player
        self.round.current_player_id = first_player
        self.history = []
        state = self.get_state(player_id=current_player_id)
        return state, current_player_id

    def init_round(self):
        ''' Re-initialize all characters in the game and starts another round
        '''
        self.actions: List[ActionEvent] = []
        self.round = MariaRound(num_players=self.num_players, round_number=self.round_number, dealer_id=((self.round.dealer_id + 1) % 4), np_random=self.np_random)
        for player_id in range(4):
            player = self.round.players[player_id]
            self.round.dealer.deal_cards(player=player, num=13)
            player.order_cards()
        first_player = self.round.current_player_id
        for player in self.round.players:
            if MariaCard('C', '2') in player.hand:
                first_player = player.player_id
                break
        current_player_id = first_player
        self.round.current_player_id = first_player
        state = self.get_state(player_id=current_player_id)
        return state, current_player_id

    def step(self, action: ActionEvent):
        ''' Perform game action and return next player number, and the state for next player
        '''

        if self.allow_step_back:
            sb_actions = deepcopy(self.actions)
            sb_won_points = deepcopy(self.won_points)
            sb_round_number = deepcopy(self.round_number)
            sb_round = deepcopy(self.round)
            sb_round_current_player_id = deepcopy(self.round.current_player_id)
            self.history.append((sb_actions, sb_won_points, sb_round_number, sb_round, sb_round_current_player_id))

        if isinstance(action, PlayCardAction):
            self.round.play_card(action=action)
        elif isinstance(action, TradeCardAction):
            self.round.trade_card(action=action)
        else:
            raise Exception(f'Unknown step action={action}')
        self.actions.append(action)
        if self.round.is_over():
            for player in self.round.players:
                for card in self.round.won_pile[player.player_id]:
                    if card.suit == 'H':
                        self.won_points[player.player_id] -= 1
                    elif card.suit == 'S' and card.rank == 'Q':
                        self.won_points[player.player_id] -= 13
                if self.won_points[player.player_id] == -26:
                    if len(self.round.won_pile[player.player_id]) == 13:
                        for player_id in self.round.players:
                            if player_id.player_id == player.player_id:
                                self.won_points[player_id.player_id] += 26
                            else:
                                self.won_points[player_id.player_id] -= 52
                    else:
                        if max(self.won_points) >= -25:
                            self.won_points[player.player_id] += 52
                        else:
                            for player_id in self.round.players:
                                if player_id.player_id == player.player_id:
                                    self.won_points[player_id.player_id] += 26
                                else:
                                    self.won_points[player_id.player_id] -= 26
            if not self.is_over():
                self.round_number += 1
                return self.init_round()
        next_player_id = self.round.current_player_id
        next_state = self.get_state(player_id=next_player_id)
        return next_state, next_player_id

    def step_back(self):
        ''' Return to the previous state of the game

        Returns:
            (bool): True if the game steps back successfully
        '''
        if not self.history:
            return False
        self.actions, self.won_points, self.round_number, self.round, self.round.current_player_id = self.history.pop()
        return True

    def get_num_players(self) -> int:
        ''' Return the number of players in the game
        '''
        return self.num_players

    @staticmethod
    def get_num_actions() -> int:
        ''' Return the number of possible actions in the game
        '''
        return ActionEvent.get_num_actions()

    def get_player_id(self):
        ''' Return the current player that will take actions soon
        '''
        return self.round.current_player_id

    def is_over(self) -> bool:
        ''' Return whether the current game is over
        '''
        is_over = False
        for player in self.round.players:
            if self.won_points[player.player_id] <= -51:
                is_over = True
                break
        return is_over

    def get_state(self, player_id: int):  # wch: not really used
        ''' Get player's state

        Return:
            state (dict): The information of the state
        '''
        state = {}
        state['player_id'] = player_id
        state['current_player_id'] = self.round.current_player_id
        state['hand'] = self.round.players[player_id].hand
        return state
