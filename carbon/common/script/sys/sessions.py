from __future__ import with_statement
import blue
import bluepy
import uthread
import weakref
import log
import copy
import types
import util
import macho
import sys
import service
import base
import const
import uuid
from collections import deque
from service import *
SESSIONCHANGEDELAY = 30 * const.SEC

def GetSessionChangeTimer(role):
    delay = SESSIONCHANGEDELAY
    if role and role & ROLE_GML > 0 and macho.mode == 'client' and prefs.GetValue('sessionChangeTimer', 0) > 0:
        delay = min(max(prefs.GetValue('sessionChangeTimer', 0), 5), 60)
        delay *= const.SEC
    return delay


allObjectConnections = weakref.WeakKeyDictionary({})
allConnectedObjects = weakref.WeakKeyDictionary({})
dyingObjects = deque()

def ObjectKillah():
    n = 0
    while 1:
        maxNumObjects = prefs.GetValue('objectKillahMaxObjects', -1)
        sleepTime = prefs.GetValue('objectKillahSleepTime', 30)
        if dyingObjects and (maxNumObjects <= 0 or n < maxNumObjects):
            delay = (dyingObjects[0][0] - blue.os.GetTime()) / SEC
            delay = min(delay, 30)
            if delay > 0:
                blue.pyos.synchro.Sleep(1000 * delay)
            else:
                (dietime, diediedie,) = dyingObjects.popleft()
                try:
                    with bluepy.Timer('sessions::' + diediedie.GetObjectConnectionLogClass()):
                        diediedie.DisconnectObject()
                except Exception:
                    log.LogException()
                    sys.exc_clear()
                del diediedie
                n += 1
        else:
            if maxNumObjects > 0 and n >= maxNumObjects:
                log.general.Log("ObjectKillah killed the maximum number of allowed objects for this round, %d, which means that we're lagging behind! Sleeping for %d seconds" % (maxNumObjects, sleepTime), log.LGWARN)
            elif n > 0:
                if maxNumObjects > 0:
                    log.general.Log('ObjectKillah killed %d objects for this round out of a maximum of %d. Sleeping for %d seconds' % (n, maxNumObjects, sleepTime), log.LGINFO)
                else:
                    log.general.Log('ObjectKillah killed %d objects for this round. Sleeping for %d seconds' % (n, sleepTime), log.LGINFO)
            n = 0
            blue.pyos.synchro.Sleep(1000 * sleepTime)



uthread.new(ObjectKillah).context = 'sessions::ObjectKillah'

def GetUndeadObjects():
    global allSessionsBySID
    global allConnectedObjects
    global allObjectConnections
    from util import allMonikers
    while 1:
        obs = []
        for each in allConnectedObjects.iterkeys():
            obs.append(each)

        break

    while 1:
        con = []
        for each in allObjectConnections.iterkeys():
            con.append(each)

        break

    while 1:
        ses = []
        for each in allSessionsBySID.itervalues():
            ses.append(each)

        break

    while 1:
        mon = []
        for each in allMonikers.iterkeys():
            mon.append(each)

        break

    zombies = []
    bombies = []
    for each in con:
        liveone = 0
        for other in ses:
            for yetanother in other.connectedObjects.itervalues():
                if each is yetanother[0]:
                    liveone = 1
                    break


        if not liveone:
            for other in mon:
                if other.boundObject is each:
                    liveone = 1
                    break

        if not liveone:
            zombies.append(each)

    for each in obs:
        liveone = 0
        for other in con:
            if other.__object__ is each:
                liveone = 1
                for yetanother in zombies:
                    if yetanother is other:
                        liveone = 2

                if liveone:
                    break

        if not liveone:
            zombies.append(each)
        elif liveone == 2:
            bombies.append(each)

    return (zombies, bombies)



class MasqueradeMask(object):

    def __init__(self, props):
        self._MasqueradeMask__prevStorage = UpdateLocalStorage(props)



    def __enter__(self):
        pass



    def __exit__(self, e, v, tb):
        self.UnMask()



    def UnMask(self):
        SetLocalStorage(self._MasqueradeMask__prevStorage)
        self._MasqueradeMask__prevStorage = None



callTimerKeys = {}
serviceCallTimes = {}
webCallTimes = {}
userCallTimes = {}
outstandingCallTimers = []

class RealCallTimer():

    def __init__(self, k):
        k = callTimerKeys.setdefault(k, k)
        self.key = k
        UpdateLocalStorage({'calltimer.key': k})
        if not session:
            self.mask = GetServiceSession('DefaultCallTimer').Masquerade()
        else:
            self.mask = None
        self.start = blue.os.GetTime(1)
        outstandingCallTimers.append((k, self.start))



    def Done(self):
        stop = blue.os.GetTime(1)
        t = stop - self.start
        if t < 0:
            log.general.Log('blue.os.GetTime(1) is running backwards... now=%s, start=%s' % (stop, self.start), 2, 1)
            t = 0
        if session and not session.role & ROLE_SERVICE:
            if getattr(session, 'clientID', 0):
                other = userCallTimes
            else:
                other = webCallTimes
        else:
            other = serviceCallTimes
        for calltimes in (session.calltimes, other):
            if self.key not in calltimes:
                theCallTime = [0,
                 0,
                 -1,
                 -1,
                 0,
                 0]
                calltimes[self.key] = theCallTime
            else:
                theCallTime = calltimes[self.key]
            theCallTime[0] += 1
            theCallTime[1] += t
            if theCallTime[2] == -1 or t < theCallTime[2]:
                theCallTime[2] = t
            if theCallTime[3] == -1 or t > theCallTime[3]:
                theCallTime[3] = t

        if self.mask:
            self.mask.UnMask()
        try:
            outstandingCallTimers.remove((self.key, self.start))
        except:
            sys.exc_clear()



    def __enter__(self):
        pass



    def __exit__(self, e, v, tb):
        self.Done()




class DummyCallTimer(object):

    def __init__(self, k):
        pass



    def Done(self):
        pass



    def __enter__(self):
        pass



    def __exit__(self, e, v, tb):
        pass



CallTimer = DummyCallTimer

def EnableCallTimers(on):
    global CallTimer
    was = CallTimer == RealCallTimer
    CallTimer = RealCallTimer if on else DummyCallTimer
    import base
    base.CallTimer = CallTimer
    return was



def CallTimersEnabled():
    was = CallTimer == RealCallTimer
    return was



def GetCallTimes():
    return (userCallTimes, serviceCallTimes, webCallTimes)



