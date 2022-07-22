'''
    File name: maria/utils/utils.py
    Author: William Hale
    Date created: 11/26/2021
'''

from typing import List

import numpy as np

from .maria_card import MariaCard

def encode_cards(cards: List[MariaCard]) -> np.ndarray:  # Note: not used ??
    plane = np.zeros(52, dtype=int)
    for card in cards:
        plane[card.card_id] = 1
    return plane
