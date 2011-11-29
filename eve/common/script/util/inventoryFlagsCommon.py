import util
import const
import localization
inventoryFlagData = {const.flagCargo: {'name': localization.GetByLabel('UI/Ship/CargoHold'),
                   'openCommand': localization.GetByLabel('UI/Commands/OpenCargoHold'),
                   'attribute': const.attributeCapacity,
                   'allowCategories': None,
                   'allowGroups': None,
                   'blockGroups': None,
                   'allowTypes': None,
                   'blockTypes': None},
 const.flagDroneBay: {'name': localization.GetByLabel('UI/Ship/DroneBay'),
                      'openCommand': localization.GetByLabel('UI/Commands/OpenDroneBay'),
                      'attribute': const.attributeDroneCapacity,
                      'allowCategories': (const.categoryDrone,),
                      'allowGroups': None,
                      'blockGroups': None,
                      'allowTypes': None,
                      'blockTypes': None},
 const.flagShipHangar: {'name': localization.GetByLabel('UI/Ship/ShipMaintenanceBay'),
                        'openCommand': localization.GetByLabel('UI/Commands/OpenShipMaintenanceBay'),
                        'attribute': const.attributeShipMaintenanceBayCapacity,
                        'allowCategories': (const.categoryShip,),
                        'allowGroups': None,
                        'blockGroups': (const.groupCapsule,),
                        'allowTypes': None,
                        'blockTypes': None},
 const.flagSpecializedFuelBay: {'name': localization.GetByLabel('UI/Ship/FuelBay'),
                                'openCommand': localization.GetByLabel('UI/Commands/OpenFuelBay'),
                                'attribute': const.attributeSpecialFuelBayCapacity,
                                'allowCategories': None,
                                'blockCategories': None,
                                'allowGroups': (const.groupIceProduct,),
                                'blockGroups': None,
                                'allowTypes': None,
                                'blockTypes': None},
 const.flagSpecializedOreHold: {'name': localization.GetByLabel('UI/Ship/OreHold'),
                                'openCommand': localization.GetByLabel('UI/Commands/OpenOreHold'),
                                'attribute': const.attributeSpecialOreHoldCapacity,
                                'allowCategories': (const.categoryAsteroid,),
                                'blockCategories': None,
                                'allowGroups': None,
                                'blockGroups': None,
                                'allowTypes': None,
                                'blockTypes': None},
 const.flagSpecializedGasHold: {'name': localization.GetByLabel('UI/Ship/GasHold'),
                                'openCommand': localization.GetByLabel('UI/Commands/OpenGasHold'),
                                'attribute': const.attributeSpecialGasHoldCapacity,
                                'allowCategories': None,
                                'blockCategories': None,
                                'allowGroups': (const.groupHarvestableCloud,),
                                'blockGroups': None,
                                'allowTypes': None,
                                'blockTypes': None},
 const.flagSpecializedMineralHold: {'name': localization.GetByLabel('UI/Ship/MineralHold'),
                                    'openCommand': localization.GetByLabel('UI/Commands/OpenMineralHold'),
                                    'attribute': const.attributeSpecialMineralHoldCapacity,
                                    'allowCategories': None,
                                    'blockCategories': None,
                                    'allowGroups': (const.groupMineral,),
                                    'blockGroups': None,
                                    'allowTypes': None,
                                    'blockTypes': None},
 const.flagSpecializedSalvageHold: {'name': localization.GetByLabel('UI/Ship/SalvageHold'),
                                    'openCommand': localization.GetByLabel('UI/Commands/OpenSalvageHold'),
                                    'attribute': const.attributeSpecialSalvageHoldCapacity,
                                    'allowCategories': None,
                                    'blockCategories': None,
                                    'allowGroups': (const.groupAncientSalvage, const.groupSalvagedMaterials, const.groupRefinables),
                                    'blockGroups': None,
                                    'allowTypes': None,
                                    'blockTypes': None},
 const.flagSpecializedShipHold: {'name': localization.GetByLabel('UI/Ship/ShipHold'),
                                 'openCommand': localization.GetByLabel('UI/Commands/OpenShipHold'),
                                 'attribute': const.attributeSpecialShipHoldCapacity,
                                 'allowCategories': (const.categoryShip,),
                                 'blockCategories': None,
                                 'allowGroups': None,
                                 'blockGroups': None,
                                 'allowTypes': None,
                                 'blockTypes': None},
 const.flagSpecializedSmallShipHold: {'name': localization.GetByLabel('UI/Ship/SmallShipHold'),
                                      'openCommand': localization.GetByLabel('UI/Commands/OpenSmallShipHold'),
                                      'attribute': const.attributeSpecialSmallShipHoldCapacity,
                                      'allowCategories': None,
                                      'blockCategories': None,
                                      'allowGroups': (const.groupFrigate,
                                                      const.groupAssaultShip,
                                                      const.groupDestroyer,
                                                      const.groupInterdictor,
                                                      const.groupInterceptor,
                                                      const.groupCovertOps,
                                                      const.groupElectronicAttackShips,
                                                      const.groupStealthBomber),
                                      'blockGroups': None,
                                      'allowTypes': None,
                                      'blockTypes': None},
 const.flagSpecializedMediumShipHold: {'name': localization.GetByLabel('UI/Ship/MediumShipHold'),
                                       'openCommand': localization.GetByLabel('UI/Commands/OpenMediumShipHold'),
                                       'attribute': const.attributeSpecialMediumShipHoldCapacity,
                                       'allowCategories': None,
                                       'blockCategories': None,
                                       'allowGroups': (const.groupCruiser,
                                                       const.groupCombatReconShip,
                                                       const.groupCommandShip,
                                                       const.groupHeavyAssaultShip,
                                                       const.groupHeavyInterdictors,
                                                       const.groupLogistics,
                                                       const.groupStrategicCruiser,
                                                       const.groupBattlecruiser,
                                                       const.groupForceReconShip),
                                       'blockGroups': None,
                                       'allowTypes': None,
                                       'blockTypes': None},
 const.flagSpecializedLargeShipHold: {'name': localization.GetByLabel('UI/Ship/LargeShipHold'),
                                      'openCommand': localization.GetByLabel('UI/Commands/OpenLargeShipHold'),
                                      'attribute': const.attributeSpecialLargeShipHoldCapacity,
                                      'allowCategories': None,
                                      'blockCategories': None,
                                      'allowGroups': (const.groupBattleship, const.groupBlackOps, const.groupMarauders),
                                      'blockGroups': None,
                                      'allowTypes': None,
                                      'blockTypes': None},
 const.flagSpecializedIndustrialShipHold: {'name': localization.GetByLabel('UI/Ship/IndustrialShipHold'),
                                           'openCommand': localization.GetByLabel('UI/Commands/OpenIndustrialShipHold'),
                                           'attribute': const.attributeSpecialIndustrialShipHoldCapacity,
                                           'allowCategories': None,
                                           'blockCategories': None,
                                           'allowGroups': (const.groupIndustrial,
                                                           const.groupExhumer,
                                                           const.groupMiningBarge,
                                                           const.groupTransportShip),
                                           'blockGroups': None,
                                           'allowTypes': None,
                                           'blockTypes': None},
 const.flagSpecializedAmmoHold: {'name': localization.GetByLabel('UI/Ship/AmmoHold'),
                                 'openCommand': localization.GetByLabel('UI/Commands/OpenAmmoHold'),
                                 'attribute': const.attributeSpecialAmmoHoldCapacity,
                                 'allowCategories': (const.categoryCharge,),
                                 'blockCategories': None,
                                 'allowGroups': None,
                                 'blockGroups': None,
                                 'allowTypes': None,
                                 'blockTypes': None},
 const.flagSpecializedCommandCenterHold: {'name': localization.GetByLabel('UI/Ship/CommandCenterHold'),
                                          'openCommand': localization.GetByLabel('UI/Commands/OpenCommandCenterHold'),
                                          'attribute': const.attributeSpecialCommandCenterHoldCapacity,
                                          'allowCategories': None,
                                          'blockCategories': None,
                                          'allowGroups': (const.groupCommandPins,),
                                          'blockGroups': None,
                                          'allowTypes': None,
                                          'blockTypes': None},
 const.flagSpecializedPlanetaryCommoditiesHold: {'name': localization.GetByLabel('UI/Ship/PlanetaryCommoditiesHold'),
                                                 'openCommand': localization.GetByLabel('UI/Commands/OpenPlanetaryCommoditiesHold'),
                                                 'attribute': const.attributeSpecialPlanetaryCommoditiesHoldCapacity,
                                                 'allowCategories': (const.categoryPlanetaryCommodities, const.categoryPlanetaryResources),
                                                 'blockCategories': None,
                                                 'allowGroups': None,
                                                 'blockGroups': None,
                                                 'allowTypes': (const.typeWater, const.typeOxygen),
                                                 'blockTypes': None},
 const.flagSpecializedMaterialBay: {'name': localization.GetByLabel('UI/Ship/MaterialBay'),
                                    'openCommand': localization.GetByLabel('UI/Commands/OpenMaterialBay'),
                                    'attribute': const.attributeSpecialMaterialBayCapacity,
                                    'allowCategories': (const.categoryPlanetaryCommodities, const.categoryCommodity, const.categoryMaterial),
                                    'blockCategories': None,
                                    'allowGroups': None,
                                    'blockGroups': None,
                                    'allowTypes': None,
                                    'blockTypes': None}}