class CoreSession():
    __guid__ = 'base.CoreSession'
    __persistvars__ = ['userid',
     'languageID',
     'role',
     'charid',
     'address',
     'userType',
     'maxSessionTime']
    __nonpersistvars__ = ['sid',
     'c2ooid',
     'connectedObjects',
     'clientID']
    __attributesWithDefaultValueOfZero__ = []

    def __init__(self, sid, role, defaultVarList = []):
        d = self.__dict__
        d['additionalNoSetAttributes'] = []
        defaultVarList = self.__persistvars__ + defaultVarList
        for attName in defaultVarList:
            d[attName] = self.GetDefaultValueOfAttribute(attName)

        d['version'] = 1
        d['sid'] = sid
        d['role'] = None
        d['c2ooid'] = 1
        d['connectedObjects'] = {}
        d['calltimes'] = {}
        d['notificationID'] = 0L
        d['machoObjectsByID'] = {}
        d['machoObjectConnectionsByObjectID'] = {}
        d['sessionVariables'] = {}
        d['lastRemoteCall'] = blue.os.GetTime()
        d['nextSessionChange'] = None
        d['sessionChangeReason'] = 'Initial State'
        d['rwlock'] = uthread.RWLock(('sessions', sid))
        d['sessionhist'] = []
        d['hasproblems'] = 0
        d['mutating'] = 0
        d['changing'] = None
        d['additionalDistributedProps'] = []
        d['additionalNonIntegralAttributes'] = []
        d['longAttributes'] = []
        d['additionalAttributesToPrint'] = []
        d['additionalHexAttributes'] = []
        self._CoreSession__ChangeAttribute('role', role)
        self.LogSessionHistory('Session created')



    def IsMutating(self):
        return self.mutating



    def IsChanging(self):
        return self.changing is not None



    def IsItSafe(self):
        return not (self.IsMutating() or self.IsChanging())



    def IsItSemiSafe(self):
        return self.IsItSafe() or self.IsMutating() and self.IsChanging()



    def WaitUntilSafe(self):
        if session.IsItSafe():
            return 
        timeWaited = 0
        while timeWaited <= 30000 and not session.IsItSafe():
            blue.pyos.synchro.Sleep(100)
            timeWaited += 100

        if not session.IsItSafe():
            raise RuntimeError('Session did not become safe within 30secs')



    def RegisterMachoObjectConnection(self, objectID, connection, refID):
        connectionID = GetObjectUUID(connection)
        if objectID not in self.machoObjectConnectionsByObjectID:
            self.machoObjectConnectionsByObjectID[objectID] = [0, weakref.WeakValueDictionary({})]
        self.machoObjectConnectionsByObjectID[objectID][1][connectionID] = connection
        self.machoObjectConnectionsByObjectID[objectID][0] = max(self.machoObjectConnectionsByObjectID[objectID][0], refID)



    def UnregisterMachoObjectConnection(self, objectID, connection):
        connectionID = GetObjectUUID(connection)
        if objectID not in self.machoObjectConnectionsByObjectID:
            return None
        else:
            if connectionID in self.machoObjectConnectionsByObjectID[objectID][1]:
                log.LogTraceback('Unexpected Crapola:  connectionID still found in machoObjectConnectionsByObjectID[objectID]')
                del self.machoObjectConnectionsByObjectID[objectID][1][connectionID]
            if not self.machoObjectConnectionsByObjectID[objectID][1]:
                refID = self.machoObjectConnectionsByObjectID[objectID][0]
                del self.machoObjectConnectionsByObjectID[objectID]
                return refID
            return None



    def RegisterMachoObject(self, objectID, object, refID):
        if objectID not in sessionsByAttribute['objectID']:
            sessionsByAttribute['objectID'][objectID] = {self.sid: refID}
        else:
            sessionsByAttribute['objectID'][objectID][self.sid] = max(refID, sessionsByAttribute['objectID'][objectID].get(self.sid, 0))
        if objectID in self.machoObjectsByID:
            self.machoObjectsByID[objectID][0] = max(refID, self.machoObjectsByID[objectID][0])
        else:
            self.machoObjectsByID[objectID] = [refID, object]



    def UnregisterMachoObject(self, objectID, refID, suppressnotification = 1):
        try:
            if objectID in self.machoObjectConnectionsByObjectID:
                del self.machoObjectConnectionsByObjectID[objectID]
            wasin = 0
            if objectID in sessionsByAttribute['objectID']:
                wasin = 1
                if self.sid in sessionsByAttribute['objectID'][objectID]:
                    if refID is None or refID >= sessionsByAttribute['objectID'][objectID][self.sid]:
                        del sessionsByAttribute['objectID'][objectID][self.sid]
                        if not sessionsByAttribute['objectID'][objectID]:
                            del sessionsByAttribute['objectID'][objectID]
            if objectID in self.machoObjectsByID:
                if refID is None or refID >= self.machoObjectsByID[objectID][0]:
                    object = self.machoObjectsByID[objectID][1]
                    del self.machoObjectsByID[objectID]
                    if macho.mode != 'client' and not suppressnotification and getattr(self, 'clientID', 0) and not getattr(self, 'clearing_session', 0):
                        sm.services['machoNet'].Scattercast('+clientID', [self.clientID], 'OnMachoObjectDisconnect', objectID, self.clientID, refID)
                    if isinstance(object, ObjectConnection):
                        object.DisconnectObject()
        except StandardError:
            log.LogException()
            sys.exc_clear()



    def GetNotificationID(self):
        self.notificationID += 1L
        return self.notificationID



    def DumpSession(self, prefix, reason):
        log.general.Log(prefix + ':  ' + reason + ".  It's history is as follows:", 1, 2)
        lastEntry = ''
        for eachHistoryRecord in self.sessionhist:
            header = prefix + ':  ' + util.FmtDate(eachHistoryRecord[0], 'll') + ': '
            lines = eachHistoryRecord[1].split('\n')
            tmp = eachHistoryRecord[2]
            if tmp == lastEntry:
                txt = '< same >'
            else:
                txt = tmp
            lastEntry = tmp
            footer = ', ' + txt
            for eachLine in lines[:(len(lines) - 1)]:
                log.general.Log(header + eachLine, 1, 2)

            log.general.Log(header + lines[(len(lines) - 1)] + footer, 1, 2)

        log.general.Log(prefix + ':  Current Session Data:  %s' % strx(self), 1, 2)
        currentcall = GetLocalStorage().get('base.currentcall', None)
        if currentcall:
            try:
                currentcall = currentcall()
                log.general.Log('currentcall was: ' + strx(currentcall))
            except ReferenceError:
                sys.exc_clear()



    def Masquerade(self, props = None):
        w = weakref.ref(self)
        if self.charid:
            tmp = {'base.session': w,
             'base.charsession': w}
        else:
            tmp = {'base.session': w}
        if props is not None:
            tmp.update(props)
        return MasqueradeMask(tmp)



    def GetActualSession(self):
        return self



    def LogSessionHistory(self, reason, details = None, noBlather = 0):
        if self.role & ROLE_SERVICE and not self.hasproblems:
            return 
        timer = PushMark('LogSessionHistory')
        try:
            if details is None:
                details = ''
                for each in ['sid', 'clientID'] + self.__persistvars__:
                    if getattr(self, each, None) is not None:
                        details = details + each + ':' + strx(getattr(self, each)) + ', '

                details = 'session=' + details[:-2]
            else:
                details = 'info=' + strx(details)
            self.__dict__['sessionhist'].append((blue.os.GetTime(), strx(reason)[:255], strx(details)[:255]))
            if len(self.__dict__['sessionhist']) > 120:
                self.__dict__['sessionhist'] = self.__dict__['sessionhist'][70:]
            if not noBlather and log.general.IsOpen(1):
                log.general.Log('SessionHistory:  reason=%s, %s' % (reason, strx(details)), 1, 1)

        finally:
            PopMark(timer)




    def LogSessionError(self, what, novalidate = 0):
        self._CoreSession__LogSessionProblem(what, 4, novalidate)



    def __LogSessionProblem(self, what, how, novalidate = 0):
        self.hasproblems = 1
        self.LogSessionHistory(what)
        if log.general.IsOpen(how):
            log.general.Log('A session related error has occurred.  Session history:', how, 2)
            for eachHistoryRecord in self.sessionhist:
                s = ''.join(map(strx, util.FmtDate(eachHistoryRecord[0], 'll') + ': ' + eachHistoryRecord[1] + ', ' + eachHistoryRecord[2]))
                if len(s) > 5000:
                    s = s[:5000]
                while len(s) > 255:
                    log.general.Log(s[:253], how, 2)
                    s = '- ' + s[253:]

                log.general.Log(s, how, 2)

            log.general.Log('Session Data (should be identical to last history record):  %s' % strx(self), how, 2)
            try:
                currentcall = GetLocalStorage().get('base.currentcall', None)
                if currentcall:
                    currentcall = currentcall()
                    log.general.Log('currentcall was: ' + strx(currentcall))
            except ReferenceError:
                sys.exc_clear()
        if not novalidate:
            self.ValidateSession('session-error-dump')



    def SetSessionVariable(self, k, v):
        if v is None:
            try:
                del self.__dict__['sessionVariables'][k]
            except:
                sys.exc_clear()
        else:
            self.__dict__['sessionVariables'][k] = v



    def GetSessionVariable(self, k, defaultValue = None):
        try:
            return self.__dict__['sessionVariables'][k]
        except:
            sys.exc_clear()
            if defaultValue is not None:
                self.__dict__['sessionVariables'][k] = defaultValue
                return defaultValue
            return 



    def GetDistributedProps(self, orwhat):
        if self.role & ROLE_SERVICE != 0:
            return []
        retval = []
        for each in self.__persistvars__ + self.additionalDistributedProps:
            if orwhat or self.__dict__[each] != self.GetDefaultValueOfAttribute(each):
                retval.append(each)

        return retval


    __dependant_attributes__ = {'userid': ['role',
                'charid',
                'callback',
                'languageID',
                'userType',
                'maxSessionTime'],
     'sid': ['userid']}

    def DependantAttributes(self, attribute):
        retval = self.__dependant_attributes__.get(attribute, [])
        retval2 = {}
        for each in retval:
            retval2[each] = 1
            for other in self.DependantAttributes(each):
                retval2[other] = 1


        return retval2.keys()



    def GetDefaultValueOfAttribute(self, attribute):
        if attribute == 'role':
            return ROLE_LOGIN
        if attribute in self.__attributesWithDefaultValueOfZero__:
            return 0
        if attribute == 'languageID' and macho.mode == 'client':
            return strx(prefs.GetValue('languageID', 'EN'))



    def ClearAttributes(self, isRemote = 0, dontSendMessage = False):
        if not self.changing:
            self.changing = 'ClearAttributes'
        try:
            if getattr(self, 'clearing_session', 0):
                self.LogSessionHistory("Tried to clear a cleared/clearing session's attributes")
            else:
                self.LogSessionHistory('Clearing session attributes')
                for each in self.__dict__['connectedObjects'].values():
                    each[0].DisconnectObject()

                for objectID in copy.copy(self.__dict__['machoObjectsByID']):
                    self.UnregisterMachoObject(objectID, None)

                if self.sid in sessionsBySID:
                    self.ValidateSession('pre-clear')
                    sid = self.sid
                    del sessionsBySID[sid]
                    for attr in sessionsByAttribute:
                        v = getattr(self, attr, None)
                        try:
                            del sessionsByAttribute[attr][v][sid]
                            if not sessionsByAttribute[attr][v]:
                                del sessionsByAttribute[attr][v]
                        except:
                            sys.exc_clear()

                self.__dict__['clearing_session'] = 1
                d = {}
                for each in self.__persistvars__:
                    if each not in ('connectedObjects', 'c2ooid'):
                        d[each] = self.GetDefaultValueOfAttribute(each)

                self.SetAttributes(d, isRemote, dontSendMessage=dontSendMessage)
                self.__dict__['connectedObjects'] = {}
                self.__dict__['machoObjectsByID'] = {}
                d['sessionVariables'] = {}
                sm.ScatterEvent('OnSessionEnd', self.sid)
                self.LogSessionHistory('Session attributes cleared')

        finally:
            self.changing = None




    def ValidateSession(self, prefix):
        bad = 0
        if not getattr(self, 'clearing_session', 0):
            for each in sessionsByAttribute.iterkeys():
                attr = getattr(self, each, None)
                if attr:
                    if attr not in sessionsByAttribute[each]:
                        self.LogSessionHistory('sessionsByAttribute[%s] broken, %s is not found' % (each, attr))
                        bad = 1
                    elif self.sid not in sessionsByAttribute[each][attr]:
                        self.LogSessionHistory('sessionsByAttribute[%s][%s] broken, %s is not found' % (each, attr, self.sid))
                        bad = 1
                    elif attr in ('userid', 'charid') and len(sessionsByAttribute[each][attr][sid]) != 1:
                        self.LogSessionHistory('sessionsByAttribute[%s][%s] broken, this user/char has multiple sessions (%d)' % (each, attr, len(sessionsByAttribute[each][attr][sid])))
                        bad = 1

            if bad:
                self.LogSessionError("The session failed it's %s validation check.  Session dump and stack trace follows." % prefix, 1)
                log.LogTraceback()
        return bad



    def __ChangeAttribute(self, attr, towhat):
        self.__dict__['nextSessionChange'] = blue.os.GetTime() + GetSessionChangeTimer(self.role)
        if getattr(self, 'clearing_session', 0):
            self.__dict__[attr] = towhat
        else:
            sa = sessionsByAttribute.get(attr, None)
            if sa is None:
                self.__dict__[attr] = towhat
            else:
                try:
                    if towhat and towhat not in sa:
                        sa[towhat] = {}
                    fromwhat = self.__dict__[attr]
                    if fromwhat and fromwhat in sa and self.sid in sa[fromwhat]:
                        del sa[fromwhat][self.sid]
                    self.__dict__[attr] = towhat
                    if towhat:
                        sa[towhat][self.sid] = 1
                    if fromwhat and fromwhat in sa and not len(sa[fromwhat]):
                        del sa[fromwhat]
                    charIDAttribute = attr == 'charid'
                    if not charsession and charIDAttribute and towhat:
                        UpdateLocalStorage({'base.charsession': weakref.ref(self)})
                except:
                    self.DumpSession('ARGH!!!', 'This session is blowing up during change attribute')
                    raise 



    def RecalculateDependantAttributes(self, d):
        pass



    def SetAttributes(self, requested, isRemote = 0, dontSendMessage = False):
        if not self.changing:
            self.changing = 'SetAttributes'
        try:
            self.LogSessionHistory('Setting session attributes')
            try:
                orig = copy.copy(requested)
                junk = []
                for each in orig:
                    if each not in self.__persistvars__:
                        junk.append(each)

                if junk:
                    log.LogTraceback(extraText=strx(junk), severity=log.LGWARN)
                    for each in junk:
                        del orig[each]

                arr = []
                d = {}
                for each in orig.iterkeys():
                    arr += self.DependantAttributes(each)
                    if orig[each] is not None and each not in ['address', 'languageID'] + self.additionalNonIntegralAttributes:
                        try:
                            if each in self.longAttributes:
                                d[each] = long(orig[each])
                            else:
                                d[each] = int(orig[each])
                        except TypeError:
                            log.general.Log('%s is not an integer %s' % (each, strx(orig[each])), 4, 1)
                            log.LogTraceback()
                            raise 
                    else:
                        d[each] = orig[each]

                charID = orig.get('charid', None)
                if charID is not None and charID != self.charid:
                    d.update(sm.GetService('sessionMgr').GetInitialValuesFromCharID(charID))
                for each in arr:
                    if each not in d:
                        d[each] = self.GetDefaultValueOfAttribute(each)

                self.RecalculateDependantAttributes(d)
                self.ValidateSession('pre-change')
                clientID = getattr(self, 'clientID', 0)
                change = {}
                disappeared = {}
                for each in d.iterkeys():
                    df = self.GetDefaultValueOfAttribute(each)
                    if self.__dict__.get(each, df) != d[each]:
                        change[each] = (self.__dict__.get(each, df), d[each])
                        if change[each][0] and not change[each][1]:
                            disappeared[each] = 1

                mask = None
                try:
                    if 'userid' in change and change['userid'][0] and change['userid'][1]:
                        self.LogSessionError("A session's userID may not change, %s=>%s" % change['userid'])
                        raise RuntimeError("A session's userID may not change")
                    if not self.role & ROLE_SERVICE and change:
                        mask = self.Masquerade()
                        sm.SendEvent('DoSessionChanging', isRemote, self, change)
                        if disappeared:
                            dudes = []
                            for each in self.connectedObjects.iterkeys():
                                if self.connectedObjects[each][0].__object__ is not None and hasattr(self.connectedObjects[each][0].__object__, '__sessionfilter__'):
                                    for other in disappeared.iterkeys():
                                        if other in self.connectedObjects[each][0].__object__.__sessionfilter__:
                                            dudes.append((self.connectedObjects[each][0], self.connectedObjects[each][0].__object__, each))
                                            break


                            for each in dudes:
                                with self.Masquerade({'base.caller': weakref.ref(each[0])}):
                                    try:
                                        if each[2] in self.connectedObjects:
                                            each[0].DisconnectObject()
                                    except StandardError:
                                        log.LogException()
                                        sys.exc_clear()

                    for each in change:
                        self._CoreSession__ChangeAttribute(each, d[each])

                    self.ValidateSession('post-change')
                    if not self.role & ROLE_SERVICE:
                        if change and dontSendMessage == False:
                            if mask is None:
                                mask = self.Masquerade()
                            notifyOtherNodes = list(sm.ChainEvent('ProcessSessionChange', isRemote, self, change))
                            dudes = []
                            for each in self.connectedObjects.iterkeys():
                                if self.connectedObjects[each][0].__object__ is not None and hasattr(self.connectedObjects[each][0].__object__, '__sessionfilter__') and hasattr(self.connectedObjects[each][0].__object__, 'ProcessSessionChange'):
                                    for other in change.iterkeys():
                                        if other in self.connectedObjects[each][0].__object__.__sessionfilter__:
                                            dudes.append((self.connectedObjects[each][0], self.connectedObjects[each][0].__object__, each))
                                            break


                            for each in dudes:
                                with self.Masquerade({'base.caller': weakref.ref(each[0])}):
                                    try:
                                        if each[2] in self.connectedObjects:
                                            notifyOtherNodes.append(each[1].ProcessSessionChange(isRemote, self, change))
                                    except StandardError:
                                        log.LogException()
                                        sys.exc_clear()

                            if clientID and not isRemote:
                                if not (self.role & (ROLE_LOGIN | ROLE_PLAYER) or self.role & (ROLE_SERVICE | ROLE_REMOTESERVICE)):
                                    self.LogSessionError("A distributed session's role should probably always have login and player rights, even before a change broadcast")
                                sessionChangeLayer = sm.services['machoNet'].GetGPCS('sessionchange')
                                if sessionChangeLayer is not None:
                                    sessionChangeLayer.SessionChanged(clientID, self.sid, change, notifyOtherNodes)
                            sm.ScatterEvent('OnSessionChanged', isRemote, self, change)

                finally:
                    if mask is not None:
                        mask.UnMask()


            finally:
                self.LogSessionHistory('Session attributes set')


        finally:
            self.changing = None




    def RecalculateDependantAttributesWithChanges(self, changes):
        pass



    def ApplyRemoteAttributeChanges(self, clueless, changes):
        if not self.changing:
            self.changing = 'ApplyRemoteAttributeChanges'
        try:
            self.LogSessionHistory('Applying remote attribute changes')
            if self.role & ROLE_SERVICE:
                self.LogSessionError('A service session may not change via remote attribute propagation, change=%s' % strx(changes))
                raise RuntimeError('A service session may not change via remote attribute propagation, change=%s' % strx(changes))
            try:
                notify = {}
                self.ValidateSession('pre-change')
                self.RecalculateDependantAttributesWithChanges(changes)
                disappeared = {}
                for each in changes.iterkeys():
                    df = self.GetDefaultValueOfAttribute(each)
                    if self.__dict__.get(each, df) != changes[each][1]:
                        notify[each] = (self.__dict__.get(each, df), changes[each][1])
                        if notify[each][0] and not notify[each][1]:
                            disappeared[each] = 1

                mask = None
                try:
                    if 'userid' in notify and notify['userid'][0] and notify['userid'][1]:
                        self.LogSessionError("A session's userID may not change, %s=>%s" % notify['userid'])
                        raise RuntimeError("A session's userID may not change")
                    if not self.role & ROLE_SERVICE and notify:
                        mask = self.Masquerade()
                        sm.SendEvent('DoSessionChanging', 1, self, notify)
                        dudes = []
                        for each in self.connectedObjects.iterkeys():
                            if self.connectedObjects[each][0].__object__ is not None and hasattr(self.connectedObjects[each][0].__object__, '__sessionfilter__'):
                                for other in disappeared.iterkeys():
                                    if other in self.connectedObjects[each][0].__object__.__sessionfilter__:
                                        dudes.append((self.connectedObjects[each][0], self.connectedObjects[each][0].__object__, each))
                                        break


                        for each in dudes:
                            with self.Masquerade({'base.caller': weakref.ref(each[0])}):
                                try:
                                    if each[2] in self.connectedObjects:
                                        each[0].DisconnectObject()
                                except StandardError:
                                    log.LogException()
                                    sys.exc_clear()

                    for each in notify:
                        self._CoreSession__ChangeAttribute(each, changes[each][1])

                    self.ValidateSession('post-change')
                    if 'role' in notify and self.charid and notify['role'][1] != self.role:
                        self.LogSessionError("A session's role should probably not change for active characters, even in remote attribute stuff")
                    if not self.role & (ROLE_LOGIN | ROLE_PLAYER):
                        self.LogSessionError("A distributed session's role should probably always have login and player rights, even during a change broadcast")
                    if notify:
                        if mask is None:
                            mask = self.Masquerade()
                        sm.ChainEvent('ProcessSessionChange', 1, self, notify)
                        dudes = []
                        for each in self.connectedObjects.iterkeys():
                            if self.connectedObjects[each][0].__object__ is not None and hasattr(self.connectedObjects[each][0].__object__, '__sessionfilter__') and hasattr(self.connectedObjects[each][0].__object__, 'ProcessSessionChange'):
                                for other in notify.iterkeys():
                                    if other in self.connectedObjects[each][0].__object__.__sessionfilter__:
                                        dudes.append((self.connectedObjects[each][0], self.connectedObjects[each][0].__object__, each))
                                        break


                        for each in dudes:
                            with self.Masquerade({'base.caller': weakref.ref(each[0])}):
                                try:
                                    if each[2] in self.connectedObjects:
                                        each[1].ProcessSessionChange(1, self, notify)
                                except StandardError:
                                    log.LogException()
                                    sys.exc_clear()

                        sm.ScatterEvent('OnSessionChanged', 1, self, notify)

                finally:
                    if mask is not None:
                        mask.UnMask()


            finally:
                self.LogSessionHistory('Applied remote attribute changes')


        finally:
            self.changing = None




    def ApplyInitialState(self, initialstate):
        if not self.changing:
            self.changing = 'ApplyInitialState'
        try:
            self.LogSessionHistory('Applying initial session state from remote session information')
            if self.role & ROLE_SERVICE:
                self.LogSessionError('A service session may not change via remote attribute propagation, change=%s' % strx(initialstate))
                raise RuntimeError('A service session may not change via remote attribute propagation, change=%s' % strx(initialstate))
            try:
                notify = {}
                self.ValidateSession('pre-change')
                self.RecalculateDependantAttributes(initialstate)
                disappeared = {}
                for each in initialstate.iterkeys():
                    df = self.GetDefaultValueOfAttribute(each)
                    if self.__dict__.get(each, df) != initialstate[each]:
                        notify[each] = (self.__dict__.get(each, df), initialstate[each])
                        if notify[each][0] and not notify[each][1]:
                            disappeared[each] = 1

                mask = None
                try:
                    if 'userid' in notify and notify['userid'][0] and notify['userid'][1]:
                        self.LogSessionError("A session's userID may not change, %s=>%s" % notify['userid'])
                        raise RuntimeError("A session's userID may not change")
                    if not self.role & ROLE_SERVICE and notify:
                        mask = self.Masquerade()
                        sm.SendEvent('DoSessionChanging', 1, self, notify)
                        dudes = []
                        for each in self.connectedObjects.iterkeys():
                            if self.connectedObjects[each][0].__object__ is not None and hasattr(self.connectedObjects[each][0].__object__, '__sessionfilter__'):
                                for other in disappeared.iterkeys():
                                    if other in self.connectedObjects[each][0].__object__.__sessionfilter__:
                                        dudes.append((self.connectedObjects[each][0], self.connectedObjects[each][0].__object__, each))
                                        break


                        for each in dudes:
                            with self.Masquerade({'base.caller': weakref.ref(each[0])}):
                                try:
                                    if each[2] in self.connectedObjects:
                                        each[0].DisconnectObject()
                                except StandardError:
                                    log.LogException()
                                    sys.exc_clear()

                    for each in notify:
                        self._CoreSession__ChangeAttribute(each, initialstate[each])

                    self.ValidateSession('post-change')
                    if not self.role & (ROLE_LOGIN | ROLE_PLAYER):
                        self.LogSessionError("A distributed session's role should probably always have login and player rights, even in initial state")
                    if notify:
                        if mask is None:
                            mask = self.Masquerade()
                        sm.ChainEvent('ProcessSessionChange', 1, self, notify)
                        dudes = []
                        for each in self.connectedObjects.iterkeys():
                            if self.connectedObjects[each][0].__object__ is not None and hasattr(self.connectedObjects[each][0].__object__, '__sessionfilter__') and hasattr(self.connectedObjects[each][0].__object__, 'ProcessSessionChange'):
                                for other in notify.iterkeys():
                                    if other in self.connectedObjects[each][0].__object__.__sessionfilter__:
                                        dudes.append((self.connectedObjects[each][0], self.connectedObjects[each][0].__object__, each))
                                        break


                        for each in dudes:
                            with self.Masquerade({'base.caller': weakref.ref(each[0])}):
                                try:
                                    if each[2] in self.connectedObjects:
                                        each[1].ProcessSessionChange(1, self, notify)
                                except StandardError:
                                    log.LogException()
                                    sys.exc_clear()

                        sm.ScatterEvent('OnSessionChanged', 1, self, notify)

                finally:
                    if mask is not None:
                        mask.UnMask()


            finally:
                self.LogSessionHistory('Applied initial session state from remote session information')


        finally:
            self.changing = None




    def __repr__(self):
        ret = '<Session: ('
        for each in ['sid',
         'clientID',
         'changing',
         'mutating'] + self.additionalAttributesToPrint + self.__persistvars__:
            if getattr(self, each, None) is not None:
                if each in ['role'] + self.additionalHexAttributes:
                    ret = ret + each + ':' + strx(hex(getattr(self, each))) + ', '
                else:
                    ret = ret + each + ':' + strx(getattr(self, each)) + ', '

        ret = ret[:-2] + ')>'
        return ret



    def __setattr__(self, attr, value):
        if attr in ['sid', 'clientID'] + self.additionalNoSetAttributes + self.__persistvars__:
            raise RuntimeError('ReadOnly', attr)
        else:
            self.__dict__[attr] = value



    def DisconnectObject(self, object, key = None, delaySecs = 1):
        for (k, v,) in self.connectedObjects.items():
            (obConn,) = v
            if obConn.__object__ is object and (key is None or key == (obConn.__dict__['__session__'].sid, obConn.__dict__['__c2ooid__'])):
                obConn.DisconnectObject(delaySecs)




    def RedirectObject(self, object, serviceName = None, bindParams = None, key = None):
        for (k, v,) in self.connectedObjects.items():
            (obConn,) = v
            if obConn.__object__ is object and (key is None or key == (obConn.__dict__['__session__'].sid, obConn.__dict__['__c2ooid__'])):
                obConn.RedirectObject(serviceName, bindParams)




    def ConnectToObject(self, object, serviceName = None, bindParams = None):
        c2ooid = self.__dict__['c2ooid']
        self.__dict__['c2ooid'] += 1
        return ObjectConnection(self, object, c2ooid, serviceName, bindParams)



    def ConnectToClientService(self, svc, idtype = None, theID = None):
        if theID is None or idtype is None:
            if self.role & ROLE_SERVICE:
                log.LogTraceback()
                raise RuntimeError('You must specify an ID type and ID to identify the client')
            else:
                theID = self.clientID
                idtype = 'clientID'
        elif not self.role & ROLE_SERVICE and macho.mode != 'client':
            log.LogTraceback()
            raise RuntimeError('You cannot cross the wire except in the context of a service')
        if currentcall:
            currentcall.UnLockSession()
        return sm.services['sessionMgr'].ConnectToClientService(svc, idtype, theID)



    def ConnectToService(self, svc, **keywords):
        return ServiceConnection(self, svc, **keywords)



    def ConnectToAllServices(self, svc, batchInterval = 0):
        if not self.role & ROLE_SERVICE and macho.mode != 'client':
            raise RuntimeError('You cannot cross the wire except in the context of a service')
        return sm.services['machoNet'].ConnectToAllServices(svc, self, batchInterval=batchInterval)



    def ConnectToRemoteService(self, svc, nodeID = None):
        if not self.role & ROLE_SERVICE and macho.mode != 'client':
            raise RuntimeError('You cannot cross the wire except in the context of a service')
        if macho.mode == 'server' and nodeID is None:
            nodeID = sm.GetService(svc).MachoResolve(self)
            if type(nodeID) == types.StringType:
                raise RuntimeError(nodeID)
            elif nodeID is None:
                return self.ConnectToService(svc)
        if nodeID is not None and nodeID == sm.services['machoNet'].GetNodeID():
            return self.ConnectToService(svc)
        return sm.services['machoNet'].ConnectToRemoteService(svc, nodeID, self)



    def ConnectToSolServerService(self, svc, nodeID = None):
        if not self.role & ROLE_SERVICE and macho.mode != 'client':
            raise RuntimeError('You cannot cross the wire except in the context of a service')
        if macho.mode == 'server' and nodeID is None:
            nodeID = sm.GetService(svc).MachoResolve(self)
            if type(nodeID) == types.StringType:
                raise RuntimeError(nodeID)
            elif nodeID is None:
                return self.ConnectToService(svc)
        if macho.mode == 'server' and (nodeID is None or nodeID == sm.services['machoNet'].GetNodeID()):
            return self.ConnectToService(svc)
        else:
            return sm.services['machoNet'].ConnectToRemoteService(svc, nodeID, self)



    def ConnectToProxyServerService(self, svc, nodeID = None):
        if not self.role & ROLE_SERVICE and macho.mode != 'client':
            raise RuntimeError('You cannot cross the wire except in the context of a service')
        if macho.mode == 'proxy' and (nodeID is None or nodeID == sm.services['machoNet'].GetNodeID()):
            return self.ConnectToService(svc)
        else:
            return sm.services['machoNet'].ConnectToRemoteService(svc, nodeID, self)



    def ConnectToAnyService(self, svc):
        if not self.role & ROLE_SERVICE and macho.mode != 'client':
            raise RuntimeError('You cannot cross the wire except in the context of a service')
        if svc in sm.services:
            return self.ConnectToService(svc)
        else:
            return self.ConnectToRemoteService(svc)



    def ConnectToAllNeighboringServices(self, svc, batchInterval = 0):
        if not self.role & ROLE_SERVICE and macho.mode != 'client':
            raise RuntimeError('You cannot cross the wire except in the context of a service')
        return sm.services['machoNet'].ConnectToAllNeighboringServices(svc, self, batchInterval=batchInterval)



    def ConnectToAllProxyServerServices(self, svc, batchInterval = 0):
        if not self.role & ROLE_SERVICE and macho.mode != 'client':
            raise RuntimeError('You cannot cross the wire except in the context of a service')
        if macho.mode == 'proxy':
            return sm.services['machoNet'].ConnectToAllSiblingServices(svc, self, batchInterval=batchInterval)
        else:
            return sm.services['machoNet'].ConnectToAllNeighboringServices(svc, self, batchInterval=batchInterval)



    def ConnectToAllSolServerServices(self, svc, batchInterval = 0):
        if not self.role & ROLE_SERVICE and macho.mode != 'client':
            raise RuntimeError('You cannot cross the wire except in the context of a service')
        if macho.mode == 'server':
            return sm.services['machoNet'].ConnectToAllSiblingServices(svc, self, batchInterval=batchInterval)
        else:
            return sm.services['machoNet'].ConnectToAllNeighboringServices(svc, self, batchInterval=batchInterval)



    def RemoteServiceCall(self, dest, service, method, *args, **keywords):
        return self.RemoteServiceCallWithoutTheStars(dest, service, method, args, keywords)



    def RemoteServiceCallWithoutTheStars(self, dest, service, method, *args, **keywords):
        if not self.role & ROLE_SERVICE and macho.mode != 'client':
            raise RuntimeError('You cannot cross the wire except in the context of a service')
        return sm.services['machoNet'].RemoteServiceCallWithoutTheStars(self, dest, service, method, args, keywords)



    def RemoteServiceNotify(self, dest, service, method, *args, **keywords):
        return self.RemoteServiceNotifyWithoutTheStars(dest, service, method, args, keywords)



    def RemoteServiceNotifyWithoutTheStars(self, dest, service, method, args, keywords):
        if not self.role & ROLE_SERVICE and macho.mode != 'client':
            raise RuntimeError('You cannot cross the wire except in the context of a service')
        sm.services['machoNet'].RemoteServiceNotifyWithoutTheStars(self, args, keywords)



    def ResetSessionChangeTimer(self, reason):
        sm.GetService('sessionMgr').LogInfo("Resetting next legal session change timer, reason='", reason, "', was ", util.FmtDate(self.nextSessionChange or blue.os.GetTime()))
        self.nextSessionChange = None




