import aiming
AIMING_VALID_TARGET_GAZE_ID = 1
AIMING_VALID_TARGET_COMBAT_ID = 2
AIMING_CLIENTSERVER_FLAG_CLIENT = 1
AIMING_CLIENTSERVER_FLAG_SERVER = 2
AIMING_CLIENTSERVER_FLAG_BOTH = AIMING_CLIENTSERVER_FLAG_CLIENT | AIMING_CLIENTSERVER_FLAG_SERVER
AIMING_VALID_TARGETS = {AIMING_VALID_TARGET_GAZE_ID: (AIMING_VALID_TARGET_GAZE_ID,
                               'GazeTarget',
                               5.0,
                               AIMING_CLIENTSERVER_FLAG_BOTH),
 AIMING_VALID_TARGET_COMBAT_ID: (AIMING_VALID_TARGET_COMBAT_ID,
                                 'CombatTarget',
                                 1.0,
                                 AIMING_CLIENTSERVER_FLAG_BOTH)}
AIMING_VALID_TARGETS_FIELD_ID = 0
AIMING_VALID_TARGETS_FIELD_NAME = 1
AIMING_VALID_TARGETS_FIELD_RESELECTDELAY = 2
AIMING_VALID_TARGETS_FIELD_CLIENTSERVER_FLAG = 3
AIMING_CLIENTSERVER_FLAGS = {AIMING_CLIENTSERVER_FLAG_CLIENT: ' (Client only)',
 AIMING_CLIENTSERVER_FLAG_SERVER: ' (Server only)',
 AIMING_CLIENTSERVER_FLAG_BOTH: ' (Client & Server)'}
