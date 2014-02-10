__author__ = 'dark-wizard'

import GameMechanics


class GameInfo:
    all_active_data = list()                    # active data to be rendered onstage, from every player
    player_private_data = list()
    turn_number = 1
    active_player = 0
    window_manager = None
    unitGrid = None
    worldGrid = None
    game_core = None
    ai = None

    time_passed = 0

    selected_unit = None
    selected_town = None
    main_castle = None

    def __init__(self):
        pass

    @staticmethod
    def set_defaults():
        for x in range(GameInfo.game_core.total_players):
            GameInfo.player_private_data.append(dict())
        #print GameInfo.player_private_data