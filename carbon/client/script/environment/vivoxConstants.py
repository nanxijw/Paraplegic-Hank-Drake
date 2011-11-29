import util
VIVOX_NONE = 0
VIVOX_INITIALIZING = 1
VIVOX_OPTIC = 3
VXCNATDISCOVERY_NONE = 0
VXCNATDISCOVERY_STUN = 1
VXCNATDISCOVERY_MEDIA_PROXY = 2
VXCNATDISCOVERY_ALL = 3
VXCMEDIATYPE_AUDIO_SEND = 1
VXCMEDIATYPE_AUDIO_RECEIVE = 2
VXCMEDIATYPE_VIDEO_SEND = 4
VXCMEDIATYPE_VIDEO_RECEIVE = 8
VXCEVENTFILTER_CONNECTOR = 1
VXCEVENTFILTER_LOGIN_STATE_CHANGE = 2
VXCEVENTFILTER_SESSION_STATE_CHANGE = 4
VXCEVENTFILTER_SESSION_OPERATION_COMPLETE = 8
VXCEVENTFILTER_PARTICIPANT_STATE_CHANGE = 16
VXCEVENTFILTER_MEDIA = 32
VXCEVENTFILTER_INTENSITY = 64
VXCEVENTFILTER_MESSAGING = 128
VXCEVENTFILTER_BUDDY = 256
VXCEVENTFILTER_WATCHER = 512
VXCEVENTFILTER_PROFILE = 1024
VXCEVENTFILTER_USERSEARCH = 2048
VXCEVENTFILTER_INFO = 4096
VXCEVENTFILTER_GROUP = 8192
VXCEVENTFILTER_MEDIA_REQUEST = 16384
VXCEVENTFILTER_ROAMING = 65536
VXCEVENTFILTER_PRESENCE_PROPERTY = 131072
VXCEVENTFILTER_SESSION_REFER_STATUS = 1048576
VXCEVENTFILTER_SESSION_REFERRED = 2097152
VXCEVENTFILTER_REINVITE = 4194304
VXCEVENTFILTER_PRESENCE_DATA = 8388608
VXCEVENTFILTER_PRESENCE_STATUS = 16777216
VXCEVENTFILTER_CONNECTOR_STATE_CHANGE = 33554432
VXCEVENTFILTER_CONNECTOR_INITIALIZATION = 67108864
VXCEVENTFILTER_QUERY_COMPLETED = 134217728
VXCEVENTFILTER_ACCOUNT_COMMAND_COMPLETED = 268435456
VXCEVENTFILTER_CHANNEL_COMMAND_COMPLETED = 536870912
VXCEVENTFILTER_ALL = 1073741823
VXCPORTSELECTION_RANDOM = 0
VXCPORTSELECTION_SEQUENTIAL = 1
VXCAUDIODEVICE_SPEAKER = 0
VXCAUDIODEVICE_MICROPHONE = 1
VXCVIDEODEVICE_RECEIVE = 0
VXCVIDEODEVICE_PREVIEW = 1
VXCRINGTYPE_PHONE = 0
VXCRINGTYPE_MESSAGE = 1
VXCRINGTYPE_RINGBACK = 2
VXC_TOPOLOGY_UNKNOWN = 0
VXC_TOPOLOGY_STUN_OPEN = 1
VXC_TOPOLOGY_STUN_FULL_CONE_FIREWALL = 2
VXC_TOPOLOGY_STUN_FULL_CONE_NAT = 3
VXC_TOPOLOGY_STUN_RESTRICTED_CONE_NAT = 4
VXC_TOPOLOGY_STUN_PORT_RESTRICTED_CONE_NAT = 5
VXC_TOPOLOGY_STUN_SYMMETRIC_FIREWALL = 6
VXC_TOPOLOGY_STUN_SYMMETRIC_NAT = 7
VXC_TOPOLOGY_STUN_BLOCKED = 8
VXC_TOPOLOGY_UPNP_ENABLED_NAT_OR_FIREWALL = 9
VXCCONNECTORSTATE_SHUTDOWN = 0
VXCCONNECTORSTATE_INITIALIZING = 1
VXCCONNECTORSTATE_INITIALIZED = 2
VXCCONNECTORSTATE_SHUTTINGDOWN = 3
VXCLOGINSTATE_LOGGEDOUT = 0
VXCLOGINSTATE_LOGGINGIN = 1
VXCLOGINSTATE_LOGGEDIN = 2
VXCLOGINSTATE_LOGGINGOUT = 3
VXCLOGINSTATE_ERROR = 4
VXCDTMF_0 = 0
VXCDTMF_1 = 1
VXCDTMF_2 = 2
VXCDTMF_3 = 3
VXCDTMF_4 = 4
VXCDTMF_5 = 5
VXCDTMF_6 = 6
VXCDTMF_7 = 7
VXCDTMF_8 = 8
VXCDTMF_9 = 9
VXCDTMF_STAR = 10
VXCDTMF_POUND = 11
VXCDTMF_A = 12
VXCDTMF_B = 13
VXCDTMF_C = 14
VXCDTMF_D = 15
VXCDTMF_FLASH = 16
VXCANSWERMODE_OFFER_SESSION_EVENT = 0
VXCANSWERMODE_AUTOMATICALLY_ACCEPT = 1
VXCANSWERMODE_AUTOMATICALLY_REJECT = 2
VXCANSWERMODE_NOT_SUPPORTED = 3
VXCSESSIONTYPE_IM = 4
VXCSESSIONTYPE_MEDIA = 0
VXCEVENT_NONE = 0
VXCEVENT_ACCOUNT_LOGIN_STATE_CHANGE = 2
VXCEVENT_BUDDY_PRESENCE = 7
VXCEVENT_SUBSCRIPTION = 8
VXCEVENT_SESSION_NOTIFICATION = 9
VXCEVENT_MESSAGE = 10
VXCEVENT_AUX_AUDIO_PROPERTIES = 11
VXCEVENT_BUDDY_CHANGED = 15
VXCEVENT_BUDDY_GROUP_CHANGED = 16
VXCEVENT_BUDDY_AND_GROUP_LIST_CHANGED = 17
VXCEVENT_KEYBOARD_MOUSE = 18
VXCEVENT_IDLE_STATE_CHANGED = 19
VXCEVENT_MEDIA_STREAM_UPDATED = 20
VXCEVENT_TEXT_STREAM_UPDATED = 21
VXCEVENT_SESSIONGROUP_ADDED = 22
VXCEVENT_SESSIONGROUP_REMOVED = 23
VXCEVENT_SESSION_ADDED = 24
VXCEVENT_SESSION_REMOVED = 25
VXCEVENT_PARTICIPANT_ADDED = 26
VXCEVENT_PARTICIPANT_REMOVED = 27
VXCEVENT_PARTICIPANT_UPDATED = 28
VXCEVENT_SESSIONGROUP_PLAYBACK_FRAME_PLAYED = 30
VXCEVENT_SESSION_UPDATED = 31
VXCEVENT_SESSIONGROUP_UPDATED = 32
VXCEVENT_MEDIA_COMPLETION = 33
VXCEVENT_SERVER_APP_DATA = 35
VXCEVENT_USER_APP_DATA = 36
VXCEVENT_NETWORK_MESSAGE = 38
VXCEVENT_VOICE_SERVICE_CONNECTION_STATE_CHANGED = 39
VXCEVENT_LAST = VXCEVENT_VOICE_SERVICE_CONNECTION_STATE_CHANGED + 1
VXCSESSIONSTATE_ANSWERING = 2
VXCSESSIONSTATE_CONNECTED = 4
VXCSESSIONSTATE_DISCONNECTED = 5
VXCSESSIONSTATE_HOLD = 6
VXCSESSIONSTATE_IDLE = 0
VXCSESSIONSTATE_INCOMING = 1
VXCSESSIONSTATE_INPROGRESS = 3
VXCSESSIONSTATE_REFER = 7
VQRC_CHANNEL_ID = 0
VQRC_CHANNEL_NAME = 1
VQRC_CHANNEL_LIMIT = 2
VQRC_CHANNEL_URI = 3
VQRC_CHANNEL_PROTECTED = 4
VQRC_CHANNEL_OWNER = 5
VQRC_CHANNEL_PARENTID = 6
VQRC_CHANNEL_SIZE = 7
VQRC_CHANNEL_HOST = 8
VQRC_CHANNEL_PERSISTENT = 9
VQRC_CHANNEL_MODIFIED = 10
VQRC_CHANNEL_OWNERUSERNAME = 11
VQRC_CHANNEL_DESCRIPTION = 12
VQRC_CHANNEL_TYPE = 13
VQRC_USER_URI = 14
VQRC_USER_ACCOUNT = 15
VQRC_USER_ISPARTICIPANT = 16
VQRC_USER_ISBANNED = 17
VQRC_USER_ISMODERATOR = 18
VQRC_USER_FIRSTNAME = 19
VQRC_USER_LASTNAME = 20
VXPARTICIPANTSTATE_IDLE = 0
VXPARTICIPANTSTATE_PENDING = 1
VXPARTICIPANTSTATE_INCOMING = 2
VXPARTICIPANTSTATE_ANSWERING = 3
VXPARTICIPANTSTATE_INPROGRESS = 4
VXPARTICIPANTSTATE_ALERTING = 5
VXPARTICIPANTSTATE_CONNECTED = 6
VXPARTICIPANTSTATE_DISCONNECTING = 7
VXPARTICIPANTSTATE_DISCONNECTED = 8
VXPARTICIPANTTYPE_USER = 0
VXPARTICIPANTTYPE_MODERATOR = 1
VXPARTICIPANTTYPE_FOCUS = 2
VXCSESSIONSTATE_IDLE = 0
VXCSESSIONSTATE_INCOMING = 1
VXCSESSIONSTATE_ANSWERING = 2
VXCSESSIONSTATE_INPROGRESS = 3
VXCSESSIONSTATE_CONNECTED = 4
VXCSESSIONSTATE_DISCONNECTED = 5
VXCSESSIONSTATE_HOLD = 6
VXCSESSIONSTATE_REFER = 7
VXTYPINGSTATUS_IDLE = 0
VXTYPINGSTATUS_TYPING = 1
VXTERMINATEREASON_NORMAL = 0
VXTERMINATEREASON_DND = 1
VXTERMINATEREASON_BUSY = 2
VXTERMINATEREASON_REJECT = 3
VXTERMINATEREASON_TIMEOUT = 4
VXTERMINATEREASON_SHUTDOWN = 5
VXTERMINATEREASON_INSUFFICIENT_SECURITY_LEVEL = 6
VXTERMINATEREASON_NOT_SUPPORTED = 7
VXCMEDIAEVENTTYPE_STOPPED = 0
VXCMEDIAEVENTTYPE_STARTED = 1
VXCMEDIAEVENTTYPE_FAILED = 2
VXCMEDIAEVENTREASON_NORMAL = 0
VXCMEDIAEVENTREASON_HOLD = 1
VXCMEDIAEVENTREASON_TIMEOUT = 2
VXCMEDIAEVENTREASON_BAD_DEVICE = 3
VXCMEDIAEVENTREASON_NO_PORT = 4
VXCMEDIAEVENTREASON_PORT_MAPPING_FAILED = 5
VXCMEDIAEVENTREASON_REMOTE_REQUEST = 6
VXCMESSAGINGEVENTTYPE_MESSAGE = 0
VXCMESSAGINGEVENTTYPE_STATUS = 1
VXCMESSAGINGUSERSTATUS_IDLE = 0
VXCMESSAGINGUSERSTATUS_TYPING = 1
VXCQUERYRESULTTYPE_CHANNELS = 0
VXCQUERYRESULTTYPE_CHANNEL_USERS = 1
JOINED = 0
TALKING = 1
MUTED = 2
NOTJOINED = 3
VXACCOUNT_MAXCREATIONATTEMPTS = 5
VXVOLUME_MIN = 40
VXVOLUME_MAX = 75
VXVOLUME_DEFAULT = 50
VXVOLUME_OFF = 0
VXVOLUME_LOW = 25
VX_NOTONACL = 20212
VX_ACCESSDENIED = 403
VX_NOTFOUND = 404
VXLOGLEVEL_NONE = 0
VXLOGLEVEL_ERRORS = 1
VXLOGLEVEL_WARNINGS = 2
VXLOGLEVEL_INFO = 3
VXLOGLEVEL_DEBUG = 4
exports = util.AutoExports('vivoxConstants', globals())

