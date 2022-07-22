from rlcard.games.maria.utils.action_event import ActionEvent, PlayCardAction, TradeCardAction
from rlcard.games.maria.utils.maria_card import MariaCard

class HumanAgent(object):
    ''' A human agent for Maria. It can be used to play against trained models
    '''

    def __init__(self, num_actions):
        ''' Initilize the human agent

        Args:
            num_actions (int): the size of the ouput action space
        '''
        self.use_raw = True
        self.num_actions = num_actions

    @staticmethod
    def step(state):
        ''' Human agent will display the state and make decisions through interfaces

        Args:
            state (dict): A dictionary that represents the current state

        Returns:
            action (int): The action decided by human
        '''
        # print(state['raw_obs'])
        _print_state(state)
        action = int(input('>> Choose an action (integer): '))
        while action < 0 or action >= len(state['legal_actions']):
            print('Illegal action!')
            action = int(input('>> Re-choose an action (integer): '))
        if isinstance(ActionEvent.from_action_id(state['raw_legal_actions'][action]), PlayCardAction):
            return PlayCardAction(MariaCard.card(state['raw_legal_actions'][action]))
        elif isinstance(ActionEvent.from_action_id(state['raw_legal_actions'][action]), TradeCardAction):
            return TradeCardAction(MariaCard.card(state['raw_legal_actions'][action] % 52))

    def eval_step(self, state):
        ''' Predict the action given the curent state for evaluation. The same to step here.

        Args:
            state (numpy.array): an numpy array that represents the current state

        Returns:
            action (int): the action predicted (randomly chosen) by the random agent
        '''
        return self.step(state), {}

def _print_state(state):
    ''' Print out the state of a given player

    Args:
        player (int): Player id
    '''
    action_record = state['action_record']
    for i in range(1, len(action_record)+1):
        if action_record[-i][0] == state['current_player']:
            break
    print(f"Round {state['round_number']}")
    # for i, pile in enumerate(state['won_piles']):
    #     if i == 0:
    #         print('Your pile: {}'.format(pile))
    #     else:
    #         print('Player {}\'s pile: {}'.format(i, pile))
    if state['raw_legal_actions'][0] < 52:
        print('=============== Tray ===============')
        MariaCard.print_cards(state['played_cards'])
    elif state['raw_legal_actions'][0] >= 52:
        print('=============== Traded ===============')
        MariaCard.print_cards(state['won_piles'][state['current_player']])
    print('')
    print('\n============= Your Hand =============')
    MariaCard.print_cards(state['hand'])
    print('')
    print('====== Actions You Can Choose =======')
    for i, action in enumerate(state['raw_legal_actions']):
        print(str(i)+': ', end='')
        MariaCard.print_cards(action % 52)
        if i < len(state['raw_legal_actions']) - 1:
            print(', ', end='')
    print('\n')
