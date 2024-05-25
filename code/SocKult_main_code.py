import os
from SocKult_Player_class import Player
from SocKult_Table_class import Table

# Change to your own path
os.chdir("D:\\AU_Cog_Sci\\socKult\\social_and_cultural_dynamics_MST_exam")

player_1 = Player('player_1', 1000)
player_2 = Player('player_2', 1000)
player_3 = Player('player_3', 1000)

player_list = [player_1, player_2, player_3]

number_of_tables = range(1, 11)

for i in number_of_tables:
    new_table = Table(50, 8, player_list, f'table{i}')
    new_table.play_games()
    new_table.make_dataframe()
    new_table.save_dataframe()
