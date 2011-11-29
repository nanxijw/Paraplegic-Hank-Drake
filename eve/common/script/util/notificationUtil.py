import sys
import log
import const
import util
import blue
import entities
import types
import yaml
import localization
import localizationUtil
securityLevelDescriptions = {-10: 'Notifications/SecurityStatus/SecurityDescription_-10',
 -9: 'Notifications/SecurityStatus/SecurityDescription_-9',
 -8: 'Notifications/SecurityStatus/SecurityDescription_-8',
 -7: 'Notifications/SecurityStatus/SecurityDescription_-7',
 -6: 'Notifications/SecurityStatus/SecurityDescription_-6',
 -5: 'Notifications/SecurityStatus/SecurityDescription_-5',
 -4: 'Notifications/SecurityStatus/SecurityDescription_-4',
 -3: 'Notifications/SecurityStatus/SecurityDescription_-3',
 -2: 'Notifications/SecurityStatus/SecurityDescription_-2',
 -1: 'Notifications/SecurityStatus/SecurityDescription_-1',
 0: 'Notifications/SecurityStatus/SecurityDescription_0',
 1: 'Notifications/SecurityStatus/SecurityDescription_1',
 2: 'Notifications/SecurityStatus/SecurityDescription_2',
 3: 'Notifications/SecurityStatus/SecurityDescription_3',
 4: 'Notifications/SecurityStatus/SecurityDescription_4',
 5: 'Notifications/SecurityStatus/SecurityDescription_5',
 6: 'Notifications/SecurityStatus/SecurityDescription_6',
 7: 'Notifications/SecurityStatus/SecurityDescription_7',
 8: 'Notifications/SecurityStatus/SecurityDescription_8',
 9: 'Notifications/SecurityStatus/SecurityDescription_9',
 10: 'Notifications/SecurityStatus/SecurityDescription_10'}
rankLost = {const.factionCaldariState: 'Factions/CaldariState/rankLost',
 const.factionMinmatarRepublic: 'Factions/MinmatarRepublic/rankLost',
 const.factionAmarrEmpire: 'Factions/AmarrEmpire/rankLost',
 const.factionGallenteFederation: 'Factions/GallenteFederation/rankLost'}
rankGain = {const.factionCaldariState: 'Factions/CaldariState/rankGain',
 const.factionMinmatarRepublic: 'Factions/MinmatarRepublic/rankGain',
 const.factionAmarrEmpire: 'Factions/AmarrEmpire/rankGain',
 const.factionGallenteFederation: 'Factions/GallenteFederation/rankGain'}
notificationTypes = {'notificationTypeOldLscMessages': 1,
 'notificationTypeCharTerminationMsg': 2,
 'notificationTypeCharMedalMsg': 3,
 'notificationTypeAllMaintenanceBillMsg': 4,
 'notificationTypeAllWarDeclaredMsg': 5,
 'notificationTypeAllWarSurrenderMsg': 6,
 'notificationTypeAllWarRetractedMsg': 7,
 'notificationTypeAllWarInvalidatedMsg': 8,
 'notificationTypeCharBillMsg': 9,
 'notificationTypeCorpAllBillMsg': 10,
 'notificationTypeBillOutOfMoneyMsg': 11,
 'notificationTypeBillPaidCharMsg': 12,
 'notificationTypeBillPaidCorpAllMsg': 13,
 'notificationTypeBountyClaimMsg': 14,
 'notificationTypeCloneActivationMsg': 15,
 'notificationTypeCorpAppNewMsg': 16,
 'notificationTypeCorpAppRejectMsg': 17,
 'notificationTypeCorpAppAcceptMsg': 18,
 'notificationTypeCorpTaxChangeMsg': 19,
 'notificationTypeCorpNewsMsg': 20,
 'notificationTypeCharLeftCorpMsg': 21,
 'notificationTypeCorpNewCEOMsg': 22,
 'notificationTypeCorpDividendMsg': 23,
 'notificationTypeCorpVoteMsg': 25,
 'notificationTypeCorpVoteCEORevokedMsg': 26,
 'notificationTypeCorpWarDeclaredMsg': 27,
 'notificationTypeCorpWarFightingLegalMsg': 28,
 'notificationTypeCorpWarSurrenderMsg': 29,
 'notificationTypeCorpWarRetractedMsg': 30,
 'notificationTypeCorpWarInvalidatedMsg': 31,
 'notificationTypeContainerPasswordMsg': 32,
 'notificationTypeCustomsMsg': 33,
 'notificationTypeInsuranceFirstShipMsg': 34,
 'notificationTypeInsurancePayoutMsg': 35,
 'notificationTypeInsuranceInvalidatedMsg': 36,
 'notificationTypeSovAllClaimFailMsg': 37,
 'notificationTypeSovCorpClaimFailMsg': 38,
 'notificationTypeSovAllBillLateMsg': 39,
 'notificationTypeSovCorpBillLateMsg': 40,
 'notificationTypeSovAllClaimLostMsg': 41,
 'notificationTypeSovCorpClaimLostMsg': 42,
 'notificationTypeSovAllClaimAquiredMsg': 43,
 'notificationTypeSovCorpClaimAquiredMsg': 44,
 'notificationTypeAllAnchoringMsg': 45,
 'notificationTypeAllStructVulnerableMsg': 46,
 'notificationTypeAllStrucInvulnerableMsg': 47,
 'notificationTypeSovDisruptorMsg': 48,
 'notificationTypeCorpStructLostMsg': 49,
 'notificationTypeCorpOfficeExpirationMsg': 50,
 'notificationTypeCloneRevokedMsg1': 51,
 'notificationTypeCloneMovedMsg': 52,
 'notificationTypeCloneRevokedMsg2': 53,
 'notificationTypeInsuranceExpirationMsg': 54,
 'notificationTypeInsuranceIssuedMsg': 55,
 'notificationTypeJumpCloneDeletedMsg1': 56,
 'notificationTypeJumpCloneDeletedMsg2': 57,
 'notificationTypeFWCorpJoinMsg': 58,
 'notificationTypeFWCorpLeaveMsg': 59,
 'notificationTypeFWCorpKickMsg': 60,
 'notificationTypeFWCharKickMsg': 61,
 'notificationTypeFWCorpWarningMsg': 62,
 'notificationTypeFWCharWarningMsg': 63,
 'notificationTypeFWCharRankLossMsg': 64,
 'notificationTypeFWCharRankGainMsg': 65,
 'notificationTypeAgentMoveMsg': 66,
 'notificationTypeTransactionReversalMsg': 67,
 'notificationTypeReimbursementMsg': 68,
 'notificationTypeLocateCharMsg': 69,
 'notificationTypeResearchMissionAvailableMsg': 70,
 'notificationTypeMissionOfferExpirationMsg': 71,
 'notificationTypeMissionTimeoutMsg': 72,
 'notificationTypeStoryLineMissionAvailableMsg': 73,
 'notificationTypeTutorialMsg': 74,
 'notificationTypeTowerAlertMsg': 75,
 'notificationTypeTowerResourceAlertMsg': 76,
 'notificationTypeStationAggressionMsg1': 77,
 'notificationTypeStationStateChangeMsg': 78,
 'notificationTypeStationConquerMsg': 79,
 'notificationTypeStationAggressionMsg2': 80,
 'notificationTypeFacWarCorpJoinRequestMsg': 81,
 'notificationTypeFacWarCorpLeaveRequestMsg': 82,
 'notificationTypeFacWarCorpJoinWithdrawMsg': 83,
 'notificationTypeFacWarCorpLeaveWithdrawMsg': 84,
 'notificationTypeCorpLiquidationMsg': 85,
 'notificationTypeSovereigntyTCUDamageMsg': 86,
 'notificationTypeSovereigntySBUDamageMsg': 87,
 'notificationTypeSovereigntyIHDamageMsg': 88,
 'notificationTypeContactAdd': 89,
 'notificationTypeContactEdit': 90,
 'notificationTypeIncursionCompletedMsg': 91,
 'notificationTypeCorpKicked': 92,
 'notificationTypeOrbitalAttacked': 93,
 'notificationTypeOrbitalReinforced': 94,
 'notificationTypeOwnershipTransferred': 95}
