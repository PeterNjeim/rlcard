'''
    File name: maria/utils/tray.py
    Author: William Hale
    Date created: 11/28/2021
'''

class Tray(object):

    def __init__(self, dealer_id):
        self.dealer_id = dealer_id

    def __str__(self):
        return f'dealer_id={self.dealer_id}'
