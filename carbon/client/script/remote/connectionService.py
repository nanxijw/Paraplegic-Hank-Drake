from service import Service
import blue
import uthread
import log
import const
import service
import sys
import base
import util
import uiconst
DEFAULTLONGWAITWARNINGSECS = 300
LONGWAITWARNINGMETHODS = ['MachoBindObject', 'SelectCharacterID']

class ClientShell:
    __guid__ = 'base.ClientShell'

    def __init__(self):
        self.notify = {}



    def Register(self, eventid, func):
        if not self.notify.has_key(eventid):
            self.notify[eventid] = []
        self.notify[eventid].append(func)



    def OnEvent(self, eventid, *args):
        print 'ConnectionService::ClientShell is actually being used!  sacrifice the goats!'
        if self.notify.has_key(eventid):
            for func in self.notify[eventid]:
                handled = apply(func, args)
                if handled:
                    return 





class ConnectionService(Service):
    __guid__ = 'svc.connection'
    __servicename__ = 'connection'
    __displayname__ = 'Network Connection Service'
    __exportedcalls__ = {'Connect': [],
     'Disconnect': [],
     'IsConnected': [],
     'ConnectToService': [],
     'Login': []}
    __dependencies__ = ['machoNet']
    __notifyevents__ = ['ProcessLoginProgress']

    def __init__(self):
        Service.__init__(self)
        self.shell = None
        self.reentrancyGaurd = 0
        self.processingBulkData = False
        self.clocksynchronizing = 0
        self.clocklastsynchronized = None
        self.lastLongCallTimestamp = 0
        blue.pyos.synchro.timesyncs.append(self.OnTimerResync)



    def Run(self, *args):
        Service.Run(self, *args)
        uthread.worker('ConnectionService::LongCallTimer', self._ConnectionService__LongCallTimer)
        uthread.new(self.TryAutomaticLogin)



    def OnTimerResync(self, old, new):
        if session and session.nextSessionChange:
            diff = new - old
            log.general.Log('Readjusting next session change by %.3f seconds' % (diff / float(const.SEC)), log.LGINFO)
            session.nextSessionChange += diff



    def Connect(self, host, port, userid, password, ct):
        try:
            self.LogInfo('calling connect')
            address = '%s:%d' % (str(host), port)
            response = self.machoNet.ConnectToServer(address, userid, password, ct)
            self.LogInfo('connect completed...')
        except GPSException as what:
            self.LogError('connect failed %s' % what)
            raise UserError('LoginConnectFailed', {'what': what})
        self.SynchronizeClock()
        return response



    def ProcessLoginProgress(self, what, prefix = None, current = 1, total = 1, response = None):
        if what not in cfg.messages:
            text = "In ProcessLoginProgress, '%s' not found in messages" % what
            log.LogTraceback(extraText=text, channel='_Mls.General', severity=log.LGERR)
            return 
        self.processingBulkData = 0
        msg = cfg.Format(what)
        useMorph = 1
        if what == 'loginprogress::gettingbulkdata':
            self.processingBulkData = total
            msg += ' ' + str(current) + '/' + str(total)
            useMorph = 0
        uthread.new(sm.GetService('loading').ProgressWnd, mls.UI_LOGIN_LOGGINGIN, msg, current, total, useMorph=useMorph, autoTick=useMorph)
        blue.pyos.synchro.Yield()



    def Login(self, loginparam, selchar = None):
        if self.reentrancyGaurd:
            return 
        self.reentrancyGaurd = 1
        try:
            if loginparam is None:
                raise RuntimeError('loginparam can not be None anymore dude')
            if loginparam[4]:
                ct = 'udp'
            else:
                ct = 'tcp'
            response = self.Connect(loginparam[2], loginparam[3], loginparam[0], loginparam[1], ct)
            return response

        finally:
            self.reentrancyGaurd = 0




    def Disconnect(self, silently = 0):
        if self.reentrancyGaurd:
            return 
        self.reentrancyGaurd = 1
        try:
            self.machoNet.DisconnectFromServer()

        finally:
            self.reentrancyGaurd = 0




    def ConnectToProxyService(self, serviceName):
        return session.ConnectToRemoteService(serviceName, sm.services['machoNet'].myProxyNodeID)



    def ConnectToService(self, serviceName):
        return session.ConnectToRemoteService(serviceName)



    def IsConnected(self):
        return self.machoNet.IsConnected()



    def SynchronizeClock(self, firstTime = 1, maxIterations = 5):
        log.general.Log('connection.synchronizeClock called', log.LGINFO)
        if not firstTime:
            if self.clocklastsynchronized is not None and blue.os.GetTime() - self.clocklastsynchronized < const.HOUR:
                return 
        if self.clocksynchronizing:
            return 
        self.clocklastsynchronized = blue.os.GetTime()
        self.clocksynchronizing = 1
        try:
            diff = 0
            goodCount = 0
            lastElaps = None
            log.general.Log('***   ***   ***   ***   Clock Synchronizing loop initiating      ***   ***   ***   ***', log.LGINFO)
            for i in range(maxIterations):
                myTime = blue.os.GetTime(1)
                serverTime = sm.ProxySvc('machoNet').GetTime()
                now = blue.os.GetTime(1)
                elaps = now - myTime
                serverTime += elaps / 2
                diff = float(now - serverTime) / float(const.SEC)
                if diff > 2.0 and not firstTime:
                    logflag = log.LGERR
                else:
                    logflag = log.LGINFO
                log.general.Log('Synchronizing clock diff %.3f sec elaps %f sec.' % (diff, elaps / float(const.SEC)), logflag)
                if lastElaps is None or elaps < lastElaps and elaps < const.SEC:
                    goodCount += 1
                    log.general.Log('Synchronizing clock:  iteration completed, setting time', logflag)
                    blue.pyos.synchro.ResetClock(serverTime)
                    lastElaps = elaps
                else:
                    log.general.Log('Synchronizing clock:  iteration ignored as it was less accurate (%f) than our current time (%f)' % (elaps / float(const.SEC), lastElaps / float(const.SEC)), log.LGINFO)
                if goodCount >= 3:
                    break
                firstTime = 0

            log.general.Log('***   ***   ***   ***   Clock Synchronizing loop completed       ***   ***   ***   ***', log.LGINFO)

        finally:
            self.clocksynchronizing = 0




    def IsClockSynchronizing(self):
        if self.clocksynchronizing:
            log.general.Log('Clock synchronization in progress', log.LGINFO)
        return self.clocksynchronizing



    def __LongCallTimer(self):
        longWarningSecs = prefs.GetValue('longOutstandingCallWarningSeconds', DEFAULTLONGWAITWARNINGSECS)
        sleepSecs = 60
        if longWarningSecs < sleepSecs:
            sleepSecs = longWarningSecs
        self.LogInfo('__LongCallTimer reporting warnings after', longWarningSecs, 'seconds and checking every', sleepSecs, 'seconds')

        def ShouldWarn(method):
            for w in LONGWAITWARNINGMETHODS:
                if w in repr(method):
                    return True

            return False


        while self.state == service.SERVICE_RUNNING:
            if sm.GetService('machoNet').GetClientConfigVals().get('disableLongCallWarning'):
                self.LogWarn('__LongCallTimer should not be running! Exiting.')
                return 
            blue.pyos.synchro.Sleep(sleepSecs * 1000)
            try:
                maxDiff = 0
                for ct in base.outstandingCallTimers:
                    method = ct[0]
                    t = ct[1]
                    diff = blue.os.GetTime(1) - t
                    if diff > maxDiff and ShouldWarn(method):
                        maxDiff = diff
                    if diff > 60 * const.SEC:
                        self.LogWarn('Have waited', util.FmtTime(diff), 'for', method)

                if maxDiff > longWarningSecs * const.SEC and self.lastLongCallTimestamp < blue.os.GetTime(1) - longWarningSecs * const.SEC:
                    modalWnd = uicore.registry.GetModalWindow()
                    if modalWnd:
                        modalWnd.SetModalResult(uiconst.ID_CLOSE)
                    uthread.new(uicore.Message, 'LongWaitForRemoteCall', {'time': int(maxDiff / const.MIN)})
                    self.lastLongCallTimestamp = blue.os.GetTime(1)
            except:
                log.LogException()
                sys.exc_clear()




    def TryAutomaticLogin(self):
        if util.GetLoginCredentials() is None or session.userid is not None:
            return 
        (username, password,) = util.GetLoginCredentials()
        self.Login((username,
         password,
         util.GetServerName(),
         util.GetServerPort(),
         None))