notifyIDs = util.KeyVal(notificationTypes)
groupUnread = 0
groupAgents = 1
groupBills = 2
groupCorp = 3
groupMisc = 4
groupOld = 5
groupSov = 6
groupStructures = 7
groupWar = 8
groupContacts = 9
groupTypes = {groupAgents: [notifyIDs.notificationTypeAgentMoveMsg,
               notifyIDs.notificationTypeLocateCharMsg,
               notifyIDs.notificationTypeResearchMissionAvailableMsg,
               notifyIDs.notificationTypeMissionOfferExpirationMsg,
               notifyIDs.notificationTypeMissionTimeoutMsg,
               notifyIDs.notificationTypeStoryLineMissionAvailableMsg,
               notifyIDs.notificationTypeTutorialMsg],
 groupBills: [notifyIDs.notificationTypeAllMaintenanceBillMsg,
              notifyIDs.notificationTypeCharBillMsg,
              notifyIDs.notificationTypeCorpAllBillMsg,
              notifyIDs.notificationTypeBillOutOfMoneyMsg,
              notifyIDs.notificationTypeBillPaidCharMsg,
              notifyIDs.notificationTypeBillPaidCorpAllMsg,
              notifyIDs.notificationTypeCorpOfficeExpirationMsg],
 groupContacts: [notifyIDs.notificationTypeContactAdd, notifyIDs.notificationTypeContactEdit],
 groupCorp: [notifyIDs.notificationTypeCharTerminationMsg,
             notifyIDs.notificationTypeCharMedalMsg,
             notifyIDs.notificationTypeCorpAppNewMsg,
             notifyIDs.notificationTypeCorpAppRejectMsg,
             notifyIDs.notificationTypeCorpAppAcceptMsg,
             notifyIDs.notificationTypeCorpTaxChangeMsg,
             notifyIDs.notificationTypeCorpNewsMsg,
             notifyIDs.notificationTypeCharLeftCorpMsg,
             notifyIDs.notificationTypeCorpNewCEOMsg,
             notifyIDs.notificationTypeCorpDividendMsg,
             notifyIDs.notificationTypeCorpVoteMsg,
             notifyIDs.notificationTypeCorpVoteCEORevokedMsg,
             notifyIDs.notificationTypeCorpLiquidationMsg,
             notifyIDs.notificationTypeCorpKicked],
 groupMisc: [notifyIDs.notificationTypeBountyClaimMsg,
             notifyIDs.notificationTypeCloneActivationMsg,
             notifyIDs.notificationTypeContainerPasswordMsg,
             notifyIDs.notificationTypeCustomsMsg,
             notifyIDs.notificationTypeInsuranceFirstShipMsg,
             notifyIDs.notificationTypeInsurancePayoutMsg,
             notifyIDs.notificationTypeInsuranceInvalidatedMsg,
             notifyIDs.notificationTypeCloneRevokedMsg1,
             notifyIDs.notificationTypeCloneMovedMsg,
             notifyIDs.notificationTypeCloneRevokedMsg2,
             notifyIDs.notificationTypeInsuranceExpirationMsg,
             notifyIDs.notificationTypeInsuranceIssuedMsg,
             notifyIDs.notificationTypeJumpCloneDeletedMsg1,
             notifyIDs.notificationTypeJumpCloneDeletedMsg2,
             notifyIDs.notificationTypeTransactionReversalMsg,
             notifyIDs.notificationTypeReimbursementMsg,
             notifyIDs.notificationTypeIncursionCompletedMsg],
 groupOld: [notifyIDs.notificationTypeOldLscMessages],
 groupSov: [notifyIDs.notificationTypeSovAllClaimFailMsg,
            notifyIDs.notificationTypeSovCorpClaimFailMsg,
            notifyIDs.notificationTypeSovAllBillLateMsg,
            notifyIDs.notificationTypeSovCorpBillLateMsg,
            notifyIDs.notificationTypeSovAllClaimLostMsg,
            notifyIDs.notificationTypeSovCorpClaimLostMsg,
            notifyIDs.notificationTypeSovAllClaimAquiredMsg,
            notifyIDs.notificationTypeSovCorpClaimAquiredMsg,
            notifyIDs.notificationTypeSovDisruptorMsg,
            notifyIDs.notificationTypeAllStructVulnerableMsg,
            notifyIDs.notificationTypeAllStrucInvulnerableMsg,
            notifyIDs.notificationTypeSovereigntyTCUDamageMsg,
            notifyIDs.notificationTypeSovereigntySBUDamageMsg,
            notifyIDs.notificationTypeSovereigntyIHDamageMsg],
 groupStructures: [notifyIDs.notificationTypeAllAnchoringMsg,
                   notifyIDs.notificationTypeCorpStructLostMsg,
                   notifyIDs.notificationTypeTowerAlertMsg,
                   notifyIDs.notificationTypeTowerResourceAlertMsg,
                   notifyIDs.notificationTypeStationAggressionMsg1,
                   notifyIDs.notificationTypeStationStateChangeMsg,
                   notifyIDs.notificationTypeStationConquerMsg,
                   notifyIDs.notificationTypeStationAggressionMsg2,
                   notifyIDs.notificationTypeOrbitalAttacked,
                   notifyIDs.notificationTypeOrbitalReinforced,
                   notifyIDs.notificationTypeOwnershipTransferred],
 groupWar: [notifyIDs.notificationTypeAllWarDeclaredMsg,
            notifyIDs.notificationTypeAllWarSurrenderMsg,
            notifyIDs.notificationTypeAllWarRetractedMsg,
            notifyIDs.notificationTypeAllWarInvalidatedMsg,
            notifyIDs.notificationTypeCorpWarDeclaredMsg,
            notifyIDs.notificationTypeCorpWarFightingLegalMsg,
            notifyIDs.notificationTypeCorpWarSurrenderMsg,
            notifyIDs.notificationTypeCorpWarRetractedMsg,
            notifyIDs.notificationTypeCorpWarInvalidatedMsg,
            notifyIDs.notificationTypeFWCorpJoinMsg,
            notifyIDs.notificationTypeFWCorpLeaveMsg,
            notifyIDs.notificationTypeFWCorpKickMsg,
            notifyIDs.notificationTypeFWCharKickMsg,
            notifyIDs.notificationTypeFWCorpWarningMsg,
            notifyIDs.notificationTypeFWCharWarningMsg,
            notifyIDs.notificationTypeFWCharRankLossMsg,
            notifyIDs.notificationTypeFWCharRankGainMsg,
            notifyIDs.notificationTypeFacWarCorpJoinRequestMsg,
            notifyIDs.notificationTypeFacWarCorpLeaveRequestMsg,
            notifyIDs.notificationTypeFacWarCorpJoinWithdrawMsg,
            notifyIDs.notificationTypeFacWarCorpLeaveWithdrawMsg]}
groupNamePaths = {groupAgents: 'Notifications/groupAgents',
 groupBills: 'Notifications/groupBills',
 groupContacts: 'Notifications/groupContacts',
 groupCorp: 'Notifications/groupCorporation',
 groupMisc: 'Notifications/groupMisc',
 groupOld: 'Notifications/groupOld',
 groupSov: 'Notifications/groupSovereignty',
 groupStructures: 'Notifications/groupStructures',
 groupWar: 'Notifications/groupWar'}

def GetTypeGroup(typeID):
    for (groupID, typeIDs,) in groupTypes.iteritems():
        if typeID in typeIDs:
            return groupID




def CreateItemInfoLink(itemID):
    item = cfg.eveowners.Get(itemID)
    return '<a href="showinfo:%(typeID)s//%(itemID)s">%(itemName)s</a>' % {'typeID': item.typeID,
     'itemID': itemID,
     'itemName': item.name}



def CreateLocationInfoLink(locationID, locationTypeID = None):
    locationName = cfg.evelocations.Get(locationID).name
    if locationTypeID is None:
        if util.IsRegion(locationID):
            locationTypeID = const.typeRegion
        elif util.IsConstellation(locationID):
            locationTypeID = const.typeConstellation
        elif util.IsSolarSystem(locationID):
            locationTypeID = const.typeSolarSystem
        elif util.IsStation(locationID):
            if boot.role == 'client':
                stationinfo = sm.RemoteSvc('stationSvc').GetStation(locationID)
            else:
                stationinfo = sm.GetService('stationSvc').GetStation(locationID)
            locationTypeID = stationinfo.stationTypeID
    if locationTypeID is None:
        return locationName
    else:
        return '<a href="showinfo:%(typeID)s//%(locationID)s">%(locationName)s</a>' % {'typeID': locationTypeID,
         'locationID': locationID,
         'locationName': locationName}