class ObjectConnection():
    __passbyvalue__ = 0
    __restrictedcalls__ = {'PseudoMethodCall': 1,
     'LogPseudoMethodCall': 1,
     'GetObjectConnectionLogClass': 1,
     'RedirectObject': 1,
     'Objectcast': 1}

    def __init__(self, sess, object, c2ooid, serviceName = None, bindParams = None):
        if object is None:
            sess.LogSessionError('Establishing an object connection to None')
            log.LogTraceback()
        self.__dict__['__last_used__'] = blue.os.GetTime()
        self.__dict__['__constructing__'] = 1
        self.__dict__['__deleting__'] = 0
        self.__dict__['__machoObjectUUID__'] = GetObjectUUID(object)
        self.__dict__['__redirectObject__'] = None
        self.__dict__['__disconnected__'] = 1
        self.__dict__['__session__'] = weakref.proxy(sess)
        self.__dict__['__c2ooid__'] = c2ooid
        self.__dict__['__object__'] = object
        self.__dict__['__serviceName__'] = serviceName
        self.__dict__['__bindParams__'] = bindParams
        self.__dict__['__publicattributes__'] = getattr(object, '__publicattributes__')
        if not hasattr(object, 'objectConnections'):
            object.objectConnections = weakref.WeakValueDictionary({})
        if not hasattr(object, 'objectConnectionsBySID'):
            object.objectConnectionsBySID = {}
        if not hasattr(object, 'sessionConnections'):
            object.sessionConnections = weakref.WeakValueDictionary({})
        if not hasattr(object, 'machoInstanceID'):
            object.machoInstanceID = blue.os.GetTime(1)
        try:
            lock = None
            if not object.sessionConnections:
                if object.objectConnections:
                    log.LogTraceback()
                if sess.role & service.ROLE_PLAYER:
                    sm.GetService(serviceName).LogInfo('Player session re-aquiring big lock.  Session:', sess)
                    lock = (sm.GetService(serviceName).LockService(bindParams), bindParams)
                object.service = weakref.proxy(sm.GetService(serviceName))
                object.session = weakref.proxy(object.service.session)
                for each in getattr(object, '__dependencies__', []):
                    if not hasattr(object.service, each):
                        dep = object.service.session.ConnectToService(each)
                        setattr(object.service, each, dep)
                    setattr(object, each, getattr(object.service, each))

                self.PseudoMethodCall(object, 'OnRun')
            if sess.role & service.ROLE_PLAYER and lock is None:
                charid = sess.charid
                lock = (object.service.LockService((bindParams, charid)), (bindParams, charid))
            if sess.sid not in object.sessionConnections:
                self.PseudoMethodCall(object, 'OnSessionAttach')
                object.sessionConnections[sess.sid] = sess
            object.objectConnections[(sess.sid, c2ooid)] = self
            if sess.sid not in object.objectConnectionsBySID:
                object.objectConnectionsBySID[sess.sid] = {c2ooid: 1}
            else:
                object.objectConnectionsBySID[sess.sid][c2ooid] = 1
            sess.connectedObjects[self.__c2ooid__] = (self,)
            self.__disconnected__ = 0
            self.__pendingDisconnect__ = 0
            allObjectConnections[self] = 1
            allConnectedObjects[object] = 1

        finally:
            if lock is not None:
                sm.GetService(serviceName).UnLockService(lock[1], lock[0])

        self.__dict__['__constructing__'] = 0



    def GetSession(self):
        return self.__session__



    def __del__(self):
        if not self.__deleting__:
            self.__deleting__ = 1
            if not self.__disconnected__:
                if log.methodcalls.IsOpen(2):
                    log.methodcalls.Log("Curious....   Disconnecting during __del__ wasn't entirely expected...", 2, 1)
                self.DisconnectObject(30)



    def __str__(self):
        return 'ObjectConnection to ' + strx(self.__object__)



    def __repr__(self):
        return self.__str__()



    def GetInstanceID(self):
        return self.__object__.machoInstanceID



    def PseudoMethodCall(self, object, method, *args, **keywords):
        self.__dict__['__last_used__'] = blue.os.GetTime()
        if hasattr(object, method):
            try:
                if hasattr(object, '__guid__'):
                    logname = object.__guid__
                    s = logname.split('.')
                    if len(s) > 1:
                        logname = s[1]
                else:
                    logname = object.__class__.__name__
            except:
                logname = 'CrappyClass'
                sys.exc_clear()
            with self.__session__.Masquerade({'base.caller': weakref.ref(self)}):
                with CallTimer(logname + '::' + method):
                    try:
                        result = apply(getattr(object, method), args, keywords)
                    except Exception as e:
                        self.LogPseudoMethodCall(e, method)
                        raise 
                    self.LogPseudoMethodCall(result, method)
            return result



    def LogPseudoMethodCall(self, result, method, *args, **keywords):
        logChannel = log.methodcalls
        if logChannel.IsOpen(log.LGINFO):
            try:
                if hasattr(self.__object__, '__guid__'):
                    logname = self.__object__.__guid__
                    s = logname.split('.')
                    if len(s) > 1:
                        logname = s[1]
                else:
                    logname = self.__object__.__class__.__name__
            except:
                logname = 'CrappyClass'
                sys.exc_clear()
            if isinstance(result, Exception):
                eorr = ', EXCEPTION='
            else:
                eorr = ', retval='
            if keywords:
                logwhat = [logname,
                 '::',
                 method,
                 ' args=',
                 args,
                 ', keywords={',
                 keywords,
                 '}',
                 eorr,
                 result]
            else:
                logwhat = [logname,
                 '::',
                 method,
                 ' args=',
                 args,
                 eorr,
                 result]
            timer = PushMark(logname + '::LogPseudoMethodCall')
            try:
                try:
                    s = ''.join(map(strx, logwhat))
                    if len(s) > 2500:
                        s = s[:2500]
                    while len(s) > 255:
                        logChannel.Log(s[:253], log.LGINFO, 1)
                        s = '- ' + s[253:]

                    logChannel.Log(s, log.LGINFO, 1)
                except TypeError:
                    logChannel.Log('[X]'.join(map(strx, logwhat)).replace('\x00', '\\0'), log.LGINFO, 1)
                    sys.exc_clear()
                except UnicodeEncodeError:
                    logChannel.Log('[U]'.join(map(lambda x: x.encode('ascii', 'replace'), map(unicode, logwhat))), log.LGINFO, 1)
                    sys.exc_clear()

            finally:
                PopMark(timer)




    def GetObjectConnectionLogClass(self):
        ob = self.__object__
        try:
            try:
                logclass = ob.__logname__
            except AttributeError:
                try:
                    logclass = ob.__guid__.split('.')
                    if len(logclass) > 1:
                        logclass = logclass[1]
                    else:
                        logclass = logclass[0]
                    try:
                        setattr(ob, '__logname__', logclass)
                    except:
                        pass
                except AttributeError:
                    logclass = ob.__class__.__name__
        except:
            logclass = 'CrappyClass'
        sys.exc_clear()
        return logclass



    def __GetObjectType(self):
        return 'ObjectConnection to ' + self.GetObjectConnectionLogClass()



    def RedirectObject(self, serviceName = None, bindParams = None):
        if serviceName is None:
            serviceName = self.__serviceName__
        if bindParams is None:
            bindParams = self.__bindParams__
        self.__redirectObject__ = (serviceName, bindParams)



    def DisconnectObject(self, delaySecs = 0):
        if delaySecs:
            if not self.__pendingDisconnect__:
                dyingObjects.append((blue.os.GetTime() + delaySecs * SEC, self))
                self.__pendingDisconnect__ = 1
            else:
                self.__pendingDisconnect__ += 1
                if self.__pendingDisconnect__ in (10, 100, 1000, 10000, 100000, 1000000, 10000000):
                    if not prefs.GetValue('suppressObjectKillahDupSpam', 0):
                        log.LogTraceback('Many duplicate requests (%d) to add object to objectKillah dyingObjects list - %r %r' % (self.__pendingDisconnect__, self, self.GetObjectConnectionLogClass()), severity=log.LGWARN)
            return 
        if not self.__disconnected__:
            self.__disconnected__ = 1
            try:
                if not sm.IsServiceRunning(self.__serviceName__):
                    return 
                lock = None
                if self.__session__.role & ROLE_PLAYER:
                    charid = getattr(self.__session__, 'charid')
                    lock = sm.GetService(self.__serviceName__).LockService((self.__bindParams__, charid))
                try:
                    objectID = GetObjectUUID(self)
                    if objectID in self.__session__.machoObjectsByID:
                        objectType = self._ObjectConnection__GetObjectType()
                        self.__session__.LogSessionHistory('%s object %s disconnected from this session by the server' % (objectType, objectID), strx(self.__object__))
                        self.__session__.UnregisterMachoObject(objectID, None, 0)
                    try:
                        del self.__object__.objectConnections[(self.__session__.sid, self.__c2ooid__)]
                    except:
                        sys.exc_clear()
                    try:
                        del self.__object__.objectConnectionsBySID[self.__session__.sid][self.__c2ooid__]
                        if not self.__object__.objectConnectionsBySID[self.__session__.sid]:
                            del self.__object__.objectConnectionsBySID[self.__session__.sid]
                            found = 0
                        else:
                            found = 1
                    except:
                        found = 0
                        sys.exc_clear()
                    if not found:
                        try:
                            del self.__object__.sessionConnections[self.__session__.sid]
                        except:
                            sys.exc_clear()
                        try:
                            self.PseudoMethodCall(self.__object__, 'OnSessionDetach')
                        except StandardError:
                            log.LogException()
                            sys.exc_clear()
                    try:
                        del self.__session__.connectedObjects[self.__c2ooid__]
                    except:
                        sys.exc_clear()

                finally:
                    if lock:
                        sm.GetService(self.__serviceName__).UnLockService((self.__bindParams__, charid), lock)

                with sm.GetService(self.__serviceName__).LockedService(self.__bindParams__):
                    if not getattr(self.__object__, 'sessionConnections', None):
                        if hasattr(self.__object__, 'sessionConnections'):
                            delattr(self.__object__, 'sessionConnections')
                        if getattr(self.__object__, 'objectConnections', {}):
                            StackTrace()
                        if getattr(self.__object__, 'objectConnectionsBySID', {}):
                            StackTrace()
                        if hasattr(self.__object__, 'objectConnections'):
                            delattr(self.__object__, 'objectConnections')
                        if hasattr(self.__object__, 'objectConnectionsBySID'):
                            delattr(self.__object__, 'objectConnectionsBySID')
                        service = sm.GetService(self.__serviceName__)
                        if self.__bindParams__ in service.boundObjects:
                            del service.boundObjects[self.__bindParams__]
                        self.PseudoMethodCall(self.__object__, 'OnStop')
                        if hasattr(self.__object__, 'service'):
                            delattr(self.__object__, 'service')
                        if hasattr(self.__object__, 'session'):
                            delattr(self.__object__, 'session')
                        for each in getattr(self.__object__, 'dependencies', []):
                            delattr(self.__object__, each)

            except ReferenceError:
                sys.exc_clear()
            except StandardError:
                log.LogException()
                sys.exc_clear()
            self.__object__ = None



    def __getattr__(self, method):
        if method in self.__dict__:
            return self.__dict__[method]
        if not method.isupper():
            if method in self.__dict__['__publicattributes__']:
                return getattr(self.__object__, method)
            if method.startswith('__'):
                raise AttributeError(method)
        if self.__c2ooid__ not in self.__session__.connectedObjects:
            self.__session__.LogSessionHistory('Object no longer live:  c2ooid=' + strx(self.__c2ooid__) + ', serviceName=' + strx(self.__serviceName__) + ', bindParams=' + strx(self.__bindParams__) + ', uuid=' + strx(self.__machoObjectUUID__), None, 1)
            self.__session__.LogSessionError('This object connection is no longer live')
            raise RuntimeError('This object connection is no longer live')
        self.__dict__['__last_used__'] = blue.os.GetTime()
        if self.__session__.role & (ROLE_SERVICE | ROLE_REMOTESERVICE) == ROLE_SERVICE:
            if method.endswith('_Ex'):
                return service.FastCallWrapper(self.__session__, self.__object__, method[:-3], self)
            else:
                return service.FastCallWrapper(self.__session__, self.__object__, method, self)
        return service.ObjectCallWrapper(self.__session__, self.__object__, method, self, self.GetObjectConnectionLogClass())




