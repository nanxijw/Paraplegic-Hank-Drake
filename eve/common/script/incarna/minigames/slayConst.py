import util
SOUND_KILL_PEASANT = 'slay_kill_soldier_play'
SOUND_KILL_SPEARMAN = 'slay_kill_small_bot_play'
SOUND_KILL_KNIGHT = 'slay_kill_big_bot_play'
SOUND_KILL_TOWN = 'slay_kill_bunker_play'
SOUND_KILL_PINEFOREST = 'slay_kill_drone1_play'
SOUND_KILL_PALMFOREST = 'slay_kill_drone2_play'
SOUND_MOVE_PEASANT = 'slay_move_soldier_play'
SOUND_MOVE_SPEARMAN = 'slay_move_small_bot_play'
SOUND_MOVE_KNIGHT = 'slay_move_big_bot_play'
SOUND_MOVE_BARON = 'slay_move_gunship_play'
SOUND_NOTIFY_YOUR_TURN = 'slay_notify_play'
SOUND_UPGRADE_UNIT = 'slay_upgrade_play'
SOUND_PLAYER_WON = 'slay_victory_play'
BASIC_UNIT_BUY_COST = 10
GAME_RESTART = 110
IDEAL_START_REGION_SIZE = 4
NUM_HEXAGON_SIDES = 6
PLAYER_LEFT = 100
IN_GAME_MESSAGE = 103
NEXT_TURN = 104
READY_PLAY = 105
READY_WAIT = 106
REFRESH_DATA = 107
LEAVE_GAME = 108
CLEAR_TABLE = 109
ACCESS_DENY_SETTING_UP = 111
ACCESS_GRANT_WAITING = 112
ACCESS_GRANT_WELCOMEBACK = 113
ACCESS_GRANT_STARTING_NOW = 114
GAME_INIT = 115
GAMEMASTER_INIT = 116
GAMEMASTER_SETTINGS = 117
GAME_WON = 118
PLAYER_LOST = 119
INFORM_PLAYER_LEFT = 120
INFORM_PLAYER_SURRENDERED = 121
KICKOUT_DUE_TO_SETUP_INACTIVITY = 122
GAME_WON_BY_AI = 123
LEAVE_GAME_PROCESSED = 124
SLOT_POSITION_UPDATE = 125
READY_WAIT_FOR_AI = 126
UPDATE_AVAILABLE_COLORS = 127
READY_WAIT_AI = 128
PLACE_UNIT = 130
PLACE_CASTLE = 131
MOVE_UNIT = 132
KILL_UNIT = 133
AREAS_MERGED = 134
AREA_INFO = 135
UNDO = 136
ROUND_END = 138
ACCEPTING_PLAYERS = 139
GAME_CANCELED = 140
MEMBERS = 141
RESET_TIMER = 142
INQUIRE_PLACE_RUNNING_BET = 143
PLACE_RUNNING_BET = 144
RUNNING_BET_SETUP = 145
CANCEL_RUNNING_BET = 146
REQUEST_RUNNING_BET = 147
ACCEPT_RUNNING_BET_CHALLENGE = 148
AREA_INFO_AGGREGATED = 149
SPECTATE_MODE = 150
GAME_CLOSED = 151
LIGHT_STATE_UPDATE = 152
ACTIVATE_LIGHT = 153
MINIGAME_SYSTEM_SHUTDOWN = 154
CHAT_CHANNEL_JOIN = 155
CHAT_CHANNEL_LEAVE = 156
KICKOUT_DUE_TO_INACTIVITY = 157
GENERIC_MESSAGE = 158
OCCUPY_DEAD = 0
OCCUPY_NONE = 1
OCCUPY_PINEFOREST = 2
OCCUPY_PALMFOREST = 3
OCCUPY_PEASANT = 4
OCCUPY_TOWN = 5
OCCUPY_SPEARMAN = 6
OCCUPY_CASTLE = 7
OCCUPY_KNIGHT = 8
OCCUPY_BARON = 9
AI_MODE_DEFENSIVE = 200
AI_MODE_EXPANSIONIST = 201
AI_MODE_AGGRESSIVE = 201
BUY_COST_PEASANT = 10
BUY_COST_CASTLE = 15
SUPPORT_COST_PEASANT = 2
SUPPORT_COST_SPEARMAN = 6
SUPPORT_COST_KNIGHT = 18
SUPPORT_COST_BARON = 54
SLAY_MIN_HEIGHT = 10
SLAY_MIN_WIDTH = 10
MAX_GAMEWORLD_HEIGHT = 18
MAX_GAMEWORLD_WIDTH = 18
TILE_SCALE = 5.8
TOWN_SCALE = 2.0
FOREST_SCALE = 1.2
PEASANT_SCALE = 1.5
KNIGHT_SCALE = 2.6
BARON_SCALE = 2.0
SPEARMAN_SCALE = 1.6
RIP_SCALE = 3.0
CASTLE_SCALE = 2.0
BARON_Y_OFFSET = 0.04
MAP_Y_LOCATION_SCALE = 0.09825
MAP_X_LOCATION_SCALE = 0.0839
UNITS_Y_OFFSET = 0.051
TOWN_Y_OFFSET = 0.047
HIGHLIGH_TILESCALE = 5.5
HIGHLIGHT_Y_SCALE = 6.0
HEXAGONMAP_ODDROW_OFFSET = 0.0495
TILE_SLIGHT_HOVER_OFFSET = 0.0001
START_LOC_X_TABLE_SHIFT = 0.885
START_LOC_Y_TABLE_SHIFT = 0.11
START_LOC_Z_TABLE_SHIFT = 0.665
MAP_TYPE_RANDOM = 1108
COLOR_1 = 500
COLOR_2 = 501
COLOR_3 = 502
COLOR_4 = 503
COLOR_5 = 504
COLOR_6 = 505
COLOR_7 = 506
COLOR_NONE = 507
UNUSED_SLOT = 508
SLAY_UNIT_SET_STANDARD = 600
slayUnitSetMapping = {SLAY_UNIT_SET_STANDARD: util.KeyVal(hexagon=10485, dead=10491, pineForest=10493, palmForest=10489, peasant=10490, townOpen=10486, townClosed=10487, spearman=10492, castle=10484, knight=10488, baron=10483)}
mapIDs = [19,
 1,
 3,
 7,
 9,
 10,
 18,
 24,
 25,
 26,
 28,
 37,
 43,
 45,
 52,
 55,
 58,
 65,
 69,
 75,
 85]
