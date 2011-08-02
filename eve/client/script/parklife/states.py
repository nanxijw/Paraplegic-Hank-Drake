exports = {'state.version': 5}
flags = {'mouseOver': 1,
 'selected': 2,
 'activeTarget': 3,
 'targeting': 4,
 'targeted': 5,
 'lookingAt': 6,
 'threatTargetsMe': 7,
 'threatAttackingMe': 8,
 'flagCriminal': 9,
 'flagDangerous': 10,
 'flagSameFleet': 11,
 'flagSameCorp': 12,
 'flagAtWarCanFight': 13,
 'flagSameAlliance': 14,
 'flagStandingHigh': 15,
 'flagStandingGood': 16,
 'flagStandingNeutral': 17,
 'flagStandingBad': 18,
 'flagStandingHorrible': 19,
 'flagIsWanted': 20,
 'flagAgentInteractable': 21,
 'gbEnemySpotted': 22,
 'gbTarget': 23,
 'gbHealShield': 24,
 'gbHealArmor': 25,
 'gbHealCapacitor': 26,
 'gbWarpTo': 27,
 'gbNeedBackup': 28,
 'gbAlignTo': 29,
 'gbJumpTo': 30,
 'gbInPosition': 31,
 'gbHoldPosition': 32,
 'gbTravelTo': 33,
 'gbJumpBeacon': 34,
 'gbLocation': 35,
 'flagWreckAlreadyOpened': 36,
 'flagWreckEmpty': 37,
 'flagWarpScrambled': 38,
 'flagWebified': 39,
 'flagECMd': 40,
 'flagSensorDampened': 41,
 'flagTrackingDisrupted': 42,
 'flagTargetPainted': 43,
 'flagAtWarMilitia': 44,
 'flagSameMilitia': 45,
 'flagEnergyLeeched': 46,
 'flagEnergyNeut': 47,
 'flagNoStanding': 48}
for (flag, value,) in flags.iteritems():
    exports['state.' + flag] = value