class ServiceConnection():
    __restrictedcalls__ = {'Lock': 1,
     'UnLock': 1,
     'GetCachedObject': 1,
     'SetCachedObject': 1,
     'DelCachedObject': 1}

    def __init__(self, sess, service, **keywords):
        self.__session__ = weakref.proxy(sess)
        self.__service__ = service
        self.__remote__ = keywords.get('remote', 0)
        srv = sm.StartService(self.__service__)



    def Lock(self, lockID):
        return sm.GetService(self.__service__).LockService(lockID)



    def UnLock(self, lockID, lock):
        sm.GetService(self.__service__).UnLockService(lockID, lock)



    def GetCachedObject(self, key):
        srv = sm.GetService(self.__service__)
        return srv.boundObjects.get(key, None)



    def SetCachedObject(self, key, object):
        srv = sm.GetService(self.__service__)
        if sm.services[self.__service__].__machocacheobjects__:
            srv.boundObjects[key] = object



    def DelCachedObject(self, key):
        srv = sm.GetService(self.__service__)
        if key in srv.boundObjects:
            del srv.boundObjects[key]



    def GetInstanceID(self):
        return sm.GetService(self.__service__).startedWhen



    def __getitem__(self, key):
        mn = sm.services['machoNet']
        if type(key) == types.TupleType:
            nodeID = mn.GetNodeFromAddress(key[0], key[1])
        elif type(key) == types.IntType:
            nodeID = key
        else:
            srv = sm.GetService(self.__service__)
            nodeID = self.MachoResolve(key)
        if nodeID == mn.GetNodeID():
            return self
        else:
            return self.__session__.ConnectToRemoteService(self.__service__, nodeID)



    def __nonzero__(self):
        return 1



    def __str__(self):
        sess = 'unknown'
        try:
            sess = strx(self.__session__)
        except:
            pass
        return 'ServiceConnection, Service:' + strx(self.__service__) + '. Session:' + sess



    def __repr__(self):
        return self.__str__()



    def __getattr__(self, method):
        if method in self.__dict__:
            return self.__dict__[method]
        else:
            if method.startswith('__'):
                raise AttributeError(method)
            svc = sm.GetService(self.__service__)
            if not self.__remote__ and (self.__session__.role & ROLE_SERVICE or macho.mode == 'client' or method == 'MachoResolve'):
                self._ServiceConnection__WaitForRunningState(svc)
                if method.endswith('_Ex'):
                    return service.FastCallWrapper(self.__session__, svc, method[:-3], self)
                else:
                    return service.FastCallWrapper(self.__session__, svc, method, self)
            if self.__session__.role & ROLE_SERVICE:
                return service.UnlockedServiceCallWrapper(self.__session__, svc, method, self, self.__service__)
            return service.ServiceCallWrapper(self.__session__, svc, method, self, self.__service__)



    def __WaitForRunningState(self, svc):
        desiredStates = (service.SERVICE_RUNNING,)
        errorStates = (service.SERVICE_FAILED, service.SERVICE_STOPPED)
        sm.WaitForServiceObjectState(svc, desiredStates, errorStates)



