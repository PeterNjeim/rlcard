'''
    File name: maria/utils/action_event.py
    Author: William Hale
    Date created: 11/25/2021
'''

from .maria_card import MariaCard

# ====================================
# Action_ids:
#       0 to 51 -> play_card_action_id
#       52 to 103 -> action_card_action_id
# ====================================


class ActionEvent(object):  # Interface

    first_play_card_action_id = 0
    first_trade_card_action_id = 52

    def __init__(self, action_id: int):
        self.action_id = action_id

    def __eq__(self, other):
        result = False
        if isinstance(other, ActionEvent):
            result = self.action_id == other.action_id
        return result

    @staticmethod
    def from_action_id(action_id: int):
        if ActionEvent.first_play_card_action_id <= action_id < ActionEvent.first_play_card_action_id + 52:
            card_id = action_id - ActionEvent.first_play_card_action_id
            card = MariaCard.card(card_id=card_id)
            return PlayCardAction(card=card)
        elif ActionEvent.first_trade_card_action_id <= action_id < ActionEvent.first_trade_card_action_id + 52:
            card_id = action_id - ActionEvent.first_trade_card_action_id
            card = MariaCard.card(card_id=card_id)
            return TradeCardAction(card=card)
        else:
            raise Exception(f'ActionEvent from_action_id: invalid action_id={action_id}')

    @staticmethod
    def get_num_actions():
        ''' Return the number of possible actions in the game
        '''
        return 104  # 52 play_card, 52 trade_card

class PlayCardAction(ActionEvent):

    def __init__(self, card: MariaCard):
        play_card_action_id = ActionEvent.first_play_card_action_id + card.card_id
        super().__init__(action_id=play_card_action_id)
        self.card: MariaCard = card

    def __str__(self):
        return f"{self.card}"

    def __repr__(self):
        return f"{self.card}"

class TradeCardAction(ActionEvent):

    def __init__(self, card: MariaCard):
        trade_card_action_id = ActionEvent.first_trade_card_action_id + card.card_id
        super().__init__(action_id=trade_card_action_id)
        self.card: MariaCard = card

    def __str__(self):
        return f"{self.card}"

    def __repr__(self):
        return f"{self.card}"
