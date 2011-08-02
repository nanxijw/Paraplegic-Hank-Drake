import const
if const.world.WORLD_SPACE_SCHEMA == 'zworld':
    LOCATOR_SCHEMA = 'zworld'
else:
    LOCATOR_SCHEMA = 'locator'
_LOCATOR_PREFIX = LOCATOR_SCHEMA + '.'
LOCATOR_TABLE_NAME = 'locators'
LOCATOR_TABLE_FULL_NAME = _LOCATOR_PREFIX + LOCATOR_TABLE_NAME
AREA_TABLE_NAME = 'locatorAreas'
AREA_TABLE_FULL_NAME = _LOCATOR_PREFIX + AREA_TABLE_NAME
ALL_TABLES = [LOCATOR_TABLE_FULL_NAME, AREA_TABLE_FULL_NAME]
TRINITY_DRAG_LOCATOR = 'Locator'
TRINITY_DRAG_AREA = 'Area'
LOCATOR_ID = 'locatorID'
LOCATOR_NAME = 'locatorName'
LOCATOR_WORLDSPACE_ID = 'worldSpaceID'
LOCATOR_POSITION_X = 'posX'
LOCATOR_POSITION_Y = 'posY'
LOCATOR_POSITION_Z = 'posZ'
LOCATOR_YAW = 'yaw'
LOCATOR_PITCH = 'pitch'
LOCATOR_ROLL = 'roll'
LOCATOR_SNAP_TO_GROUND = 'snapToGround'
AREA_TYPE = 'areaType'
AREA_RADIUS = 'radius'
ALL_ATTRIBUTES = [LOCATOR_ID,
 LOCATOR_NAME,
 LOCATOR_POSITION_X,
 LOCATOR_POSITION_Y,
 LOCATOR_POSITION_Z,
 LOCATOR_YAW,
 LOCATOR_PITCH,
 LOCATOR_ROLL,
 LOCATOR_SNAP_TO_GROUND]
AREA_ATTRIBUTES = [LOCATOR_ID,
 LOCATOR_NAME,
 AREA_TYPE,
 AREA_RADIUS,
 LOCATOR_POSITION_X,
 LOCATOR_POSITION_Y,
 LOCATOR_POSITION_Z,
 LOCATOR_YAW,
 LOCATOR_PITCH,
 LOCATOR_ROLL,
 LOCATOR_SNAP_TO_GROUND]
SPHERE_AREA_TYPE = 0
CYLINDER_AREA_TYPE = 1
LOGIN_CAMERA_LOCATOR = 'CameraMarker'
LOGIN_CHARACTER_SELECTION_LOCATOR = 'characterSelectionMarker'
HAVEN_LOCATOR_DOOR = 'HavenDoor'
HAVEN_LOCATOR_BED = 'HavenBed'
HAVEN_LOCATOR_SPAWN = 'HavenSpawn'