service_sessions = {}
sessionsByAttribute = {'userid': {},
 'userType': {},
 'charid': {},
 'objectID': {}}
sessionsBySID = {}
allSessionsBySID = weakref.WeakValueDictionary({})

def GetAllSessionInfo():
    return (allSessionsBySID, sessionsBySID, sessionsByAttribute)



def GetNewSid():
    return uuid.uuid4().int



def GetSessionMaps():
    return (sessionsBySID, sessionsByAttribute)



def CreateSession(role = ROLE_LOGIN, sid = None):
    if sid is None:
        sid = GetNewSid()
    if sid in sessionsBySID:
        log.general.Log('Session SID collision!', log.LGERR)
        log.general.Log('Local session being broken %s' % (sessionsBySID[sid],), log.LGERR)
    s = base.Session(sid, role)
    sessionsBySID[sid] = s
    allSessionsBySID[sid] = s
    return s



def GetServiceSession(forwho, refcounted = 0):
    if forwho not in service_sessions:
        ret = CreateSession(ROLE_SERVICE)
        ret.serviceName = forwho
        service_sessions[forwho] = ret
    else:
        ret = service_sessions[forwho]
    if refcounted:
        if not hasattr(ret, 'remoteServiceSessionRefCount'):
            ret.__dict__['remoteServiceSessionRefCount'] = 1
        else:
            ret.__dict__['remoteServiceSessionRefCount'] += 1
    return ret



