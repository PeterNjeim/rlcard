'''
    File name: maria/player.py
    Author: William Hale
    Date created: 11/25/2021
'''

from typing import List

from .utils.maria_card import MariaCard

class MariaPlayer:

    def __init__(self, player_id: int):
        ''' Initialize a MariaPlayer player class

        Args:
            player_id (int): id for the player
        '''
        if player_id < 0 or player_id > 3:
            raise Exception(f'MariaPlayer has invalid player_id: {player_id}')
        self.player_id: int = player_id
        self.hand: List[MariaCard] = []

    def remove_card_from_hand(self, card: MariaCard):
        self.hand.remove(card)

    def add_card_to_hand(self, card: MariaCard):
        self.hand.append(card)

    def order_cards(self):
        self.hand.sort(key=lambda e:e.card_id)

    def __str__(self):
        return ['N', 'E', 'S', 'W'][self.player_id]