def ShouldAllowAdd(flag, categoryID, groupID, typeID):
    if flag not in inventoryFlagData:
        return 
    flagData = inventoryFlagData[flag]
    errorTuple = None
    useAllow = True
    if flagData['allowCategories'] is not None:
        if categoryID in flagData['allowCategories']:
            useAllow = False
        else:
            errorTuple = (CATID, categoryID)
    if useAllow:
        if flagData['allowGroups'] is not None:
            if groupID in flagData['allowGroups']:
                errorTuple = None
                useAllow = False
            else:
                errorTuple = (GROUPID, groupID)
                useAllow = True
    elif flagData['blockGroups'] is not None:
        if groupID in flagData['blockGroups']:
            errorTuple = (GROUPID, groupID)
            useAllow = True
        else:
            errorTuple = None
            useAllow = False
    if useAllow:
        if flagData['allowTypes'] is not None:
            if typeID in flagData['allowTypes']:
                errorTuple = None
            else:
                errorTuple = (TYPEID, typeID)
    elif flagData['blockTypes'] is not None:
        if typeID in flagData['blockTypes']:
            errorTuple = (TYPEID, typeID)
        else:
            errorTuple = None
    return errorTuple


autoConsumeTypes = {}
autoConsumeGroups = {const.groupIceProduct: (const.flagSpecializedFuelBay,)}
autoConsumeCategories = {}

def GetBaysToCheck(typeID, priorityBays = []):
    baysToCheck = priorityBays
    if baysToCheck is None:
        baysToCheck = []
    if typeID in autoConsumeTypes:
        baysToCheck.extend(autoConsumeTypes[typeID])
    else:
        invType = cfg.invtypes.Get(typeID)
        if invType.groupID in autoConsumeGroups:
            baysToCheck.extend(autoConsumeGroups[invType.groupID])
        elif invType.categoryID in autoConsumeCategories:
            baysToCheck.extend(autoConsumeCategories[invType.categoryID])
    if const.flagCargo not in baysToCheck:
        baysToCheck.append(const.flagCargo)
    return baysToCheck


exports = util.AutoExports('inventoryFlagsCommon', locals())

