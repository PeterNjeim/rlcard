'''
    File name: maria/round.py
    Author: William Hale
    Date created: 11/25/2021
'''

from typing import List

from rlcard.games.maria.utils.maria_card import MariaCard

from .dealer import MariaDealer
from .player import MariaPlayer

from .utils.action_event import PlayCardAction, TradeCardAction
from .utils.move import MariaMove, DealHandMove, PlayCardMove, TradeCardMove
from .utils.tray import Tray

class MariaRound:

    @property
    def dealer_id(self) -> int:
        return self.tray.dealer_id

    @property
    def round_phase(self):
        if self.is_over():
            result = 'round over'
        else:
            result = 'play card'
        return result

    def __init__(self, num_players: int, round_number: int, dealer_id: int, np_random):
        ''' Initialize the round class

            The round class maintains the following instances:
                1) dealer: the dealer of the round; dealer has trick_pile
                2) players: the players in the round; each player has his own hand_pile
                3) current_player_id: the id of the current player who has the move
                4) play_card_count: count of PlayCardMoves
                5) move_sheet: history of the moves of the players (including the deal_hand_move)

            The round class maintains a list of moves made by the players in self.move_sheet.
            move_sheet is similar to a chess score sheet.
            I didn't want to call it a score_sheet since it is not keeping score.
            I could have called move_sheet just moves, but that might conflict with the name moves used elsewhere.
            I settled on the longer name "move_sheet" to indicate that it is the official list of moves being made.

        Args:
            num_players: int
            np_random
        '''
        if round_number == 1:
            tray = Tray(np_random.choice([0, 1, 2, 3]))
        else:
            tray = Tray(dealer_id)
        dealer_id = tray.dealer_id
        self.tray = tray
        self.np_random = np_random
        self.dealer: MariaDealer = MariaDealer(self.np_random)
        self.players: List[MariaPlayer] = []
        for player_id in range(num_players):
            self.players.append(MariaPlayer(player_id=player_id))
        self.play_card_count: int = 0
        self.won_pile: list[list[MariaCard]] = [[], [], [], []]
        self.trade_pile: list[list[MariaCard]] = [[], [], [], []]
        self.move_sheet: List[MariaMove] = []
        self.move_sheet.append(DealHandMove(dealer=self.players[dealer_id], shuffled_deck=self.dealer.shuffled_deck))
        self.current_player_id: int = dealer_id

    def is_over(self) -> bool:
        ''' Return whether the current round is over
        '''
        is_over = True
        for player in self.players:
            if player.hand:
                is_over = False
                break
        return is_over

    def is_start(self) -> bool:
        ''' Return whether the current round just started
        '''
        is_start = False
        for pile in self.trade_pile:
            if len(pile) < 3:
                is_start = True
                break
        return is_start

    def is_done_trading(self) -> bool:
        ''' Return whether trading has finished
        '''
        is_done_trading = True
        for pile in self.trade_pile:
            if len(pile) < 3:
                is_done_trading = False
                break
        return is_done_trading

    def is_first_trick(self) -> bool:
        ''' Return whether no tricks have been won yet
        '''
        is_first_trick = True
        for pile in self.won_pile:
            if len(pile) > 0:
                is_first_trick = False
                break
        return is_first_trick

    def get_current_player(self) -> MariaPlayer or None:
        current_player_id = self.current_player_id
        return None if current_player_id is None else self.players[current_player_id]

    def get_trick_moves(self) -> List[PlayCardMove]:
        trick_moves: List[PlayCardMove] = []
        if self.play_card_count > 0:
            trick_pile_count = self.play_card_count % 4
            if trick_pile_count == 0:
                trick_pile_count = 4  # wch: note this
            for move in self.move_sheet[-trick_pile_count:]:
                if isinstance(move, PlayCardMove):
                    trick_moves.append(move)
            if len(trick_moves) != trick_pile_count:
                raise Exception(f'get_trick_moves: count of trick_moves={[str(move.card) for move in trick_moves]} does not equal {trick_pile_count}')
        return trick_moves

    def play_card(self, action: PlayCardAction):
        # when current_player takes PlayCardAction step, the move is recorded and executed
        current_player = self.players[self.current_player_id]
        self.move_sheet.append(PlayCardMove(current_player, action))
        card = action.card
        current_player.remove_card_from_hand(card=card)
        self.play_card_count += 1
        # update current_player_id
        trick_moves = self.get_trick_moves()
        if len(trick_moves) == 4:
            winning_card = trick_moves[0].card
            trick_winner = trick_moves[0].player
            trick_points = 0
            for move in trick_moves[1:]:
                trick_card = move.card
                trick_player = move.player
                if trick_card.suit == 'H':
                    trick_points -= 1
                elif trick_card.rank == 'Q' and trick_card.suit == 'S':
                    trick_points -= 13
                if trick_card.suit == winning_card.suit:
                    if trick_card.card_id > winning_card.card_id:
                        winning_card = trick_card
                        trick_winner = trick_player
            self.current_player_id = trick_winner.player_id
            self.won_pile[trick_winner.player_id].extend([*map(lambda e: e.card, trick_moves)])
        else:
            self.current_player_id = (self.current_player_id + 1) % 4

    def trade_card(self, action: TradeCardAction):
        # when current_player takes TradeCardAction step, the move is recorded and executed
        current_player = self.players[self.current_player_id]
        self.move_sheet.append(TradeCardMove(current_player, action))
        card = action.card
        current_player.remove_card_from_hand(card=card)
        tradee_id = (self.current_player_id + 1) % 4
        self.trade_pile[tradee_id].append(card)
        if len(self.trade_pile[tradee_id]) == 3:
            self.current_player_id = tradee_id

        if self.is_done_trading():
            for i, pile in enumerate(self.trade_pile):
                for card in pile:
                    self.players[i].add_card_to_hand(card=card)
            for player in self.players:
                player.order_cards()
                if MariaCard('C', '2') in player.hand:
                    self.current_player_id = player.player_id
                    break


    def get_perfect_information(self):
        state = {}
        trick_moves = [None, None, None, None]
        for trick_move in self.get_trick_moves():
            trick_moves[trick_move.player.player_id] = trick_move.card
        state['move_count'] = len(self.move_sheet)
        state['tray'] = self.tray
        state['current_player_id'] = self.current_player_id
        state['round_phase'] = self.round_phase
        state['hands'] = [player.hand for player in self.players]
        state['trick_moves'] = trick_moves
        state['round_number'] = self.round_number
        state['won_piles'] = self.won_pile
        state['trade_piles'] = self.trade_pile
        return state

    def print_scene(self):
        print(f'===== Round: {self.round_number} move: {len(self.move_sheet)} player: {self.players[self.current_player_id]} phase: {self.round_phase} =====')
        print(f'dealer={self.players[self.tray.dealer_id]}')
        for player in self.players:
            print(f'{player}: {[str(card) for card in player.hand]}')
        trick_pile = ['None', 'None', 'None', 'None']
        for trick_move in self.get_trick_moves():
            trick_pile[trick_move.player.player_id] = trick_move.card
        print(f'trick_pile: {[str(card) for card in trick_pile]}')