def CountSessions(attr, val):
    cnt = 0
    for v in val:
        try:
            r = []
            for sid in sessionsByAttribute[attr].get(v, {}).iterkeys():
                if sid in sessionsBySID:
                    cnt += 1
                else:
                    r.append(sid)

            for each in r:
                del sessionsByAttribute[attr][v][each]

        except:
            srv = sm.services['sessionMgr']
            srv.LogError('Session map borked')
            srv.LogError('sessionsByAttribute=', sessionsByAttribute)
            srv.LogError('sessionsBySID=', sessionsBySID)
            log.LogTraceback()
            raise 

    return cnt



def FindSessions(attr, val):
    ret = []
    for v in val:
        try:
            r = []
            for sid in sessionsByAttribute[attr].get(v, {}).iterkeys():
                if sid in sessionsBySID:
                    ret.append(sessionsBySID[sid])
                else:
                    r.append(sid)

            for each in r:
                del sessionsByAttribute[attr][v][each]

        except:
            srv = sm.services['sessionMgr']
            srv.LogError('Session map borked')
            srv.LogError('sessionsByAttribute=', sessionsByAttribute)
            srv.LogError('sessionsBySID=', sessionsBySID)
            log.LogTraceback()
            raise 

    return ret



def FindClients(attr, val):
    ret = []
    for v in val:
        try:
            r = []
            for sid in sessionsByAttribute[attr].get(v, {}).iterkeys():
                if sid in sessionsBySID:
                    s = sessionsBySID[sid]
                    if hasattr(s, 'clientID'):
                        ret.append(s.clientID)
                else:
                    r.append(sid)

            for each in r:
                del sessionsByAttribute[attr][v][each]

        except:
            srv = sm.services['sessionMgr']
            srv.LogError('Session map borked')
            srv.LogError('sessionsByAttribute=', sessionsByAttribute)
            srv.LogError('sessionsBySID=', sessionsBySID)
            log.LogTraceback()
            raise 

    return ret



def FindClientsAndHoles(attr, val, maxCount):
    ret = []
    nf = []
    attributes = attr.split('&')
    if len(attributes) > 1:
        if len(attributes) != len(val):
            raise RuntimeError('For a complex session query, the value must be a tuple of equal length to the complex query params')
        for i in range(len(val[0])):
            f = 0
            r = []
            for sid in sessionsByAttribute[attributes[0]].get(val[0][i], {}).iterkeys():
                if sid in sessionsBySID:
                    sess = sessionsBySID[sid]
                    k = 1
                    for j in range(1, len(val)):
                        if attributes[j] in ('corprole', 'rolesAtAll', 'rolesAtHQ', 'rolesAtBase', 'rolesAtOther'):
                            corprole = getattr(sess, attributes[j])
                            k = 0
                            for r2 in val[j]:
                                if r2 and r2 & corprole == r2:
                                    k = 1
                                    break

                        elif getattr(sess, attributes[j]) not in val[j]:
                            k = 0
                        if not k:
                            break

                    if k:
                        f = 1
                        clientID = getattr(sessionsBySID[sid], 'clientID', None)
                        if clientID is not None:
                            if maxCount is not None and len(ret) >= maxCount:
                                return (1, [], [])
                            ret.append(clientID)
                else:
                    r.append(sid)

            for each in r:
                del sessionsByAttribute[attributes[0]][val[0][i]][each]

            if not f:
                nf.append(val[0][i])

        if len(nf):
            nf2 = list(copy.copy(val))
            nf2[0] = nf
            nf = nf2
        return (0, ret, nf)
    for v in val:
        f = 0
        r = []
        for sid in sessionsByAttribute[attr].get(v, {}).iterkeys():
            if sid in sessionsBySID:
                clientID = getattr(sessionsBySID[sid], 'clientID', None)
                if clientID is not None:
                    if maxCount is not None and len(ret) >= maxCount:
                        return (1, [], [])
                    ret.append(clientID)
                    f = 1
            else:
                r.append(sid)

        for each in r:
            del sessionsByAttribute[attr][v][each]

        if not f:
            nf.append(v)

    return (0, ret, nf)



def FindSessionsAndHoles(attr, val, maxCount):
    ret = []
    nf = []
    attributes = attr.split('&')
    if len(attributes) > 1:
        if len(attributes) != len(val):
            raise RuntimeError('For a complex session query, the value must be a tuple of equal length to the complex query params')
        for i in range(len(val[0])):
            f = 0
            r = []
            for sid in sessionsByAttribute[attributes[0]].get(val[0][i], {}).iterkeys():
                if sid in sessionsBySID:
                    sess = sessionsBySID[sid]
                    k = 1
                    for j in range(1, len(val)):
                        if attributes[j] in ('corprole', 'rolesAtAll', 'rolesAtHQ', 'rolesAtBase', 'rolesAtOther'):
                            corprole = getattr(sess, attributes[j])
                            k = 0
                            for r2 in val[j]:
                                if r2 and r2 & corprole == r2:
                                    k = 1
                                    break

                        elif getattr(sess, attributes[j]) not in val[j]:
                            k = 0
                        if not k:
                            break

                    if k:
                        f = 1
                        clientID = getattr(sessionsBySID[sid], 'clientID', None)
                        if clientID is not None:
                            if maxCount is not None and len(ret) >= maxCount:
                                return (1, [], [])
                            ret.append(sessionsBySID[sid])
                else:
                    r.append(sid)

            for each in r:
                del sessionsByAttribute[attributes[0]][val[0][i]][each]

            if not f:
                nf.append(val[0][i])

        if len(nf):
            nf2 = list(copy.copy(val))
            nf2[0] = nf
            nf = nf2
        return (0, ret, nf)
    for v in val:
        f = 0
        r = []
        for sid in sessionsByAttribute[attr].get(v, {}).iterkeys():
            if sid in sessionsBySID:
                clientID = getattr(sessionsBySID[sid], 'clientID', None)
                if clientID is not None:
                    if maxCount is not None and len(ret) >= maxCount:
                        return (1, [], [])
                    ret.append(sessionsBySID[sid])
                    f = 1
            else:
                r.append(sid)

        for each in r:
            del sessionsByAttribute[attr][v][each]

        if not f:
            nf.append(v)

    return (0, ret, nf)



def GetSessions(sid = None):
    if sid is None:
        return sessionsBySID.values()
    else:
        return sessionsBySID.get(sid, None)



def CloseSession(sess, isRemote = 0):
    if sess is not None:
        if hasattr(sess, 'remoteServiceSessionRefCount'):
            sess.__dict__['remoteServiceSessionRefCount'] -= 1
            if sess.__dict__['remoteServiceSessionRefCount'] > 0:
                return 
        if sess.sid in sessionsBySID:
            sess.ClearAttributes(isRemote)



class ObjectcastCallWrapper():

    def __init__(self, object):
        self.object = weakref.proxy(object)



    def __call__(self, method, *args):
        sm.services['machoNet'].ObjectcastWithoutTheStars(self.object, method, args)




class UpdatePublicAttributesCallWrapper():

    def __init__(self, object):
        self.object = weakref.proxy(object)



    def __call__(self, *args, **keywords):
        pa = {}
        k = keywords.get('partial', [])
        for each in getattr(self.object, '__publicattributes__', []):
            if k and each not in k:
                continue
            if hasattr(self.object, each):
                pa[each] = getattr(self.object, each)

        sm.services['machoNet'].Objectcast(self.object, 'OnObjectPublicAttributesUpdated', GetObjectUUID(self.object), pa, args, keywords)



objectsByUUID = weakref.WeakValueDictionary({})
objectUUID = 0L

def GetObjectUUID(object):
    global objectUUID
    global objectsByUUID
    if hasattr(object, '__machoObjectUUID__'):
        return object.__machoObjectUUID__
    else:
        objectUUID += 1L
        if macho.mode == 'client':
            t = 'C=0:%s' % objectUUID
        else:
            t = 'N=%s:%s' % (sm.services['machoNet'].GetNodeID(), objectUUID)
        setattr(object, '__machoObjectUUID__', t)
        if not hasattr(object, '__publicattributes__'):
            setattr(object, '__publicattributes__', [])
        setattr(object, 'Objectcast', ObjectcastCallWrapper(object))
        setattr(object, 'UpdatePublicAttributes', UpdatePublicAttributesCallWrapper(object))
        objectsByUUID[t] = object
        return t



def GetObjectByUUID(uuid):
    try:
        return objectsByUUID.get(uuid, None)
    except ReferenceError:
        sys.exc_clear()
        return None



