import matplotlib.pyplot as plt
import os
import pytz
from datetime import datetime
import pandas as pd
from SocKult_Game_class import Game
from SocKult_Card_deck_class import CardDeck
from SocKult_Player_class import Player

class Table:
    def __init__(self, number_of_games, number_of_decks, players, table_name):
        self.number_of_games = number_of_games
        self.number_of_decks = number_of_decks
        self.players = players
        self.games_played = 0
        self.game = None
        self.wealth_stats = {player: [player.wealth] for player in players}
        self.stats_game_ending = {player: [0] for player in players}
        self.stats_games_played = [0]
        self.stats_bet = {player: [0] for player in players}
        self.stats_risk_factor = {player: [player.risk_factor] for player in players}
        self.stats_player_cards = {player: [[]] for player in players}
        self.stats_fraction_to_bet = {player: [player.fraction_to_bet] for player in players}
        self.table_name = table_name
        self.dataframe = None
        self.card_deck = CardDeck(self.number_of_decks)

    def update_wealth(self, player):
        player.wealth += (player.bet * self.game.game_ending[self.players.index(player)])

    def table_statistics(self, player):
        self.wealth_stats[player].append(player.wealth)
        self.stats_game_ending[player].append(self.game.game_ending[self.players.index(player)])
        self.stats_bet[player].append(player.bet)
        self.stats_risk_factor[player].append(player.risk_factor)
        self.stats_player_cards[player].append(self.game.player_cards[self.players.index(player)])
        self.stats_fraction_to_bet[player].append(player.fraction_to_bet)

    def play_games(self):
        while self.games_played < self.number_of_games:
            if self.games_played % 10 == 0:
                self.card_deck = CardDeck(self.number_of_decks)
                self.card_deck.create_deck()
            for player in self.players:
                player.adjust_bet()
            self.game = Game(self.card_deck, self.players)
            self.game.start()
            self.game.player_move()
            self.game.dealer_move()
            self.game.end_game()
            for player in self.players:
                self.update_wealth(player)
                self.table_statistics(player)
            self.games_played += 1
            self.stats_games_played.append(self.games_played)

    def make_dataframe(self):
        data = []
        for player in self.players:
            for game_num in range(len(self.stats_games_played)):
                data.append({
                    'player_name': player.name,
                    'table_name': self.table_name
                    'player_risk_factor': round(self.stats_risk_factor[player][game_num], 2),
                    'player_cards': self.stats_player_cards[player][game_num],
                    'wealth': round(self.wealth_stats[player][game_num], 2),
                    'game_ending': round(self.stats_game_ending[player][game_num], 2),
                    'games_played': self.stats_games_played[game_num],
                    'fraction_to_bet': round(self.stats_fraction_to_bet[player][game_num], 4),
                    'player_bet': round(self.stats_bet[player][game_num], 2)
                })
        self.dataframe = pd.DataFrame(data)

    def save_dataframe(self):
        time_stamp = datetime.now(pytz.timezone('Europe/Copenhagen'))
        if not os.path.exists('logfiles'):
            os.makedirs('logfiles')
        logfile_name = f'logfiles/logfile_{self.table_name}_{time_stamp.hour}_{time_stamp.minute}_{time_stamp.second}.csv'
        self.dataframe.to_csv(logfile_name, index=False)
