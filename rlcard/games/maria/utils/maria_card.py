'''
    File name: maria/utils/maria_card.py
    Author: William Hale
    Date created: 11/25/2021
'''

from typing import List
from termcolor import colored

from rlcard.games.base import Card


class MariaCard(Card):

    suits = ['C', 'D', 'H', 'S']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']

    @staticmethod
    def card(card_id: int):
        return _deck[card_id]

    @staticmethod
    def get_deck() -> List[Card]:
        return _deck.copy()

    def __init__(self, suit: str, rank: str):
        super().__init__(suit=suit, rank=rank)
        suit_index = MariaCard.suits.index(self.suit)
        rank_index = MariaCard.ranks.index(self.rank)
        self.card_id = 13 * suit_index + rank_index

    def __str__(self):
        return f'{self.rank}{self.suit}'

    def __repr__(self):
        return f'{self.rank}{self.suit}'

    @staticmethod
    def print_cards(cards):
        ''' Print out card in a nice form

        Args:
            card (str or list): The string form or a list of cards
        '''
        if isinstance(cards, str):
            cards = [cards]
        if isinstance(cards, int):
            cards = [_deck[cards]]
        for i, card in enumerate(cards):
            if isinstance(card, int):
                card = card(card)
            if card.suit == 'S':
                print(colored(card, 'white'), end='')
            elif card.suit == 'H':
                print(colored(card, 'red'), end='')
            elif card.suit == 'C':
                print(colored(card, 'grey'), end='')
            else:
                print(colored(card, 'magenta'), end='')
            if i < len(cards) - 1:
                print(', ', end='')

# deck is always in order from 2C, ... KC, AC, 2D, ... KD, AD, 2H, ... KH, AH, 2S, ... KS, AS
_deck = [MariaCard(suit=suit, rank=rank) for suit in MariaCard.suits for rank in MariaCard.ranks]  # want this to be read-only