class SessionMgr(service.Service):
    __guid__ = 'svc.sessionMgr'
    __displayname__ = 'Session manager'
    __exportedcalls__ = {'GetSessionStatistics': [ROLE_SERVICE],
     'CloseUserSessions': [ROLE_SERVICE],
     'GetProxyNodeFromID': [ROLE_SERVICE],
     'GetClientIDFromID': [ROLE_SERVICE],
     'UpdateSessionAttributes': [ROLE_SERVICE],
     'ConnectToClientService': [ROLE_SERVICE],
     'PerformSessionChange': [ROLE_SERVICE],
     'GetLocalClientIDs': [ROLE_SERVICE],
     'EndAllGameSessions': [ROLE_ADMIN | ROLE_SERVICE],
     'PerformHorridSessionAttributeUpdate': [ROLE_SERVICE],
     'BatchedRemoteCall': [ROLE_SERVICE],
     'GetSessionDetails': [ROLE_SERVICE],
     'TerminateClientConnections': [ROLE_SERVICE | ROLE_ADMIN]}
    __dependencies__ = []
    __notifyevents__ = ['ProcessSessionChange', 'DoSessionChanging']

    def __init__(self):
        service.Service.__init__(self)
        if macho.mode == 'server':
            self.__dependencies__ += ['authentication', 'DB2']
        self.sessionClientIDCache = {'userid': {},
         'charid': {}}
        self.proxies = {}
        self.clientIDs = {}
        self.sessionChangeShortCircuitReasons = []
        self.additionalAttribsAllowedToUpdate = []
        self.additionalStatAttribs = []
        self.additionalSessionDetailsAttribs = []



    def GetProxySessionManager(self, nodeID):
        if nodeID not in self.proxies:
            self.proxies[nodeID] = self.session.ConnectToProxyServerService('sessionMgr', nodeID)
        return self.proxies[nodeID]



    def GetLocalClientIDs(self):
        ret = []
        for each in GetSessions():
            if hasattr(each, 'clientID'):
                ret.append(each.clientID)

        return ret



    def GetReason(self, oldReason, newReason, timeLeft):
        return mls.COMMON_SESSIONS_RAISEPSCIP_BASEREASON



    def __RaisePSCIP(self, oldReason, newReason, timeLeft = None):
        if oldReason is None:
            oldReason = ''
        if newReason is None:
            newReason = ''
        reason = self.GetReason(oldReason, newReason, timeLeft)
        self.LogInfo('raising a PerformSessionChangeInProgress user error with reason ', reason)
        raise UserError('PerformSessionChangeInProgress', {'reason': reason})



    def PerformSessionLockedOperation(self, *args, **keywords):
        return self.PerformSessionChange(*args, **keywords)



    def PerformSessionChange(self, sessionChangeReason, func, *args, **keywords):
        if 'hostileMutation' in keywords or 'violateSafetyTimer' in keywords or 'wait' in keywords:
            kw2 = copy.copy(keywords)
            hostile = keywords.get('hostileMutation', 0)
            wait = keywords.get('wait', 0)
            violateSafetyTimer = keywords.get('violateSafetyTimer', 0)
            if 'violateSafetyTimer' in kw2:
                del kw2['violateSafetyTimer']
            if 'hostileMutation' in kw2:
                del kw2['hostileMutation']
            if 'wait' in kw2:
                del kw2['wait']
        else:
            hostile = 0
            violateSafetyTimer = 0
            kw2 = keywords
            wait = 0
        self.LogInfo('Performing a locked session changing operation, reason=', sessionChangeReason)
        if macho.mode == 'client':
            sess = session
            if not violateSafetyTimer and hostile in (0, 1) and sess.charid:
                if sess.nextSessionChange is not None and sess.nextSessionChange > blue.os.GetTime():
                    if wait > 0:
                        t = 1000 * (2 + (session.nextSessionChange - blue.os.GetTime()) / const.SEC)
                        self.LogInfo('PerformSessionChange is sleeping for %s ms' % t)
                        blue.pyos.synchro.Sleep(t)
                if sess.nextSessionChange is not None and sess.nextSessionChange > blue.os.GetTime():
                    self.LogError("Too frequent session change attempts.  You'll just get yourself stuck doing this.  Ignoring.")
                    self.LogError('func=', func, ', args=', args, ', keywords=', keywords)
                    if sessionChangeReason in self.sessionChangeShortCircuitReasons:
                        return 
                    self._SessionMgr__RaisePSCIP(sess.sessionChangeReason, sessionChangeReason, sess.nextSessionChange - blue.os.GetTime())
            else:
                self.LogInfo('Passing session change stuck prevention speedbump.  hostile=', hostile)
        else:
            raise RuntimeError('Not Yet Implemented')
        if sess.mutating and hostile in (0, 1):
            if sessionChangeReason in self.sessionChangeShortCircuitReasons:
                self.LogInfo('Ignoring session change attempt due to ' + sessionChangeReason + ' overzealousness')
                return 
            self._SessionMgr__RaisePSCIP(sess.sessionChangeReason, sessionChangeReason)
        try:
            if hostile not in (2, 4):
                self.LogInfo('Incrementing the session mutation flag')
                sess.mutating += 1
            if sess.mutating == 1:
                self.LogInfo('Chaining ProcessSessionMutating event')
                sm.ChainEvent('ProcessSessionMutating', func, args, kw2)
                sess.sessionChangeReason = sessionChangeReason
            if hostile == 0:
                prev = sess.nextSessionChange
                if not violateSafetyTimer:
                    sess.nextSessionChange = blue.os.GetTime() + GetSessionChangeTimer(session.role)
                localNextSessionChange = sess.nextSessionChange
                self.LogInfo('Pre-op updating next legal session change to ', util.FmtDate(sess.nextSessionChange))
                self.LogInfo('Executing the session modification method')
                try:
                    return apply(func, args, kw2)
                except:
                    if localNextSessionChange >= sess.nextSessionChange:
                        sess.nextSessionChange = prev
                        self.LogInfo('post-op exception handler reverting next legal session change to ', util.FmtDate(sess.nextSessionChange))
                    else:
                        self.LogInfo("post-op exception handler - Someone else has modified nextSessionChange, so DON'T revert it - modified value is ", util.FmtDate(sess.nextSessionChange))
                    raise 
            elif hostile in (1, 3):
                self.LogInfo('Initiating Remote Mutation (local state change only), args=', args, ', keywords=', kw2)
            else:
                self.LogInfo('Finalizing Remote Mutation (local state change only), args=', args, ', keywords=', kw2)

        finally:
            self.LogInfo('Post-op updating next legal session change to ', util.FmtDate(sess.nextSessionChange))
            if hostile not in (1, 3):
                self.LogInfo('Decrementing the session mutation flag')
                sess.mutating -= 1
                if sess.mutating == 0:
                    self.LogInfo('Scattering OnSessionMutated event')
                    sm.ScatterEvent('OnSessionMutated', func, args, kw2)




    def GetProxyNodeFromID(self, idtype, theID, refresh = 0):
        if idtype != 'clientID':
            (clientID, refreshed,) = self.GetClientIDFromID(idtype, theID, refresh)
        else:
            clientID = theID
            refreshed = 0
        return (sm.services['machoNet'].GetProxyNodeIDFromClientID(clientID), refreshed)



    def IsPlayerCharacter(self, charID):
        raise Exception('stub function not implemented')



    def GetClientIDFromID(self, idtype, theID, refresh = 0):
        if theID in sessionsByAttribute[idtype]:
            sids = sessionsByAttribute[idtype][theID]
            for sid in sids:
                if sid in sessionsBySID:
                    s = sessionsBySID[sid]
                    if getattr(s, 'clientID', 0):
                        if theID in self.sessionClientIDCache[idtype]:
                            del self.sessionClientIDCache[idtype][theID]
                        return (s.clientID, 1)

        if not refresh and theID in self.sessionClientIDCache[idtype]:
            return (self.sessionClientIDCache[idtype][theID], 0)
        if not hasattr(self, 'dbzcluster'):
            self.dbzcluster = self.DB2.GetSchema('zcluster')
        if idtype == 'charid':
            if self.IsPlayerCharacter(theID):
                clientID = None
                if theID in self.clientIDs:
                    (clientID, lastTime,) = self.clientIDs[theID]
                    if blue.os.GetTime() - lastTime > const.SEC:
                        clientID = None
                if clientID is None:
                    client = self.dbzcluster.Cluster_ClientCharacter(theID)
                    if len(client) and client[0].clientID:
                        clientID = client[0].clientID
                self.clientIDs[theID] = (clientID, blue.os.GetTime())
            else:
                log.LogTraceback('Thou shall only use GetClientIDFromID for player characters', show_locals=1)
                clientID = None
        elif idtype == 'userid':
            clientID = None
            client = self.dbzcluster.Cluster_ClientUser(theID)
            if len(client) and client[0].clientID:
                clientID = client[0].clientID
        else:
            raise RuntimeError('Can only currently use userID or characterID to locate a client through the DB')
        if not clientID:
            raise UnMachoDestination('The dude is not logged on')
        else:
            self.sessionClientIDCache[idtype][theID] = clientID
            return (clientID, 1)



    def DoSessionChanging(self, *args):
        pass



    def ProcessSessionChange(self, isRemote, sess, change):
        if 'userid' in change and change['userid'][0] in self.sessionClientIDCache['userid']:
            del self.sessionClientIDCache['userid'][change['userid'][0]]
        if 'charid' in change and change['charid'][0] in self.sessionClientIDCache['charid']:
            del self.sessionClientIDCache['charid'][change['charid'][0]]
        if macho.mode == 'proxy':
            return -1



    def TypeAndNodeValidationHook(self, idType, id):
        pass



    def UpdateSessionAttributes(self, idtype, theID, dict):
        if idtype not in ['charid', 'userid'] + self.additionalAttribsAllowedToUpdate:
            raise RuntimeError("You shouldn't be calling this, as you obviously don't know what you're doing.  This is like one of the most sensitive things in the system, dude.")
        if macho.mode == 'proxy' and theID not in sessionsByAttribute[idtype]:
            raise UnMachoDestination('Wrong proxy or client not connected')
        if macho.mode == 'server' and idtype in ('userid', 'charid'):
            proxyNodeID = None
            try:
                (proxyNodeID, refreshed,) = self.GetProxyNodeFromID(idtype, theID, 1)
            except UnMachoDestination:
                sys.exc_clear()
            if proxyNodeID is not None:
                return self.GetProxySessionManager(proxyNodeID).UpdateSessionAttributes(idtype, theID, dict)
        sessions = FindSessions(idtype, [theID])
        if idtype == 'charid' and dict.has_key('flagRolesOnly') and sessions and len(sessions) > 0:
            sessioncorpid = sessions[0].corpid
            rolecorpid = dict['corpid']
            if sessioncorpid != rolecorpid:
                self.LogError('Character session is wrong!!! Character', theID, 'has session corp', sessioncorpid, 'but should be', rolecorpid, "I'll fix his session but please investigate why this occurred! Update dict:", dict, 'Session:', sessions[0])
        if dict.has_key('flagRolesOnly'):
            del dict['flagRolesOnly']
        self.TypeAndNodeValidationHook(idtype, theID)
        parallelCalls = []
        for each in sessions:
            if hasattr(each, 'clientID'):
                parallelCalls.append((self.PerformHorridSessionAttributeUpdate, (each.clientID, dict)))
            else:
                each.LogSessionHistory('Updating session information via sessionMgr::UpdateSessionAttributes')
                each.SetAttributes(dict)
                each.LogSessionHistory('Updated session information via sessionMgr::UpdateSessionAttributes')

        if len(parallelCalls) > 60:
            log.LogTraceback('Horrid session change going haywire.  Redesign the calling code!')
        uthread.parallel(parallelCalls)



    def PerformHorridSessionAttributeUpdate(self, clientID, dict):
        try:
            if macho.mode == 'server':
                (proxyNodeID, refreshed,) = self.GetProxyNodeFromID('clientID', clientID)
                return self.GetProxySessionManager(proxyNodeID).PerformHorridSessionAttributeUpdate(clientID, dict)
            s = sm.services['machoNet'].GetSessionByClientID(clientID)
            if s:
                s.LogSessionHistory('Updating session information via sessionMgr::UpdateSessionAttributes')
                s.SetAttributes(dict)
                s.LogSessionHistory('Updated session information via sessionMgr::UpdateSessionAttributes')
        except StandardError:
            log.LogException()
            sys.exc_clear()



    def GetSessionFromParams(self, idtype, theID):
        if idtype == 'clientID':
            s = sm.services['machoNet'].GetSessionByClientID(theID)
            if s is None:
                raise UnMachoDestination('Wrong proxy or client not connected, session not found by clientID=%s' % theID)
            return s
        if theID not in sessionsByAttribute[idtype]:
            raise UnMachoDestination('Wrong proxy or client not connected, session not found by %s=%s' % (idtype, theID))
        else:
            sids = sessionsByAttribute[idtype][theID].keys()
            if not len(sids) == 1:
                raise UnMachoDestination('Ambiguous idtype/id pair (%s/%s).  There are %d sessions that match them.' % (idtype, theID, len(sids)))
            else:
                sid = sids[0]
            if sid not in sessionsBySID:
                raise UnMachoDestination("The client's session is in an invalid or terminating state")
            return sessionsBySID[sid]



    def ConnectToClientService(self, svc, idtype, theID):
        if macho.mode == 'proxy':
            s = self.GetSessionFromParams(idtype, theID)
            return sm.services['machoNet'].ConnectToRemoteService(svc, macho.MachoAddress(clientID=s.clientID, service=svc), s)
        (proxyNodeID, refreshed,) = self.GetProxyNodeFromID(idtype, theID)
        try:
            return self.GetProxySessionManager(proxyNodeID).ConnectToClientService(svc, idtype, theID)
        except UnMachoDestination:
            sys.exc_clear()
            if not refreshed:
                return self.GetProxySessionManager(self.GetProxyNodeFromID(idtype, theID, 1)[0]).ConnectToClientService(svc, idtype, theID)



    def GetSessionStatistics(self):
        retval = {}
        for (attribute, sessionsByThisAttribute,) in sessionsByAttribute.iteritems():
            if attribute in ['userid', 'userType'] + self.additionalStatAttribs:
                statsByThisAttribute = {}
                for (thisAttribute, whohasit,) in sessionsByThisAttribute.iteritems():
                    statsByThisAttribute[thisAttribute] = len(whohasit)

                retval[attribute] = (len(sessionsByThisAttribute), statsByThisAttribute)

        return retval



    def Run(self, memstream = None):
        service.Service.Run(self, memstream)
        self.AppRun(memstream)



    def AppRun(self, memstream = None):
        pass



    def BatchedRemoteCall(self, batchedCalls):
        retvals = []
        for (callID, (service, method, args, keywords,),) in batchedCalls.iteritems():
            try:
                c = '%s::%s (Batched\\Server)' % (service, method)
                timer = PushMark(c)
                try:
                    with CallTimer(c):
                        retvals.append((0, callID, apply(getattr(sm.GetService(service), method), args, keywords)))

                finally:
                    PopMark(timer)

            except StandardError as e:
                if getattr(e, '__passbyvalue__', 0):
                    retvals.append((1, callID, strx(e)))
                else:
                    retvals.append((1, callID, e))
                sys.exc_clear()

        return retvals



    def GetSessionValuesFromRowset(self, si):
        return {}



    def GetInitialValuesFromCharID(self, charID):
        return {}



    def CloseUserSessions(self, userIDs, reason, clientID = None):
        if type(userIDs) not in (types.ListType, types.TupleType):
            userIDs = [userIDs]
        for each in FindSessions('userid', userIDs):
            if clientID is None or not hasattr(each, 'clientID') or each.clientID != clientID:
                each.LogSessionHistory(reason)
                CloseSession(each)




    def TerminateClientConnections(self, reason, filter):
        if macho.mode != 'proxy' or not isinstance(filter, types.DictType) or len(filter) == 0:
            raise RuntimeError('TerminateClientConnections should only be called on a proxy and with a non-empty filter dictionnary')
        numDisconnected = 0
        for clientSession in GetSessions():
            blue.pyos.BeNice()
            if hasattr(clientSession, 'clientID') and not clientSession.role & ROLE_SERVICE:
                clientID = getattr(clientSession, 'clientID')
                if clientID is None:
                    continue
                skip = False
                for (attr, value,) in filter.iteritems():
                    if not (hasattr(clientSession, attr) and getattr(clientSession, attr) == value):
                        skip = True
                        break

                if not skip:
                    numDisconnected += 1
                    clientSession.LogSessionHistory('Connection terminated by administrator %s, reason is: %s' % (str(session.userid), reason))
                    sm.GetService('machoNet').TerminateClient(reason, clientID)

        return numDisconnected



    def EndAllGameSessions(self, remote = 0):
        if remote:
            self.session.ConnectToAllProxyServerServices('sessionMgr').EndAllGameSessions()
        else:
            txt = ''
            for s in GetSessions():
                blue.pyos.BeNice()
                if hasattr(s, 'clientID') and not s.role & ROLE_SERVICE:
                    sid = s.sid
                    s.LogSessionHistory('Session closed by administrator %s' % str(session.userid))
                    CloseSession(s)




    def GetSessionDetails(self, clientID, sid):
        import htmlwriter
        if clientID:
            s = sm.GetService('machoNet').GetSessionByClientID(clientID)
        else:
            s = GetSessions(sid)
        if s is None:
            return 
        info = [['sid', s.sid],
         ['version', s.version],
         ['clientID', getattr(s, 'clientID', '')],
         ['userid', s.userid],
         ['userType', s.userType],
         ['role', s.role],
         ['charid', s.charid],
         ['lastRemoteCall', s.lastRemoteCall]]
        for each in self.additionalSessionDetailsAttribs:
            info.append([each, s.__dict__[each]])

        (sessionsBySID, sessionsByAttribute,) = GetSessionMaps()
        for each in info:
            if each[0] == 'sid':
                if each[1] not in sessionsBySID:
                    each[1] = str(each[1]) + ' <b>(Not in sessionsBySID)</b>'
            elif each[0] in sessionsByAttribute:
                a = getattr(s, each[0])
                if a:
                    if a not in sessionsByAttribute[each[0]]:
                        each[1] = str(each[1]) + " <b>(Not in sessionsByAttribute['%s'])</b>" % each[0]
                    elif s.sid not in sessionsByAttribute[each[0]].get(a, {}):
                        each[1] = str(each[1]) + " <b>(Not in sessionsByAttribute['%s']['%s'])</b>" % (each[0], a)

        info.append(['IP Address', getattr(s, 'address', '?')])
        connectedObjects = []
        hd = ['ObjectID', 'References', 'Object']
        for (k, v,) in s.machoObjectsByID.iteritems():
            tmp = [k, '%s.%s' % (util.FmtDate(v[0]), v[0] % const.SEC), htmlwriter.Swing(str(v[1]))]
            if isinstance(v[1], ObjectConnection):
                tmp[2] = str(tmp[2]) + ' (c2ooid=%s)' % str(v[1].__dict__['__c2ooid__'])
                if v[1].__dict__['__c2ooid__'] not in s.connectedObjects:
                    tmp[2] = str(tmp[2]) + ' <b>(Not in s.connectedObjects)</b>'
                else:
                    object = v[1].__dict__['__object__']
                    if not hasattr(object, 'sessionConnections'):
                        tmp[2] = str(tmp[2]) + ' <b>(Object does not have sessionConnections)</b>'
                    elif s.sid not in object.sessionConnections:
                        tmp[2] = str(tmp[2]) + ' <b>(s.sid not in object.sessionConnections)</b>'
                    if not hasattr(object, 'objectConnections'):
                        tmp[2] = str(tmp[2]) + ' <b>(Object does not have objectConnections)</b>'
                    elif (s.sid, v[1].__dict__['__c2ooid__']) not in object.objectConnections:
                        tmp[2] = str(tmp[2]) + ' <b>((s.sid,c2ooid) not in object.sessionConnections)</b>'
            if k not in sessionsByAttribute['objectID']:
                tmp[2] = str(tmp[2]) + " <b>(Not in sessionsByAttribute['objectID'])</b>"
            elif s.sid not in sessionsByAttribute['objectID'][k]:
                tmp[2] = str(tmp[2]) + " <b>(Not in sessionsByAttribute['objectID']['%s'])</b>" % k
            connectedObjects.append(tmp)

        sessionHistory = []
        lastEntry = ''
        i = 0
        for each in s.sessionhist:
            tmp = each[2].replace('\n', '<br>')
            if tmp == lastEntry:
                txt = '< same >'
            else:
                txt = tmp
            lastEntry = tmp
            sessionHistory.append((each[0],
             i,
             each[1],
             htmlwriter.Swing(txt)))
            i += 1

        return (info,
         connectedObjects,
         sessionHistory,
         s.calltimes,
         s.sessionVariables)