def CreateTypeInfoLink(typeID):
    return '<a href="showinfo:%(typeID)s">%(typeName)s</a>' % {'typeID': typeID,
     'typeName': cfg.invtypes.Get(typeID).name}



def GetAgent(agentID):
    if boot.role == 'client':
        return sm.GetService('agents').GetAgentByID(agentID)
    else:
        agent = util.KeyVal(sm.GetService('agentMgr').GetAgentStaticInfo(agentID))
        station = sm.GetService('stationSvc').GetStation(agent.stationID)
        if agent.corporationID is None:
            agent.corporationID = station.ownerID
        agent.solarsystemID = station.solarSystemID
        return agent



def GetRelationshipName(level):
    if level == const.contactHighStanding:
        return localization.GetByLabel('Notifications/partRelationshipExcellent')
    if level == const.contactGoodStanding:
        return localization.GetByLabel('Notifications/partRelationshipGood')
    if level == const.contactNeutralStanding:
        return localization.GetByLabel('Notifications/partRelationshipNeutral')
    if level == const.contactBadStanding:
        return localization.GetByLabel('Notifications/partRelationshipBad')
    if level == const.contactHorribleStanding:
        return localization.GetByLabel('Notifications/partRelationshipHorrible')



def ParamCharacterTerminationNotification(notification):
    security = int(round(notification.data['security']))
    roleNameIDs = notification.data.get('roleNameIDs', None)
    if roleNameIDs is None or len(roleNameIDs) == 0:
        roleName = notification.data.get('roleName', localization.GetByLabel('UI/Generic/Person'))
    else:
        roleNames = [ localization.GetByMessageID(roleNameID) for roleNameID in roleNameIDs ]
        roleName = localizationUtil.FormatGenericList(roleNames, useConjunction=True)
    return {'securityDescription': localization.GetByLabel(securityLevelDescriptions[security], **notification.data),
     'corpName': CreateItemInfoLink(notification.data['corpID']),
     'roleName': roleName}



def ParamCharacterMedalNotification(notification):
    if boot.role == 'client':
        medalDetails = sm.GetService('medals').GetMedalDetails(notification.data['medalID'])
    else:
        medalDetails = sm.GetService('corporationSvc').GetMedalDetails(notification.data['medalID'])
    return {'issuerCorp': CreateItemInfoLink(notification.data['corpID']),
     'description': medalDetails.info[0].description,
     'title': medalDetails.info[0].title}



def ParamAllWarNotification(notification):
    return {'againstName': CreateItemInfoLink(notification.data['againstID']),
     'declaredByName': CreateItemInfoLink(notification.data['declaredByID'])}



def ParamAllWarNotificationWithCost(notification):
    return {'againstName': CreateItemInfoLink(notification.data['againstID']),
     'declaredByName': CreateItemInfoLink(notification.data['declaredByID']),
     'costText': localization.GetByLabel('Notifications/bodyWar', **notification.data) if notification.data['cost'] else ''}



def ParamSovFmtCorpID(notification):
    return {'corporation': CreateItemInfoLink(notification.data['corpID'])}



def ParamFmtFactionWarfare(notification):
    return {'corporationName': CreateItemInfoLink(notification.data['corpID']),
     'factionName': CreateItemInfoLink(notification.data['factionID'])}



def ParamFmtSovDamagedNotification(notification):
    res = {'shieldValue': notification.data['shieldValue'] * 100.0,
     'armorValue': notification.data['armorValue'] * 100.0,
     'hullValue': notification.data['hullValue'] * 100.0}
    aggressorID = notification.data.get('aggressorID', None)
    if aggressorID is not None:
        res['aggressor'] = CreateItemInfoLink(aggressorID)
    else:
        res['aggressor'] = localization.GetByLabel('UI/Common/Unknown')
    aggressorCorpID = notification.data.get('aggressorCorpID', None)
    if aggressorCorpID is not None:
        res['aggressorCorp'] = CreateItemInfoLink(aggressorCorpID)
    else:
        res['aggressorCorp'] = localization.GetByLabel('UI/Common/Unknown')
    aggressorAllID = notification.data.get('aggressorAllianceID', None)
    if aggressorAllID is not None:
        res['aggressorAlliance'] = CreateItemInfoLink(aggressorAllID)
    else:
        res['aggressorAlliance'] = localization.GetByLabel('UI/Common/NoAlliance')
    return res



def ParamFmtCorpDividendNotification(notification):
    msgID = 'Notifications/bodyCorpPayoutDividendsNonMember'
    if 'isMembers' in notification.data and notification.data['isMembers']:
        msgID = 'Notifications/bodyCorpPayoutDividendsMember'
    corpName = CreateItemInfoLink(notification.data['corpID'])
    return {'corporationName': corpName,
     'body': localization.GetByLabel(msgID, corporationName=corpName, **notification.data)}



def ParamFmtInsurancePayout(notification):
    msg = ''
    if notification.data['payout']:
        msg = localization.GetByLabel('Notifications/bodyInsurancePayoutDefault')
    return {'defaultPayoutText': msg}



def ParamCorpStructLost(notification):
    pilotText = ''
    if notification.data['ownerID']:
        pilotText = localization.GetByLabel('Notifications/bodyInfraStructureLostPilot', **notification.data)
    return {'newOwner': CreateItemInfoLink(notification.data['oldOwnerID']),
     'oldOwner': CreateItemInfoLink(notification.data['newOwnerID']),
     'pilotText': pilotText}



def ParamCorpOfficeExpiration(notification):
    if notification.data['typeID'] == const.typeOfficeFolder:
        whereText = localization.GetByLabel('Notifications/bodyCorpOfficeExpiresOffice', **notification.data)
    else:
        whereText = localization.GetByLabel('Notifications/bodyCorpOfficeExpiresItems', **notification.data)
    reasonText = ''
    if notification.data['errorText']:
        reasonText = localization.GetByLabel('Notifications/bodyCorpOfficeExpiresReason', **notification.data)
    return {'reasonText': reasonText,
     'whereText': whereText}



def PramCloneActivationNotification(notification):
    res = {}
    res['cloningServiceText'] = ''
    if notification.data['cloneStationID'] != notification.data['corpStationID']:
        res['cloningServiceText'] = localization.GetByLabel('Notifications/bodyCloneActivatedStationChange', **notification.data)
    res['lastCloneText'] = ''
    res['cloneBoughtText'] = ''
    res['spLostText'] = ''
    if notification.data['skillPointsLost'] is not None:
        res['spLostText'] = localization.GetByLabel('Notifications/bodyCloneActivatedSkillPointsLost', **notification.data)
        if notification.data['lastCloned'] is not None:
            res['lastCloneText'] = '<br><br>' + localization.GetByLabel('Notifications/bodyCloneActivatedLastCloned', **notification.data)
        if notification.data['cloneBought'] is not None:
            res['cloneBoughtText'] = '<br>' + localization.GetByLabel('Notifications/bodyCloneActivatedLastPurchased', **notification.data)
    return res



def ParamContainerPasswordNotification(notification):
    res = {}
    if notification.data['stationID'] is not None:
        res['locationName'] = localization.GetByLabel('Notifications/subjContainerLocation', **notification.data)
    else:
        res['locationName'] = CreateLocationInfoLink(notification.data['solarSystemID'])
    if notification.data['password'] is None:
        res['password'] = localization.GetByLabel('Notifications/bodyContainerPasswordChangedToBlank')
    if notification.data['passwordType'] == 'general':
        res['passwordType'] = localization.GetByLabel('UI/SystemMenu/GeneralSettings/General/Header')
    else:
        res['passwordType'] = localization.GetByLabel('UI/SystemMenu/AudioAndChat/GenericConfiguration/Header')
    return res



