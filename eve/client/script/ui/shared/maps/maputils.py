import util
import types
import trinity
import localization

def GetValidSolarsystemGroups():
    return [const.groupSun,
     const.groupScannerProbe,
     const.groupPlanet,
     const.groupMoon,
     const.groupStation,
     const.groupAsteroidBelt,
     const.groupBeacon,
     const.groupStargate,
     const.groupSovereigntyClaimMarkers,
     const.groupSovereigntyDisruptionStructures,
     'bookmark',
     'scanresult']



def GetVisibleSolarsystemBrackets():
    return settings.user.ui.Get('groupsInSolarsystemMap', GetValidSolarsystemGroups())



def GetHintsOnSolarsystemBrackets():
    return settings.user.ui.Get('hintsInSolarsystemMap', [const.groupStation])



def GetMyPos():
    bp = sm.GetService('michelle').GetBallpark()
    if bp and bp.ego:
        ego = bp.balls[bp.ego]
        myPos = trinity.TriVector(ego.x, ego.y, ego.z)
    elif eve.session.stationid:
        s = sm.RemoteSvc('stationSvc').GetStation(eve.session.stationid)
        myPos = trinity.TriVector(s.x, s.y, s.z)
    else:
        myPos = trinity.TriVector()
    return myPos



def GetDistance(slimItem = None, mapData = None, ball = None, transform = None):
    if ball:
        return ball.surfaceDist
    if slimItem:
        ballPark = sm.GetService('michelle').GetBallpark()
        if ballPark and slimItem.itemID in ballPark.balls:
            return ballPark.balls[slimItem.itemID].surfaceDist
    myPos = GetMyPos()
    if mapData:
        pos = trinity.TriVector(mapData.x, mapData.y, mapData.z)
    elif transform:
        pos = transform.translation
        if type(pos) == types.TupleType:
            pos = trinity.TriVector(*pos)
    else:
        return None
    return (pos - myPos).Length()



def GetNameFromMapCache(messageID, messageType = None):
    return localization.GetByMessageID(messageID)


exports = util.AutoExports('maputils', locals())