exports = {'base.CreateUserSession': CreateSession,
 'base.CreateSession': CreateSession,
 'base.SessionMgr': SessionMgr,
 'base.GetServiceSession': GetServiceSession,
 'base.CloseSession': CloseSession,
 'base.GetSessions': GetSessions,
 'base.FindSessions': FindSessions,
 'base.CountSessions': CountSessions,
 'base.FindClientsAndHoles': FindClientsAndHoles,
 'base.FindSessionsAndHoles': FindSessionsAndHoles,
 'base.ObjectConnection': ObjectConnection,
 'base.GetCallTimes': GetCallTimes,
 'base.CallTimer': CallTimer,
 'base.EnableCallTimers': EnableCallTimers,
 'base.CallTimersEnabled': CallTimersEnabled,
 'base.FindClients': FindClients,
 'base.GetSessionMaps': GetSessionMaps,
 'base.GetAllSessionInfo': GetAllSessionInfo,
 'base.allObjectConnections': allObjectConnections,
 'base.allConnectedObjects': allConnectedObjects,
 'base.GetUndeadObjects': GetUndeadObjects,
 'base.GetObjectUUID': GetObjectUUID,
 'base.GetObjectByUUID': GetObjectByUUID,
 'base.sessionChangeDelay': SESSIONCHANGEDELAY,
 'base.GetNewSid': GetNewSid,
 'base.sessionsBySID': sessionsBySID,
 'base.allSessionsBySID': allSessionsBySID,
 'base.sessionsByAttribute': sessionsByAttribute,
 'base.outstandingCallTimers': outstandingCallTimers,
 'base.dyingObjects': dyingObjects}