def ParamCustomsNotification(notification):
    standingPenaltySum = 0
    fineSum = 0
    res = {}
    res['factionName'] = CreateItemInfoLink(notification.data['factionID'])
    msg = ''
    for lost in notification.data['lostList']:
        standingPenaltySum += lost['penalty']
        fineSum += lost['fine']
        responseText = ''
        if notification.data['shouldAttack']:
            responseText = localization.GetByLabel('Notifications/bodyContrabandConfiscationResponseDeadly')
        elif notification.data['shouldConfiscate']:
            responseText = localization.GetByLabel('Notifications/bodyContrabandConfiscationResponseConfiscation')
        msg += localization.GetByLabel('Notifications/bodyContrabandConfiscationLostItems', responseText=responseText, **lost)

    res['confiscatedItems'] = msg
    res['summaryResponseText'] = ''
    if notification.data['shouldAttack']:
        res['summaryResponseText'] = localization.GetByLabel('Notifications/bodyContrabandConfiscationSummaryResponseDeadly')
    elif notification.data['shouldConfiscate']:
        res['summaryResponseText'] = localization.GetByLabel('Notifications/bodyContrabandConfiscationSummaryResponseConfiscation')
    res['ideal'] = standingPenaltySum
    res['actual'] = standingPenaltySum / notification.data['standingDivision']
    res['total'] = fineSum
    return res



def ParamInsuranceFirstShipNotification(notification):
    res = {}
    if notification.data.get('isHouseWarmingGift', 0):
        res['gift'] = CreateTypeInfoLink(const.deftypeHouseWarmingGift)
    else:
        res['gift'] = localization.GetByLabel('Notifications/bodyNoobShipNoGift')
    return res



def ParamInsuranceInvalidatedNotification(notification):
    res = {}
    reason = notification.data['reason']
    if reason == 1:
        res['reason'] = localization.GetByLabel('Notifications/bodyInsuranceInvalidNotOwnedByYou', **notification.data)
    elif reason == 2:
        res['reason'] = localization.GetByLabel('Notifications/bodyInsuranceInvalidHasExpired', **notification.data)
    elif reason == 3:
        res['reason'] = localization.GetByLabel('Notifications/bodyInsuranceInvalidNoValue', **notification.data)
    return res



def ParamSovAllClaimFailNotification(notification):
    reason = notification.data['reason']
    res = {'solarSystemID': notification.data['solarSystemID'],
     'corporation': CreateItemInfoLink(notification.data['corpID']),
     'alliance': CreateItemInfoLink(notification.data['allianceID'])}
    res['body'] = ''
    if reason == 1:
        res['body'] = localization.GetByLabel('Notifications/bodySovClaimFailedByOther', **res)
    elif reason == 2:
        res['body'] = localization.GetByLabel('Notifications/bodySovClaimFailedNoAlliance', **res)
    elif reason == 3:
        res['body'] = localization.GetByLabel('Notifications/bodySovClaimFailedBillNotPaid', **res)
    return res



def ParamAllAnchoringNotification(notification):
    res = {'corpName': CreateItemInfoLink(notification.data['corpID']),
     'allianceText': '',
     'otherTowersText': localization.GetByLabel('Notifications/bodyPOSAnchoredNoTowers')}
    if notification.data['allianceID'] is not None:
        allianceName = CreateItemInfoLink(notification.data['allianceID'])
        res['allianceText'] = localization.GetByLabel('Notifications/bodyPOSAnchoredAlliance', allianceName=allianceName)
    if notification.data['corpsPresent'] is not None and len(notification.data['corpsPresent']):
        otherTowers = localization.GetByLabel('Notifications/bodyPOSAnchoredOtherTowers')
        for corp in notification.data['corpsPresent']:
            if len(corp['towers']) > 0:
                allianceText = ''
                if corp['allianceID'] is not None:
                    allianceName = CreateItemInfoLink(corp['allianceID'])
                    allianceText = localization.GetByLabel('Notifications/bodyPOSAnchoredOthersTowerAlliance', allianceName=allianceName)
                otherTowers += localization.GetByLabel('Notifications/bodyPOSAnchoredTowersByCorp', towerCorp=CreateItemInfoLink(corp['corpID']), allianceText=allianceText)
                for tower in corp['towers']:
                    otherTowers += localization.GetByLabel('Notifications/bodyPOSAnchoredTower', **tower)

                otherTowers += '<br>'

        res['otherTowersText'] = otherTowers
    return res



def ParamJumpCloneDeleted1Notification(notification):
    res = {'destroyerID': notification.data['locationOwnerID']}
    implantListText = ''
    if len(notification.data['typeIDs']):
        implantListText += localization.GetByLabel('Notifications/bodyCloneJumpImplantDestructionHeader')
        for implantTypeID in notification.data['typeIDs']:
            msg = 'Notifications/bodyCloneJumpImplantDestructionImplantType'
            implantListText += localization.GetByLabel(msg, implantTypeID=int(implantTypeID))

    else:
        implantListText += localization.GetByLabel('Notifications/bodyCloneJumpImplantDestructionNone')
    res['implantListText'] = implantListText
    return res



def ParamJumpCloneDeleted2Notification(notification):
    res = ParamJumpCloneDeleted1Notification(notification)
    res['destroyerID'] = notification.data['destroyerID']
    return res



def ParamStoryLineMissionAvailableNotification(notification):
    agent = GetAgent(notification.senderID)
    res = {'agent_corporationName': CreateItemInfoLink(agent.corporationID),
     'agent_agentID': agent.agentID,
     'agent_stationID': agent.stationID,
     'agent_solarsystemID': agent.solarsystemID}
    notification.data.update(res)
    if agent.stationID:
        res['body'] = localization.GetByLabel('Notifications/bodyStoryLineMissionAvilableStation', **notification.data)
    else:
        res['body'] = localization.GetByLabel('Notifications/bodyStoryLineMissionAvilableSpace', **notification.data)
    return res



def ParamStationAggression1Notification(notification):
    aggressorID = notification.data['aggressorID']
    res = {'shieldDamage': int(notification.data['shieldValue'] * 100),
     'agressorText': ''}
    if aggressorID is not None:
        ownerOb = cfg.eveowners.Get(aggressorID)
        if ownerOb.IsCharacter():
            notification.data['aggressorCorpName'] = CreateItemInfoLink(notification.data['aggressorCorpID'])
            res['agressorText'] = localization.GetByLabel('Notifications/bodyOutpostAgressionAgressorCharacter', **notification.data)
        else:
            res['agressorText'] = localization.GetByLabel('Notifications/bodyOutpostAgressionAgressorOwner', owner=ownerOb.name)
    return res



def ParamStationConquerNotification(notification):
    res = {'oldCorpName': CreateItemInfoLink(notification.data['oldOwnerID']),
     'newCorpName': CreateItemInfoLink(notification.data['newOwnerID'])}
    if notification.data['charID'] is not None:
        res['characterText'] = localization.GetByLabel('Notifications/bodyOutpostConqueredCharacter', **notification.data)
    return res



def ParamStationStateChangeNotification(notification):
    state = notification.data['state']
    if state == entities.STATE_IDLE:
        return {'subject': localization.GetByLabel('Notifications/subjOutpostServiceReenabled', **notification.data)}
    if state == entities.STATE_INCAPACITATED:
        return {'subject': localization.GetByLabel('Notifications/subjOutpostServiceDisabled', **notification.data)}
    return {'subject': ''}



def ParamStationAggression2Notification(notification):
    uknMsg = localization.GetByLabel('UI/Common/Unknown')
    res = {'shieldDamage': notification.data.get('shieldValue', 0.0) * 100.0,
     'armorDamage': notification.data.get('armorValue', 0.0) * 100.0,
     'hullDamage': notification.data.get('hullValue', 0.0) * 100.0,
     'aggressor': uknMsg,
     'aggressorCorp': uknMsg,
     'aggressorAlliance': uknMsg}
    if notification.data['aggressorID'] is not None:
        res['aggressor'] = CreateItemInfoLink(notification.data['aggressorID'])
    if notification.data['aggressorCorpID'] is not None:
        res['aggressorCorp'] = CreateItemInfoLink(notification.data['aggressorCorpID'])
    aggressorAllianceID = notification.data.get('aggressorAllianceID', 0)
    if aggressorAllianceID is None:
        res['aggressorAlliance'] = localization.GetByLabel('UI/Common/CorporationNotInAlliance')
    elif aggressorAllianceID != 0:
        res['aggressorAlliance'] = CreateItemInfoLink(aggressorAllianceID)
    return res