SLAYMSG_NOT_ENOUGH_MONEY_FOR_BETTING = 5000
SLAYMSG_ERROR_STARTING_BETTING_ENTRY = 5001
SLAYMSG_BETTING_IS_DISABLED = 5002
SLAYMSG_GAME_STARTING = 5003
SLAYMSG_YOUR_TURN = 5004
SLAYMSG_NOT_YOUR_TURN = 5005
SLAYMSG_CANT_UNDO_FURTHER = 5006
SLAYMSG_MUST_SELECT_AREA = 5007
SLAYMSG_REGION_TOO_POOR = 5008
SLAYMSG_CANT_PLACE_UNIT_THERE = 5009
SLAYMSG_MUST_PLACE_UNIT_IN_AREA = 5010
SLAYMSG_BETTING_CHALLENGE_ALREADY_IN_PROGRESS = 5011
SLAYMSG_YOU_ONLY_HUMAN_PLAYER = 5012
SLAYMSG_NOT_PART_OF_GAME = 5013
SLAYMSG_NOT_INITIATOR = 5014
SLAYMSG_NOT_ENOUGH_MONEY = 5015
SLAYMSG_AREA_BELONG_NOT_YOU = 5016
SLAYMSG_AREA_TOO_SMALL = 5017
SLAYMSG_REGION_TOO_POOR_FOR_CASTLE = 5018
SLAYMSG_CASTLES_INFO = 5019
SLAYMSG_INVALID_DESTINATION = 5020
SLAYMSG_INVALID_START = 5021
SLAYMSG_NOTHING_TO_MOVE = 5022
SLAYMSG_FOREST_CANNOT_BE_MOVED = 5023
SLAYMSG_UNITS_CANNOT_BE_MOVED = 5024
SLAYMSG_UNIT_NOT_YOURS = 5025
SLAYMSG_SOURCE_HAS_NO_TILES = 5026
SLAYMSG_SOURCE_TILE_NOT_IN_AREA = 5027
SLAYMSG_UNIT_ALREADY_MOVED = 5028
SLAYMSG_MUST_PLACE_UNIT_IN_LOCAL_AREA = 5029
SLAYMSG_RUNNING_BET_DECISION = 5030
SLAYMSG_RUNNING_BET_CANCELLED_PARTICIPANT_ERROR = 5031
SLAYMSG_RUNNING_BET_CANCELLED_SYSTEM_ERROR = 5032
SLAYMSG_ERROR_PAYING_OUT_WINNINGS = 5033
SLAYMSG_WAITING_ON_AI = 5034
SLAYMSG_CANT_PLACE_ON_TOWNS = 5035
SLAYMSG_CANT_PLACE_ON_CASTLES = 5036
SLAYMSG_CANT_PLACE_ON_BARONS = 5037
SLAYMSG_UNIT_NOT_STRONG_ENOUGH = 5038
SLAYMSG_CANNOT_MERGE_UNITS = 5039
SLAYMSG_PLAYER_HAS_LEFT_GAME = 5040
SLAYMSG_PLAYER_HAS_SURRENDERED = 5041
SLAYMSG_SLAY_MAP_PREFIX_TYPE_1 = 5042
SLAYMSG_SLAY_MAP_PREFIX_TYPE_2 = 5043
SLAYMSG_SLAY_MAP_PREFIX_TYPE_3 = 5044
SLAYMSG_SLAY_MAP_PREFIX_TYPE_4 = 5045
SLAYMSG_SLAY_MAP_PREFIX_TYPE_5 = 5046
SLAYMSG_SLAY_MAP_PREFIX_TYPE_6 = 5047
SLAYMSG_SLAY_MAP_PREFIX_TYPE_7 = 5048
SLAYMSG_ERROR_PROCESSING_AI = 5049
SLAYMSG_GAME_STARTER_CANCELLED = 5050
slayMessageMapping = {SLAYMSG_NOT_ENOUGH_MONEY_FOR_BETTING: '',
 SLAYMSG_ERROR_STARTING_BETTING_ENTRY: '',
 SLAYMSG_BETTING_IS_DISABLED: '',
 SLAYMSG_GAME_STARTING: '',
 SLAYMSG_NOT_YOUR_TURN: '',
 SLAYMSG_CANT_UNDO_FURTHER: '',
 SLAYMSG_MUST_SELECT_AREA: '',
 SLAYMSG_REGION_TOO_POOR: '',
 SLAYMSG_CANT_PLACE_UNIT_THERE: '',
 SLAYMSG_MUST_PLACE_UNIT_IN_AREA: '',
 SLAYMSG_BETTING_CHALLENGE_ALREADY_IN_PROGRESS: '',
 SLAYMSG_YOU_ONLY_HUMAN_PLAYER: '',
 SLAYMSG_NOT_PART_OF_GAME: '',
 SLAYMSG_NOT_INITIATOR: '',
 SLAYMSG_NOT_ENOUGH_MONEY: '',
 SLAYMSG_AREA_BELONG_NOT_YOU: '',
 SLAYMSG_AREA_TOO_SMALL: '',
 SLAYMSG_REGION_TOO_POOR_FOR_CASTLE: '',
 SLAYMSG_CASTLES_INFO: '',
 SLAYMSG_INVALID_DESTINATION: '',
 SLAYMSG_INVALID_START: '',
 SLAYMSG_NOTHING_TO_MOVE: '',
 SLAYMSG_FOREST_CANNOT_BE_MOVED: '',
 SLAYMSG_UNITS_CANNOT_BE_MOVED: '',
 SLAYMSG_UNIT_NOT_YOURS: '',
 SLAYMSG_SOURCE_HAS_NO_TILES: '',
 SLAYMSG_SOURCE_TILE_NOT_IN_AREA: '',
 SLAYMSG_UNIT_ALREADY_MOVED: '',
 SLAYMSG_MUST_PLACE_UNIT_IN_LOCAL_AREA: '',
 SLAYMSG_RUNNING_BET_DECISION: '',
 SLAYMSG_RUNNING_BET_CANCELLED_PARTICIPANT_ERROR: '',
 SLAYMSG_RUNNING_BET_CANCELLED_SYSTEM_ERROR: '',
 SLAYMSG_ERROR_PAYING_OUT_WINNINGS: '',
 SLAYMSG_WAITING_ON_AI: '',
 SLAYMSG_CANT_PLACE_ON_TOWNS: '',
 SLAYMSG_CANT_PLACE_ON_CASTLES: '',
 SLAYMSG_CANT_PLACE_ON_BARONS: '',
 SLAYMSG_UNIT_NOT_STRONG_ENOUGH: '',
 SLAYMSG_CANNOT_MERGE_UNITS: '',
 SLAYMSG_PLAYER_HAS_LEFT_GAME: '',
 SLAYMSG_PLAYER_HAS_SURRENDERED: '',
 SLAYMSG_SLAY_MAP_PREFIX_TYPE_1: '',
 SLAYMSG_SLAY_MAP_PREFIX_TYPE_2: '',
 SLAYMSG_SLAY_MAP_PREFIX_TYPE_3: '',
 SLAYMSG_SLAY_MAP_PREFIX_TYPE_4: '',
 SLAYMSG_SLAY_MAP_PREFIX_TYPE_5: '',
 SLAYMSG_SLAY_MAP_PREFIX_TYPE_6: '',
 SLAYMSG_SLAY_MAP_PREFIX_TYPE_7: '',
 SLAYMSG_ERROR_PROCESSING_AI: '',
 SLAYMSG_GAME_STARTER_CANCELLED: ''}
exports = util.AutoExports('slayConst', locals())

