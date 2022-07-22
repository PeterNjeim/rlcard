'''
    File name: maria/utils/move.py
    Author: William Hale
    Date created: 11/25/2021
'''

#
#   These classes are used to keep a move_sheet history of the moves in a round.
#

from typing import List

from .action_event import ActionEvent, PlayCardAction, TradeCardAction
from .maria_card import MariaCard

from ..player import MariaPlayer


class MariaMove(object):  # Interface
    pass

class PlayerMove(MariaMove):  # Interface

    def __init__(self, player: MariaPlayer, action: ActionEvent):
        super().__init__()
        self.player = player
        self.action = action

class DealHandMove(MariaMove):

    def __init__(self, dealer: MariaPlayer, shuffled_deck: List[MariaCard]):
        super().__init__()
        self.dealer = dealer
        self.shuffled_deck = shuffled_deck

    def __str__(self):
        shuffled_deck_text = " ".join([str(card) for card in self.shuffled_deck])
        return f'{self.dealer} deal shuffled_deck=[{shuffled_deck_text}]'

class PlayCardMove(PlayerMove):

    def __init__(self, player: MariaPlayer, action: PlayCardAction):
        super().__init__(player=player, action=action)
        self.action = action  # Note: keep type as PlayCardAction rather than ActionEvent

    @property
    def card(self):
        return self.action.card

    def __str__(self):
        return f'{self.player} plays {self.action}'

class TradeCardMove(PlayerMove):

    def __init__(self, player: MariaPlayer, action: TradeCardAction):
        super().__init__(player=player, action=action)
        self.action = action  # Note: keep type as TradeCardAction rather than ActionEvent

    @property
    def card(self):
        return self.action.card

    def __str__(self):
        return f'{self.player} plays {self.action}'