def ParamIncursionCompletedNotification(notification):
    topTen = notification.data['topTen']
    (charIDs, discarded,) = zip(*topTen)
    cfg.eveowners.Prime(charIDs)
    res = {'topTenString': ''}
    if boot.role == 'client':
        res['constellationID'] = sm.GetService('map').GetParent(notification.data['solarSystemID'])
    else:
        solarSystemCache = sm.GetService('cache').Index(const.cacheMapSolarSystems)
        res['constellationID'] = solarSystemCache[notification.data['solarSystemID']].constellationID
    for (index, (topTenCharacterID, topTenRewardAmount,),) in enumerate(topTen):
        topTenArgs = {'number': index + 1,
         'topTenCharacterID': topTenCharacterID,
         'LPAmount': topTenRewardAmount}
        res['topTenString'] += localization.GetByLabel('Notifications/bodyIncursionCompleteTopTenEntry', **topTenArgs)

    res['journalLink'] = '<b>' + localization.GetByLabel('UI/Neocom/JournalBtn') + '</b>'
    return res



def FormatFWCharRankLossNotification(notification):
    factionID = notification.data['factionID']
    newRank = notification.data['newRank']
    (rankLabel, rankDescription,) = sm.GetService('facwar').GetRankLabel(factionID, newRank)
    message = localization.GetByLabel(rankLost[factionID], rank=rankLabel)
    return (localization.GetByLabel('UI/Generic/FormatStandingTransactions/'), message)



