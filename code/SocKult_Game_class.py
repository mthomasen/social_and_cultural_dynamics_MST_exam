
from SocKult_Card_deck_class import *

from SocKult_Player_class import *


import numpy as np
from scipy.stats import bernoulli

class Game:
    def __init__(self, cards, players):
        self.players = players
        self.player_cards = [[] for _ in players]
        self.dealer_cards = []
        self.game_card_deck = cards
        self.player_done = ['no' for _ in players]
        self.player_sum = [0 for _ in players]
        self.dealer_sum = 0
        self.game_ending = [0 for _ in players]

    def calculate_sum(self, cards):
        card_sum = 0
        ace_count = 0
        for card in cards:
            if card.isdigit():
                card_sum += int(card)
            elif card in ['J', 'Q', 'K']:
                card_sum += 10
            elif card == 'A':
                card_sum += 11
                ace_count += 1
        while card_sum > 21 and ace_count > 0:
            card_sum -= 10
            ace_count -= 1
        return card_sum

    def start(self):
        for i, player in enumerate(self.players):
            self.player_cards[i] = self.game_card_deck.deal_cards()
            player.receive_cards(self.player_cards[i])
        self.dealer_cards = self.game_card_deck.deal_cards()
        self.player_sum = [self.calculate_sum(cards) for cards in self.player_cards]
        self.dealer_sum = self.calculate_sum(self.dealer_cards)

    def player_move(self):
        for i, player in enumerate(self.players):
            while self.player_done[i] == 'no':
                player.choice_maker(self.player_sum[i])
                if player.choice == 0:
                    self.player_done[i] = 'yes'
                elif player.choice == 1:
                    self.player_cards[i].append(self.game_card_deck.draw_card())
                    self.player_sum[i] = self.calculate_sum(self.player_cards[i])
                    player.receive_cards(self.player_cards[i])

    def dealer_move(self):
        self.dealer_sum = self.calculate_sum(self.dealer_cards)
        while self.dealer_sum < 17:
            self.dealer_cards.append(self.game_card_deck.draw_card())
            self.dealer_sum = self.calculate_sum(self.dealer_cards)

    def end_game(self):
        for i, player in enumerate(self.players):
            if self.dealer_sum >= 17 and self.player_done[i] == 'yes':
                if self.player_sum[i] < 21:
                    if self.dealer_sum < self.player_sum[i] or self.dealer_sum > 21:
                        self.game_ending[i] = 1
                    elif self.dealer_sum == self.player_sum[i]:
                        self.game_ending[i] = 0
                    else:
                        self.game_ending[i] = -1
                elif self.player_sum[i] == 21:
                    if len(self.player_cards[i]) == 2 and (len(self.dealer_cards) > 2 or self.dealer_sum != 21):
                        self.game_ending[i] = 1.5
                    elif self.dealer_sum == 21:
                        self.game_ending[i] = 0
                    else:
                        self.game_ending[i] = 1
                else:
                    self.game_ending[i] = -1
