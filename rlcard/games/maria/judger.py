'''
    File name: maria/judger.py
    Author: William Hale
    Date created: 11/25/2021
'''

from typing import List

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .game import MariaGame

from .utils.action_event import ActionEvent, PlayCardAction, TradeCardAction
from .utils.maria_card import MariaCard

class MariaJudger:

    '''
        Judger decides legal actions for current player
    '''

    def __init__(self, game: 'MariaGame'):
        ''' Initialize the class MariaJudger
        :param game: MariaGame
        '''
        self.game: MariaGame = game

    def get_legal_actions(self) -> List[ActionEvent]:
        """
        :return: List[ActionEvent] of legal actions
        """
        legal_actions: List[ActionEvent] = []
        if not self.game.round.is_over():
            current_player = self.game.round.get_current_player()
            hand = self.game.round.players[current_player.player_id].hand
            if self.game.round.is_start():
                for card in hand:
                    action = TradeCardAction(card=card)
                    legal_actions.append(action)
            else:
                trick_moves = self.game.round.get_trick_moves()
                is_hearts_broken = False
                legal_cards = hand
                if trick_moves and len(trick_moves) < 4:
                    led_card: MariaCard = trick_moves[0].card
                    cards_of_led_suit = [card for card in hand if card.suit == led_card.suit]
                    if cards_of_led_suit:
                        legal_cards = cards_of_led_suit
                for pile in self.game.round.won_pile:
                    if [i for i in pile if i in [MariaCard.card(i) for i in range(26, 39)]]:
                        is_hearts_broken = True
                        break
                if not is_hearts_broken and len(trick_moves) == 4:
                    if not [i for i in hand if i not in [MariaCard.card(i) for i in range(26, 39)]]:
                        legal_cards = hand
                    else:
                        legal_cards = [i for i in hand if i not in [MariaCard.card(i) for i in range(26, 39)]]
                if self.game.round.is_first_trick() and self.game.round.play_card_count == 0:
                    legal_cards = [MariaCard('C', '2')]
                for card in legal_cards:
                    action = PlayCardAction(card=card)
                    legal_actions.append(action)
        return legal_actions