def FormatFWCharRankGainNotification(notification):
    factionID = notification.data['factionID']
    newRank = notification.data['newRank']
    (rankLabel, rankDescription,) = sm.GetService('facwar').GetRankLabel(factionID, newRank)
    message = localization.GetByLabel(rankGain[factionID], rank=rankLabel)
    return (localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectFacwarPromotion'), message)



def FormatAllWarDeclared(notification):
    notification.data.update(ParamAllWarNotificationWithCost(notification))
    heading = localization.GetByLabel('Notifications/subjWarDeclare', **notification.data)
    if notification.data['hostileState']:
        message = localization.GetByLabel('Notifications/bodyWarLegal', **notification.data)
    else:
        message = localization.GetByLabel('Notifications/bodyWarDelayed', **notification.data)
    return (heading, message)



def FormatLocateCharNotification(notification):
    characterID = notification.data['characterID']
    messageIndex = notification.data['messageIndex']
    agentLocation = notification.data['agentLocation']
    agentSystem = agentLocation.get(const.groupSolarSystem, None)
    agentStation = agentLocation.get(const.groupStation, None)
    targetLocation = notification.data['targetLocation']
    targetRegion = targetLocation.get(const.groupRegion, None)
    targetConstellation = targetLocation.get(const.groupConstellation, None)
    targetSystem = targetLocation.get(const.groupSolarSystem, None)
    targetStation = targetLocation.get(const.groupStation, None)
    locationText = ''
    if agentStation == targetStation:
        locationText = localization.GetByLabel('UI/Agents/Locator/InYourStation', charID=characterID)
    elif targetStation != None and agentSystem == targetSystem and agentStation != targetStation:
        locationText = localization.GetByLabel('UI/Agents/Locator/InYourSystemInStation', charID=characterID, stationName=targetStation)
    elif agentSystem == targetSystem:
        locationText = localization.GetByLabel('UI/Agents/Locator/InYourSystem', charID=characterID)
    elif targetStation == None:
        if targetRegion != None:
            locationText = localization.GetByLabel('UI/Agents/Locator/InOtherRegion', charID=characterID, systemName=targetSystem, constellationName=targetConstellation, regionName=targetRegion)
        elif targetConstellation != None:
            locationText = localization.GetByLabel('UI/Agents/Locator/InOtherConstellation', charID=characterID, systemName=targetSystem, constellationName=targetConstellation)
        elif targetSystem != None:
            locationText = localization.GetByLabel('UI/Agents/Locator/InOtherSystem', charID=characterID, systemName=targetSystem)
    elif targetRegion != None:
        locationText = localization.GetByLabel('UI/Agents/Locator/InOtherRegionInStation', charID=characterID, stationName=targetStation, systemName=targetSystem, constellationName=targetConstellation, regionName=targetRegion)
    elif targetConstellation != None:
        locationText = localization.GetByLabel('UI/Agents/Locator/InOtherConstellationInStation', charID=characterID, stationName=targetStation, systemName=targetSystem, constellationName=targetConstellation)
    elif targetSystem != None:
        locationText = localization.GetByLabel('UI/Agents/Locator/InOtherSystemInStation', charID=characterID, stationName=targetStation, systemName=targetSystem)
    title = localization.GetByLabel('UI/Agents/Locator/LocatedEmailHeader', charID=characterID, linkdata=['showinfo', cfg.eveowners.Get(characterID).typeID, characterID])
    message = localization.GetByLabel(['UI/Agents/Locator/LocatedEmailIntro1', 'UI/Agents/Locator/LocatedEmailIntro2'][messageIndex])
    message += '<br><br>'
    message += locationText
    message += '<br><br>'
    message += localization.GetByLabel('UI/Agents/Locator/LocatedEmailGoodbyeText', agentID=notification.senderID, linkdata=['showinfo', cfg.eveowners.Get(notification.senderID).typeID, notification.senderID])
    return (title, message)



def FormatBillNotification(notification):
    billTypeID = notification.data['billTypeID']
    if 'currentDate' not in notification.data:
        notification.data['currentDate'] = notification.created
    notification.data['creditorsName'] = CreateItemInfoLink(notification.data['creditorID'])
    notification.data['debtorsName'] = CreateItemInfoLink(notification.data['debtorID'])
    if billTypeID == const.billTypeMarketFine:
        messagePath = 'Notifications/bodyBillMarketFine'
    elif billTypeID == const.billTypeRentalBill:
        messagePath = 'Notifications/bodyBillRental'
    elif billTypeID == const.billTypeBrokerBill:
        messagePath = 'Notifications/bodyBillBroker'
    elif billTypeID == const.billTypeWarBill:
        notification.data['against'] = CreateItemInfoLink(notification.data['externalID'])
        messagePath = 'Notifications/bodyBillWar'
    elif billTypeID == const.billTypeAllianceMaintainanceBill:
        notification.data['allianceName'] = CreateItemInfoLink(notification.data['externalID'])
        messagePath = 'Notifications/bodyBillAllianceMaintenance'
    elif billTypeID == const.billTypeSovereignityMarker:
        messagePath = 'Notifications/bodyBillSovereignty'
    message = localization.GetByLabel(messagePath, **notification.data)
    subject = localization.GetByLabel('Notifications/subjBill', **notification.data)
    return (subject, message)



def FormatCorpNewsNotification(notification):
    notification.data['corpName'] = CreateItemInfoLink(notification.data['corpID'])
    voteType = notification.data['voteType']
    if voteType == const.voteWar:
        notification.data['parameterCorpName'] = CreateItemInfoLink(notification.data['parameter'])
        if notification.data['inEffect']:
            title = localization.GetByLabel('Notifications/subjCorpNewsAtWar', **notification.data)
        else:
            title = localization.GetByLabel('Notifications/subjCorpNewsAtPeace', **notification.data)
    elif voteType == const.voteShares:
        title = localization.GetByLabel('Notifications/subjCorpNewsCreatedShares', **notification.data)
    elif voteType == const.voteKickMember:
        title = localization.GetByLabel('Notifications/subjCorpNewsExpelsMemeber', **notification.data)
    message = notification.data['body']
    if message == '':
        message = title
    return (title, message)



def FormatTowerAlertNotification(notification):
    moonID = notification.data.get('moonID', None)
    if moonID is not None:
        notification.data['moonName'] = CreateLocationInfoLink(moonID)
    else:
        notification.data['moonName'] = localization.GetByLabel('Notifications/UnknownSystem')
    message = localization.GetByLabel('Notifications/bodyStarbaseDamageLocation', **notification.data)
    shieldValue = notification.data['shieldValue']
    armorValue = notification.data['armorValue']
    hullValue = notification.data['hullValue']
    if shieldValue is not None and armorValue is not None and hullValue is not None:
        notification.data['shieldDamage'] = int(shieldValue * 100)
        notification.data['armorDamage'] = int(armorValue * 100)
        notification.data['hullDamage'] = int(hullValue * 100)
        message += localization.GetByLabel('Notifications/bodyStarbaseDamageValues', **notification.data)
    else:
        message += localization.GetByLabel('Notifications/bodyStarbaseDamageMissing')
    if notification.data['aggressorID'] is not None:
        ownerOb = cfg.eveowners.Get(notification.data['aggressorID'])
        if ownerOb.IsCharacter():
            notification.data['agressorCorp'] = CreateItemInfoLink(notification.data['aggressorCorpID'])
            notification.data['agressorAlliance'] = '-'
            if notification.data['aggressorAllianceID'] is not None:
                notification.data['agressorAlliance'] = CreateItemInfoLink(notification.data['aggressorAllianceID'])
            message += localization.GetByLabel('Notifications/bodyStarbaseDamageAttacker', **notification.data)
        else:
            aggressorName = CreateItemInfoLink(notification.data['aggressorID'])
        message += localization.GetByLabel('Notifications/bodyStarbaseDamageAgressorNotCharacter', aggressorName=aggressorName)
    return (localization.GetByLabel('Notifications/subjStarbaseDamage', **notification.data), message)



def FormatTutorialNotification(notification):
    agent = GetAgent(notification.senderID)
    notification.data['charID'] = notification.receiverID
    notification.data['corpName'] = CreateItemInfoLink(agent.corporationID)
    notification.data['stationID'] = agent.stationID
    notification.data['agentID'] = agent.agentID
    title = localization.GetByLabel('Notifications/subjTutorial')
    message = localization.GetByLabel('Notifications/bodyTutorial', **notification.data)
    return (title, message)



def FormatTowerResourceAlertNotification(notification):
    if notification.data['corpID']:
        corpName = CreateItemInfoLink(notification.data['corpID'])
        msg = localization.GetByLabel('Notifications/bodyStarbaseLowResourcesCorp', corpName=corpName)
        if notification.data['allianceID'] is not None:
            allianceName = CreateItemInfoLink(notification.data['allianceID'])
            msg += localization.GetByLabel('Notifications/bodyStarbaseLowResourcesAlliance', allianceName=allianceName)
        notification.data['corpAllianceText'] = msg
    else:
        notification.data['corpAllianceText'] = ''
    message = localization.GetByLabel('Notifications/bodyStarbaseLowResources', **notification.data)
    for want in notification.data['wants']:
        message += localization.GetByLabel('Notifications/bodyStarbaseLowResourcesWants', **want)

    return (localization.GetByLabel('Notifications/subjStarbaseLowResources', **notification.data), message)



def FormatOrbitalAttackedNotification(notification):
    uknMsg = localization.GetByLabel('UI/Common/Unknown')
    res = {'shieldValue': notification.data.get('shieldLevel', 0.0) * 100.0,
     'planetID': notification.data['planetID'],
     'planetLinkArgs': ['showinfo', notification.data['planetTypeID'], notification.data['planetID']],
     'typeID': notification.data['typeID'],
     'solarSystemID': notification.data['solarSystemID'],
     'aggressor': notification.data['aggressorID'],
     'aggressorCorp': uknMsg,
     'aggressorAlliance': uknMsg}
    if notification.data['aggressorCorpID'] is not None:
        res['aggressorCorp'] = CreateItemInfoLink(notification.data['aggressorCorpID'])
    aggressorAllianceID = notification.data.get('aggressorAllianceID', 0)
    if aggressorAllianceID is None:
        res['aggressorAlliance'] = localization.GetByLabel('UI/Common/CorporationNotInAlliance')
    elif aggressorAllianceID != 0:
        res['aggressorAlliance'] = CreateItemInfoLink(aggressorAllianceID)
    return res



def FormatOrbitalReinforcedNotification(notification):
    uknMsg = localization.GetByLabel('UI/Common/Unknown')
    res = {'reinforceExitTime': notification.data['reinforceExitTime'],
     'planetID': notification.data['planetID'],
     'planetLinkArgs': ['showinfo', notification.data['planetTypeID'], notification.data['planetID']],
     'typeID': notification.data['typeID'],
     'solarSystemID': notification.data['solarSystemID'],
     'aggressor': notification.data['aggressorID'],
     'aggressorCorp': uknMsg,
     'aggressorAlliance': uknMsg}
    if notification.data['aggressorCorpID'] is not None:
        res['aggressorCorp'] = CreateItemInfoLink(notification.data['aggressorCorpID'])
    aggressorAllianceID = notification.data.get('aggressorAllianceID', 0)
    if aggressorAllianceID is None:
        res['aggressorAlliance'] = localization.GetByLabel('UI/Common/CorporationNotInAlliance')
    elif aggressorAllianceID != 0:
        res['aggressorAlliance'] = CreateItemInfoLink(aggressorAllianceID)
    return res


formatters = {notifyIDs.notificationTypeOldLscMessages: ('Notifications/subjLegacy', 'Notifications/bodyLegacy'),
 notifyIDs.notificationTypeCharTerminationMsg: ('Notifications/subjCharacterTermination', 'Notifications/bodyCharacterTermination', ParamCharacterTerminationNotification),
 notifyIDs.notificationTypeCharMedalMsg: ('Notifications/subjCharacterMedal', 'Notifications/bodyCharacterMedal', ParamCharacterMedalNotification),
 notifyIDs.notificationTypeAllMaintenanceBillMsg: ('Notifications/subjMaintenanceBill', 'Notifications/bodyMaintenanceBill', lambda d: {'allianceName': CreateItemInfoLink(d.data['allianceID'])}),
 notifyIDs.notificationTypeAllWarDeclaredMsg: FormatAllWarDeclared,
 notifyIDs.notificationTypeAllWarSurrenderMsg: ('Notifications/subjWarSurender', 'Notifications/bodyWarSunrender', ParamAllWarNotification),
 notifyIDs.notificationTypeAllWarRetractedMsg: ('Notifications/subjWarRetracts', 'Notifications/bodyWarRetract', ParamAllWarNotification),
 notifyIDs.notificationTypeAllWarInvalidatedMsg: ('Notifications/subjWarConcordInvalidates', 'Notifications/bodyWarConcordInvalidates', ParamAllWarNotification),
 notifyIDs.notificationTypeCharBillMsg: FormatBillNotification,
 notifyIDs.notificationTypeCorpAllBillMsg: FormatBillNotification,
 notifyIDs.notificationTypeBillOutOfMoneyMsg: ('Notifications/subjBillOutOfMoney', 'Notifications/bodyBillOutOfMoney', lambda d: {'billType': cfg.billtypes.Get(d.data['billTypeID']).billTypeName}),
 notifyIDs.notificationTypeBillPaidCharMsg: ('Notifications/subjBillPaid', 'Notifications/bodyBillPaid'),
 notifyIDs.notificationTypeBillPaidCorpAllMsg: ('Notifications/subjBillPaid', 'Notifications/bodyBillPaid'),
 notifyIDs.notificationTypeBountyClaimMsg: ('Notifications/subjBountyPayment', 'Notifications/bodyBountyPayment'),
 notifyIDs.notificationTypeCloneActivationMsg: ('Notifications/subjCloneActivated', 'Notifications/bodyCloneActivated', PramCloneActivationNotification),
 notifyIDs.notificationTypeCorpAppNewMsg: ('Notifications/subjCorpApplicationNew', 'Notifications/bodyApplicationNew'),
 notifyIDs.notificationTypeCorpAppRejectMsg: ('Notifications/subjCorpAppRejected', 'Notifications/bodyCorpAppRejected', lambda d: {'corporationName': CreateItemInfoLink(d.data['corpID'])}),
 notifyIDs.notificationTypeCorpAppAcceptMsg: ('Notifications/subjCorpAppAccepted', 'Notifications/bodyCorpAppAccepted', lambda d: {'corporationName': CreateItemInfoLink(d.data['corpID'])}),
 notifyIDs.notificationTypeCorpKicked: ('Notifications/Corporations/KickedTitle', 'Notifications/Corporations/KickedBody', lambda d: {'corporationName': CreateItemInfoLink(d.data['corpID'])}),
 notifyIDs.notificationTypeCorpTaxChangeMsg: ('Notifications/subjCorpTaxRateChange', 'Notifications/bodyCorpTaxRateChange', lambda d: {'corporationName': CreateItemInfoLink(d.data['corpID'])}),
 notifyIDs.notificationTypeCorpNewsMsg: FormatCorpNewsNotification,
 notifyIDs.notificationTypeCharLeftCorpMsg: ('Notifications/subjCharLeftCorp', 'Notifications/bodyCharLeftCorp', lambda d: {'corporationName': CreateItemInfoLink(d.data['corpID'])}),
 notifyIDs.notificationTypeCorpNewCEOMsg: ('Notifications/subjCEOQuit', 'Notifications/bodyCEOQuit', lambda d: {'corporationName': CreateItemInfoLink(d.data['corpID'])}),
 notifyIDs.notificationTypeCorpLiquidationMsg: ('Notifications/subjCorpLiquidation', 'Notifications/bodyCorpLiquidation', lambda d: {'corporationName': CreateItemInfoLink(d.data['corpID'])}),
 notifyIDs.notificationTypeCorpDividendMsg: ('Notifications/subjCorpPayoutDividends', 'Notifications/bodyLegacy', ParamFmtCorpDividendNotification),
 notifyIDs.notificationTypeCorpVoteMsg: ('Notifications/subjCorpVote', 'Notifications/bodyLegacy'),
 notifyIDs.notificationTypeCorpVoteCEORevokedMsg: ('Notifications/subjCEORollRevoked', 'Notifications/bodyCEORollRevoked', lambda d: {'corporationName': CreateItemInfoLink(d.data['corpID'])}),
 notifyIDs.notificationTypeCorpWarDeclaredMsg: ('Notifications/subjWarDeclare', 'Notifications/bodyWarDeclare', ParamAllWarNotificationWithCost),
 notifyIDs.notificationTypeCorpWarFightingLegalMsg: ('Notifications/subjWarDeclare', 'Notifications/bodyWarLegal', ParamAllWarNotificationWithCost),
 notifyIDs.notificationTypeCorpWarSurrenderMsg: ('Notifications/subjWarSurender', 'Notifications/bodyWarSunrender', ParamAllWarNotification),
 notifyIDs.notificationTypeCorpWarRetractedMsg: ('Notifications/subjWarRetracts', 'Notifications/bodyWarRetract', ParamAllWarNotification),
 notifyIDs.notificationTypeCorpWarInvalidatedMsg: ('Notifications/subjWarConcordInvalidates', 'Notifications/bodyWarConcordInvalidates', ParamAllWarNotification),
 notifyIDs.notificationTypeContainerPasswordMsg: ('Notifications/subjContainerPasswordChanged', 'Notifications/bodyContainerPasswordChanged', ParamContainerPasswordNotification),
 notifyIDs.notificationTypeCustomsMsg: ('Notifications/subjContrabandConfiscation', 'Notifications/bodyContrabandConfiscation', ParamCustomsNotification),
 notifyIDs.notificationTypeInsuranceFirstShipMsg: ('Notifications/subjNoobShip', 'Notifications/bodyNoobShip', ParamInsuranceFirstShipNotification),
 notifyIDs.notificationTypeInsurancePayoutMsg: ('Notifications/subjInsurancePayout', 'Notifications/bodyInsurancePayout', ParamFmtInsurancePayout),
 notifyIDs.notificationTypeInsuranceInvalidatedMsg: ('Notifications/subjInsuranceInvalid', 'Notifications/bodyInsuranceInvalid', ParamInsuranceInvalidatedNotification),
 notifyIDs.notificationTypeSovAllClaimFailMsg: ('Notifications/subjSovClaimFailed', 'Notifications/bodyLegacy', ParamSovAllClaimFailNotification),
 notifyIDs.notificationTypeSovCorpClaimFailMsg: ('Notifications/subjSovClaimFailed', 'Notifications/bodyLegacy', ParamSovAllClaimFailNotification),
 notifyIDs.notificationTypeSovAllBillLateMsg: ('Notifications/subjSovBillLate', 'Notifications/bodySovBillLate', lambda d: {'corporation': CreateItemInfoLink(d.data['corpID'])}),
 notifyIDs.notificationTypeSovCorpBillLateMsg: ('Notifications/subjSovBillLate', 'Notifications/bodySovBillLate', lambda d: {'corporation': CreateItemInfoLink(d.data['corpID'])}),
 notifyIDs.notificationTypeSovAllClaimLostMsg: ('Notifications/subjSovAllianceClaimLost', 'Notifications/bodySovAllianceClaimLost'),
 notifyIDs.notificationTypeSovCorpClaimLostMsg: ('Notifications/subjSovCorporationClaimLost', 'Notifications/bodySovCorporationClaimLost'),
 notifyIDs.notificationTypeSovAllClaimAquiredMsg: ('Notifications/subjSovClaimAquiredAlliance', 'Notifications/bodySovClaimAquiredAlliance', lambda d: {'corporation': CreateItemInfoLink(d.data['corpID']),
                                                    'alliance': CreateItemInfoLink(d.data['allianceID'])}),
 notifyIDs.notificationTypeSovCorpClaimAquiredMsg: ('Notifications/subjSovClaimAquiredCorporation', 'Notifications/bodySovClaimAquiredCorporation', lambda d: {'corporation': CreateItemInfoLink(d.data['corpID']),
                                                     'alliance': CreateItemInfoLink(d.data['allianceID'])}),
 notifyIDs.notificationTypeAllAnchoringMsg: ('Notifications/subjPOSAnchored', 'Notifications/bodyPOSAnchored', ParamAllAnchoringNotification),
 notifyIDs.notificationTypeAllStructVulnerableMsg: ('Notifications/subjSovVulnerable', 'Notifications/bodySovVulnerable'),
 notifyIDs.notificationTypeAllStrucInvulnerableMsg: ('Notifications/subjSovNotVulnerable', 'Notifications/bodySovNotVulnerable'),
 notifyIDs.notificationTypeSovDisruptorMsg: ('Notifications/subjSovDisruptionDetected', 'Notifications/bodySovDisruptionDetected'),
 notifyIDs.notificationTypeCorpStructLostMsg: ('Notifications/subjInfraStructureLost', 'Notifications/bodyInfraStructureLost', ParamCorpStructLost),
 notifyIDs.notificationTypeCorpOfficeExpirationMsg: ('Notifications/SubjCorpOfficeExpires', 'Notifications/bodyCorpOfficeExpires', ParamCorpOfficeExpiration),
 notifyIDs.notificationTypeCloneRevokedMsg1: ('Notifications/subjClone', 'Notifications/bodyCloneRevoked1', lambda d: {'managerStation': CreateItemInfoLink(d.data['corpID'])}),
 notifyIDs.notificationTypeCloneMovedMsg: ('Notifications/subjClone', 'Notifications/bodyCloneMoved', lambda d: {'corporation': CreateItemInfoLink(d.data['charsInCorpID']),
                                            'managerStation': CreateItemInfoLink(d.data['corpID'])}),
 notifyIDs.notificationTypeCloneRevokedMsg2: ('Notifications/subjClone', 'Notifications/bodyCloneRevoke2', lambda d: {'managerStation': CreateItemInfoLink(d.data['corpID'])}),
 notifyIDs.notificationTypeInsuranceExpirationMsg: ('Notifications/subjInsuranceExpired', 'Notifications/bodyInsuranceExpired'),
 notifyIDs.notificationTypeInsuranceIssuedMsg: ('Notifications/subjInsuranceIssued', 'Notifications/bodyInsuranceIssued', lambda d: {'typeID2': d.data['typeID']}),
 notifyIDs.notificationTypeJumpCloneDeletedMsg1: ('Notifications/subjCloneJumpImplantDestruction', 'Notifications/bodyCloneJumpImplantDestruction', ParamJumpCloneDeleted1Notification),
 notifyIDs.notificationTypeJumpCloneDeletedMsg2: ('Notifications/subjCloneJumpImplantDestruction', 'Notifications/bodyCloneJumpImplantDestruction', ParamJumpCloneDeleted2Notification),
 notifyIDs.notificationTypeFWCorpJoinMsg: ('Notifications/subjFacWarCorpJoin', 'Notifications/bodyFacWarCorpJoin', ParamFmtFactionWarfare),
 notifyIDs.notificationTypeFWCorpLeaveMsg: ('Notifications/subjFacWarCorpLeave', 'Notifications/bodyFacWarCorpLeave', ParamFmtFactionWarfare),
 notifyIDs.notificationTypeFWCorpKickMsg: ('Notifications/subjFacWarCorpKicked', 'Notifications/bodyFacWarCorpKicked', ParamFmtFactionWarfare),
 notifyIDs.notificationTypeFWCharKickMsg: ('Notifications/subjFacWarCharKicked', 'Notifications/bodyFacWarCharKicked', ParamFmtFactionWarfare),
 notifyIDs.notificationTypeFWCorpWarningMsg: ('Notifications/subjFacWarCorpWarrning', 'Notifications/bodyFacWarCorpWarrning', ParamFmtFactionWarfare),
 notifyIDs.notificationTypeFWCharWarningMsg: ('Notifications/subjFacWarCharWarrning', 'Notifications/bodyFacWarCharWarrning', ParamFmtFactionWarfare),
 notifyIDs.notificationTypeFWCharRankLossMsg: FormatFWCharRankLossNotification,
 notifyIDs.notificationTypeFWCharRankGainMsg: FormatFWCharRankGainNotification,
 notifyIDs.notificationTypeAgentMoveMsg: ('Notifications/subjLegacy', 'Notifications/bodyLegacy'),
 notifyIDs.notificationTypeTransactionReversalMsg: ('Notifications/subjMassReversal', 'Notifications/bodyLegacy'),
 notifyIDs.notificationTypeReimbursementMsg: ('Notifications/subjLegacy', 'Notifications/bodyLegacy'),
 notifyIDs.notificationTypeLocateCharMsg: FormatLocateCharNotification,
 notifyIDs.notificationTypeResearchMissionAvailableMsg: ('Notifications/subjResearchMissionAvailable', 'Notifications/bodyResearchMissionAvailable'),
 notifyIDs.notificationTypeMissionOfferExpirationMsg: ('Notifications/subjLegacy', 'Notifications/bodyLegacy', lambda d: {'subject': d.data['header']}),
 notifyIDs.notificationTypeMissionTimeoutMsg: ('Notifications/subjMissionTimeout', 'Notifications/bodyMissionTimeout'),
 notifyIDs.notificationTypeStoryLineMissionAvailableMsg: ('Notifications/subjStoryLineMissionAvilable', 'Notifications/bodyLegacy', ParamStoryLineMissionAvailableNotification),
 notifyIDs.notificationTypeTowerAlertMsg: FormatTowerAlertNotification,
 notifyIDs.notificationTypeTowerResourceAlertMsg: FormatTowerResourceAlertNotification,
 notifyIDs.notificationTypeStationAggressionMsg1: ('Notifications/subjOutpostAgression', 'Notifications/bodyOutpostAgression', ParamStationAggression1Notification),
 notifyIDs.notificationTypeStationStateChangeMsg: ('Notifications/subjLegacy', 'Notifications/bodyOutpostService', ParamStationStateChangeNotification),
 notifyIDs.notificationTypeStationConquerMsg: ('Notifications/subjOutpostConquered', 'Notifications/bodyOutpostConquered', ParamStationConquerNotification),
 notifyIDs.notificationTypeStationAggressionMsg2: ('Notifications/subjOutpostAgressed', 'Notifications/bodyOutpostAgressed', ParamStationAggression2Notification),
 notifyIDs.notificationTypeFacWarCorpJoinRequestMsg: ('Notifications/subjFacWarCorpJoinRequest', 'Notifications/bodyFacWarCorpJoinRequest', ParamFmtFactionWarfare),
 notifyIDs.notificationTypeFacWarCorpLeaveRequestMsg: ('Notifications/subjFacWarCorpLeaveRequest', 'Notifications/bodyFacWarCorpLeaveRequest', ParamFmtFactionWarfare),
 notifyIDs.notificationTypeFacWarCorpJoinWithdrawMsg: ('Notifications/subjFacWarCorpJoinWithdraw', 'Notifications/bodyFacWarCorpJoinWithdraw', ParamFmtFactionWarfare),
 notifyIDs.notificationTypeFacWarCorpLeaveWithdrawMsg: ('Notifications/subjFacWarCorpLeaveWithdraw', 'Notifications/bodyjFacWarCorpLeaveWithdraw', ParamFmtFactionWarfare),
 notifyIDs.notificationTypeSovereigntyTCUDamageMsg: ('Notifications/subjSovTCUDamaged', 'Notifications/bodySovTCUDamaged', ParamFmtSovDamagedNotification),
 notifyIDs.notificationTypeSovereigntySBUDamageMsg: ('Notifications/subjSovSBUDamaged', 'Notifications/bodySovSBUDamaged', ParamFmtSovDamagedNotification),
 notifyIDs.notificationTypeSovereigntyIHDamageMsg: ('Notifications/subjSovIHDamaged', 'Notifications/bodySovIHDamaged', ParamFmtSovDamagedNotification),
 notifyIDs.notificationTypeContactAdd: ('Notifications/subjContactAdd', 'Notifications/bodyContactAdd', lambda d: {'messageText': d.data.get('message', ''),
                                         'level': GetRelationshipName(d.data['level'])}),
 notifyIDs.notificationTypeContactEdit: ('Notifications/subjContactEdit', 'Notifications/bodyContactEdit', lambda d: {'messageText': d.data.get('message', ''),
                                          'level': GetRelationshipName(d.data['level'])}),
 notifyIDs.notificationTypeIncursionCompletedMsg: ('Notifications/subjIncursionComplete', 'Notifications/bodyIncursionComplete', ParamIncursionCompletedNotification),
 notifyIDs.notificationTypeTutorialMsg: FormatTutorialNotification,
 notifyIDs.notificationTypeOrbitalAttacked: ('Notifications/subjOrbitalAttacked', 'Notifications/bodyOrbitalAttacked', FormatOrbitalAttackedNotification),
 notifyIDs.notificationTypeOrbitalReinforced: ('Notifications/subjOrbitalReinforced', 'Notifications/bodyOrbitalReinforced', FormatOrbitalReinforcedNotification),
 notifyIDs.notificationTypeOwnershipTransferred: ('Notifications/subjOwnershipTransferred', 'Notifications/bodyOwnershipTransferred')}

def Format(notification):
    if notification.typeID in formatters:
        try:
            if type(notification.data) in types.StringTypes:
                notification.data = yaml.load(notification.data, Loader=yaml.CSafeLoader)
            if type(formatters[notification.typeID]) is types.TupleType:
                if type(notification.data) is types.DictType:
                    notification.data['notification_senderID'] = notification.senderID
                    notification.data['notification_receiverID'] = notification.receiverID
                    notification.data['notification_created'] = notification.created
                    if len(formatters[notification.typeID]) > 2:
                        funcDict = formatters[notification.typeID][2](notification)
                        if type(funcDict) is types.DictType:
                            notification.data.update(funcDict)
                        else:
                            log.LogException('Parameter Processor failed to return a Dic of data for formatter typeID=%s' % notification.typeID)
                    subject = localization.GetByLabel(formatters[notification.typeID][0], **notification.data)
                    body = localization.GetByLabel(formatters[notification.typeID][1], **notification.data)
                else:
                    log.LogException('No formatter found for typeID=%s %s' % (notification.typeID, type(notification.data)))
                    subject = localization.GetByLabel('Notifications/subjBadNotificationMessage')
                    body = localization.GetByLabel('Notifications/bodyBadNotificationMessage', id=notification.notificationID)
            else:
                (subject, body,) = formatters[notification.typeID](notification)
        except Exception as e:
            log.LogException('Error processing notification=%s, error=%s' % (str(notification), e))
            sys.exc_clear()
            subject = localization.GetByLabel('Notifications/subjBadNotificationMessage')
            body = localization.GetByLabel('Notifications/bodyBadNotificationMessage', id=notification.notificationID)
        return (subject, body)
    else:
        log.LogException('No formatter found for typeID=%s' % notification.typeID)
        subject = localization.GetByLabel('Notifications/subjBadNotificationMessage')
        body = localization.GetByLabel('Notifications/bodyBadNotificationMessage', id=notification.notificationID)
        return (subject, body)


exports = util.AutoExports('const', notificationTypes)
exports['notificationUtil.GetTypeGroup'] = GetTypeGroup
exports['notificationUtil.Format'] = Format
exports['notificationUtil.groupTypes'] = groupTypes
exports['notificationUtil.groupNamePaths'] = groupNamePaths
exports['const.notificationGroupUnread'] = groupUnread
exports['const.groupContacts'] = groupContacts

