import localization
STATE_OFFLINING = -7
STATE_ANCHORING = -6
STATE_ONLINING = -5
STATE_ANCHORED = -4
STATE_UNANCHORING = -3
STATE_UNANCHORED = -2
STATE_INCAPACITATED = -1
STATE_IDLE = 0
STATE_COMBAT = 1
STATE_MINING = 2
STATE_APPROACHING = 3
STATE_DEPARTING = 4
STATE_DEPARTING_2 = 5
STATE_PURSUIT = 6
STATE_FLEEING = 7
STATE_REINFORCED = 8
STATE_OPERATING = 9
STATE_ENGAGE = 10
STATE_VULNERABLE = 11
STATE_SHIELD_REINFORCE = 12
STATE_ARMOR_REINFORCE = 13
STATE_INVULNERABLE = 14
STATE_WARPAWAYANDDIE = 15
STATE_WARPAWAYANDCOMEBACK = 16
STATE_WARPTOPOSITION = 17
ENTITY_STATE_NAMES = {STATE_OFFLINING: 'State_OFFLINING',
 STATE_ANCHORING: 'STATE_ANCHORING',
 STATE_ONLINING: 'STATE_ONLINING',
 STATE_ANCHORED: 'STATE_ANCHORED',
 STATE_UNANCHORING: 'STATE_UNANCHORING',
 STATE_UNANCHORED: 'STATE_UNANCHORED',
 STATE_INCAPACITATED: 'STATE_INCAPACITATED',
 STATE_IDLE: 'STATE_IDLE',
 STATE_COMBAT: 'STATE_COMBAT',
 STATE_MINING: 'STATE_MINING',
 STATE_APPROACHING: 'STATE_APPROACHING',
 STATE_DEPARTING: 'STATE_DEPARTING',
 STATE_DEPARTING_2: 'STATE_DEPARTING_2',
 STATE_PURSUIT: 'STATE_PURSUIT',
 STATE_FLEEING: 'STATE_FLEEING',
 STATE_REINFORCED: 'STATE_REINFORCED',
 STATE_OPERATING: 'STATE_OPERATING',
 STATE_ENGAGE: 'STATE_ENGAGE',
 STATE_VULNERABLE: 'STATE_VULNERABLE',
 STATE_SHIELD_REINFORCE: 'STATE_SHIELD_REINFORCE',
 STATE_ARMOR_REINFORCE: 'STATE_ARMOR_REINFORCE',
 STATE_INVULNERABLE: 'STATE_INVULNERABLE',
 STATE_WARPAWAYANDDIE: 'STATE_WARPAWAYANDDIE',
 STATE_WARPAWAYANDCOMEBACK: 'STATE_WARPAWAYANDCOMEBACK',
 STATE_WARPTOPOSITION: 'STATE_WARPTOPOSITION'}
entityStateStrings = {STATE_ANCHORING: localization.GetByLabel('Entities/States/Anchoring'),
 STATE_ONLINING: localization.GetByLabel('Entities/States/Onlining'),
 STATE_ANCHORED: localization.GetByLabel('Entities/States/Anchored'),
 STATE_UNANCHORING: localization.GetByLabel('Entities/States/Unanchoring'),
 STATE_UNANCHORED: localization.GetByLabel('Entities/States/Unanchored'),
 STATE_INCAPACITATED: localization.GetByLabel('Entities/States/Incapacitated'),
 STATE_IDLE: localization.GetByLabel('Entities/States/Idle'),
 STATE_COMBAT: localization.GetByLabel('Entities/States/Fighting'),
 STATE_MINING: localization.GetByLabel('Entities/States/Mining'),
 STATE_APPROACHING: localization.GetByLabel('Entities/States/Approaching'),
 STATE_FLEEING: localization.GetByLabel('Entities/States/Fleeing'),
 STATE_REINFORCED: localization.GetByLabel('Entities/States/Reinforced'),
 STATE_OPERATING: localization.GetByLabel('Entities/States/Operating'),
 STATE_VULNERABLE: localization.GetByLabel('Entities/States/Vulnerable'),
 STATE_INVULNERABLE: localization.GetByLabel('Entities/States/Invulnerable'),
 STATE_SHIELD_REINFORCE: localization.GetByLabel('Entities/States/ShieldReinforced'),
 STATE_ARMOR_REINFORCE: localization.GetByLabel('Entities/States/ArmorReinforced')}

def GetEntityStateString(entityState):
    return entityStateStrings.get(entityState, localization.GetByLabel('Entities/States/Unknown', entityStateID=entityState))


INCAPACITATION_DISTANCE = 250000
COMMAND_DISTANCE = INCAPACITATION_DISTANCE
entityConstants = {'ENTITY_STATE_NAMES': ENTITY_STATE_NAMES}
exports = {'entities.entityConstants': entityConstants,
 'entities.ENTITY_STATE_NAMES': ENTITY_STATE_NAMES,
 'entities.GetEntityStateString': GetEntityStateString}
for (k, v,) in locals().items():
    if (k.startswith('STATE_') or k.endswith('_DISTANCE')) and type(v) is int:
        exports['entities.' + k] = v
        entityConstants[k] = v


