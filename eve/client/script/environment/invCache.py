import service
import util
import dbutil
import moniker
import blue
import uthread
import stackless
import traceback
import types
import uix
import lg
import sys
import dbg
import inventoryFlagsCommon
import yaml
import os
import log
from collections import defaultdict
SEC = 10000000L
MIN = SEC * 60L
HOUR = MIN * 60L

class invCache(service.Service):
    __guid__ = 'svc.invCache'
    __sessionparams__ = []
    __exportedcalls__ = {'GetInventory': [],
     'GetInventoryFromId': [],
     'GetInventoryMgr': [],
     'GetItemHeader': [],
     'IsItemLocked': [],
     'TryLockItem': [],
     'UnlockItem': [],
     'InvalidateGlobal': [],
     'GetStationIDOfItem': [],
     'GetStationIDOfficeFolderIDOfficeIDOfItem': [],
     'IsInventoryPrimedAndListed': [],
     'InvalidateLocationCache': []}
    __dependencies__ = []
    __notifyevents__ = ['ProcessSessionChange',
     'OnSessionChanged',
     'OnItemsChanged',
     'OnItemChange',
     'OnCapacityChange',
     'OnPasswordChanged',
     'DoBallRemove']

    def __init__(self):
        service.Service.__init__(self)
        self._invCache__invmgr = None
        self._invCache__invlocID = 0
        self._invCache__itemhdr = None
        self.inventories = {}
        self.containerGlobal = None
        self.lockedItems = {}
        self.lockedItemsSemaphore = None
        self.trace = 0
        self.locks = {}



    def Run(self, ms = None):
        sm.FavourMe(self.OnItemChange)
        sm.FavourMe(self.ProcessSessionChange)
        sm.FavourMe(self.OnCapacityChange)
        self.LogInfo('invCache lock tracing:', ['OFF', 'ON'][self.trace])
        if self.lockedItemsSemaphore is None:
            self.lockedItemsSemaphore = uthread.Semaphore()



    def Stop(self, stream):
        self.InvalidateCache()



    def DoBallRemove(self, ball, slimItem, terminal):
        if ball is None:
            return 
        if self.inventories.has_key((ball.id, None)):
            del self.inventories[(ball.id, None)]



    def ProcessSessionChange(self, isRemote, session, change):
        try:
            if not session.charid:
                return self.InvalidateCache()
            if change.has_key('corprole') and eve.session.stationid:
                self.LogInfo('ProcessSessionChange corprole in station')
                office = sm.GetService('corp').GetOffice()
                if office is not None:
                    key = (office.itemID, None)
                    if self.inventories.has_key(key):
                        self.LogInfo('Removing invnetory for corp hangar')
                        del self.inventories[key]
            if change.has_key('shipid') and session.solarsystemid is not None:
                if change['shipid'][0] in self.inventories:
                    del self.inventories[change['shipid'][0]]
                return 
            if not (change.has_key('stationid') or change.has_key('solarsystemid')):
                return 
            self.InvalidateCache()

        finally:
            sm.services['godma'].ProcessSessionChange(isRemote, session, change)




    def OnSessionChanged(self, isRemote, sess, change):
        if service.ROLE_ADMIN & eve.session.role == service.ROLE_ADMIN:
            self.trace = 1
        else:
            self.trace = 0
        if 'regionid' in change:
            try:
                f = blue.os.CreateInstance('blue.ResFile')
                filename = os.path.join(u'res:/planetAttributes/', unicode(str(change['regionid'][1]) + '.region'))
                if f is not None and f.Open(filename):
                    data = f.Read()
                    cfg.planetattributes.data = blue.marshal.Load(data)
                    f.Close()
            except:
                self.LogError('Could not load planet attributes for region', change['regionid'][1], '- the following exception should give more information why.')
                log.LogException()
                sys.exc_clear()
        if change.has_key('corprole') and eve.session.stationid:
            self.LogInfo('OnSessionChanged corprole in station')
            office = sm.GetService('corp').GetOffice()
            if office is not None:
                wndid = 'corpHangar_%s' % office.itemID
                wasopen = sm.GetService('window').GetWndState(wndid, 'open')
                self.LogInfo("Char's corp has a hangar wndid", wndid, 'wasopen', wasopen)
                if wasopen:
                    wnd = sm.GetService('window').GetWindow(wndid)
                    if wnd:
                        self.LogInfo('Closing corphangar')
                        wnd.CloseX()
                key = (office.itemID, None)
                if self.inventories.has_key(key):
                    self.LogInfo('Removing invnetory for corp hangar')
                    del self.inventories[key]
                if wasopen:
                    if not (change.has_key('corpid') and change['corpid'][0] != None):
                        self.LogInfo('Reopening corp hangar for player')
                        sm.GetService('window').OpenCorpHangar(office.itemID, office.officeFolderID)



    def OnPasswordChanged(self, which, containerItem):
        self.RemoveInventoryContainer(containerItem)



    def __getattr__(self, key):
        if key == 'inventorymgr':
            while eve.session.IsMutating() and not eve.session.IsChanging():
                self.LogInfo('Sleeping while waiting for a session change or mutation to complete')
                blue.pyos.synchro.Sleep(250)

            if self._invCache__invmgr is None or self._invCache__invlocID != eve.session.locationid:
                self._invCache__invlocID = eve.session.locationid
                self._invCache__invmgr = moniker.GetInventoryMgr()
            return self._invCache__invmgr
        if self.__dict__.has_key(key):
            return self.__dict__[key]
        raise AttributeError, key



    def OnItemsChanged(self, items, change):
        self.LogInfo('server says do change ', change, ' for ', len(items), ' items:', items)
        for (i, item,) in enumerate(items):
            sm.ScatterEvent('OnItemChange', item, change)
            blue.pyos.BeNice()




    def OnItemChange(self, item, change):
        if const.ixQuantity in change:
            log.LogTraceback('invCache processing a ixQuantity change')
            if change[const.ixQuantity] < 0 or item.quantity < 0:
                raise RuntimeError('OnItemChange in invCache: negative qty', item, change)
        try:
            lockKey = item.itemID
            uthread.Lock(self, lockKey)
            try:
                self.LockedItemChange(item, change)
                oldItem = blue.DBRow(item)
                for (k, v,) in change.iteritems():
                    if k in (const.ixStackSize, const.ixSingleton):
                        k = const.ixQuantity
                    oldItem[k] = v

                (keyIs, keyWas,) = (None, None)
                if eve.session.stationid:
                    if item.locationID == eve.session.stationid:
                        if item.ownerID == eve.session.charid:
                            keyIs = (const.containerHangar, None)
                        elif item.flagID == const.flagCorpMarket:
                            keyIs = (const.containerCorpMarket, item.ownerID)
                        else:
                            keyIs = (const.containerHangar, item.ownerID)
                    if oldItem.locationID == eve.session.stationid:
                        if oldItem.ownerID == eve.session.charid:
                            keyWas = (const.containerHangar, None)
                        elif oldItem.flagID == const.flagCorpMarket:
                            keyWas = (const.containerCorpMarket, oldItem.ownerID)
                        else:
                            keyWas = (const.containerHangar, oldItem.ownerID)
                if keyIs is None:
                    keyIs = (item.locationID, None)
                if keyWas is None:
                    keyWas = (oldItem.locationID, None)
                if keyWas and self.inventories.has_key(keyWas):
                    inv = self.inventories[keyWas]
                    inv.OnItemChange(item, change)
                if keyIs != keyWas or const.ixFlag in change:
                    if keyIs and self.inventories.has_key(keyIs):
                        inv = self.inventories[keyIs]
                        inv.OnItemChange(item, change)
                if util.IsJunkLocation(item.locationID) or const.ixOwnerID in change or (const.ixQuantity in change or const.ixStackSize in change) and item.stacksize == 0:
                    if util.IsJunkLocation(item.locationID):
                        self.LogInfo('REMOVING:', item.itemID, 'item is in junk location')
                    elif const.ixOwnerID in change:
                        self.LogInfo('REMOVING:', item.itemID, ' ownership changed')
                    elif const.ixStackSize in change and item.stacksize == 0:
                        self.LogInfo('REMOVING:', item.itemID, ' new stacksize is 0')
                    if const.ixLocationID in change:
                        if self.containerGlobal:
                            self.containerGlobal.TrashItem(change[const.ixLocationID], item.itemID, item.locationID)
                if self.inventories.has_key((item.itemID, None)):
                    if oldItem.ownerID == eve.session.charid != item.ownerID:
                        del self.inventories[(item.itemID, None)]
                    else:
                        self.inventories[(item.itemID, None)].item = item

            finally:
                sm.services['godma'].OnItemChange(item, change)
                sm.services['inv'].OnItemChange(item, change)


        finally:
            uthread.UnLock(self, lockKey)




    def LockedItemChange(self, item, change):
        self.UnlockItem(item.itemID)



    def TryLockItem(self, itemID, userErrorName = '', userErrorDict = {}, raiseIfLocked = 0):
        (bIsLocked, lockTime, co_name, co_filename, co_lineno,) = (0, 0, None, None, None)
        try:
            self.lockedItemsSemaphore.acquire()
            self.LogInfo('TryLockItem', itemID)
            (bIsLocked, xlockTime, xuserErrorName, xuserErrorDict, co_name, co_filename, co_lineno,) = self.IsItemLocked_NoLock(itemID)
            if bIsLocked:
                (lockTime, userErrorName, userErrorDict,) = (xlockTime, xuserErrorName, xuserErrorDict)
            else:
                co_name = None
                co_filname = None
                co_lineno = None
                if self.trace:
                    frames = traceback.extract_stack(limit=2)
                    frame = frames[1]
                    if frame[0].endswith('service.py'):
                        frame = frames[0]
                    co_name = frame[2]
                    co_filname = frame[0]
                    co_lineno = frame[1]
                    self.LogInfo('TryLockItem called by ', co_name, ' ', co_filename, '(', co_lineno, ')')
                now = blue.os.GetTime()
                self.lockedItems[itemID] = (now,
                 userErrorName,
                 userErrorDict,
                 co_name,
                 co_filname,
                 co_lineno)
                self.LogInfo('Locked Item', itemID)
                sm.ScatterEvent('OnItemLocked', itemID)
                return 1

        finally:
            self.lockedItemsSemaphore.release()

        if bIsLocked and raiseIfLocked:
            self.RaiseLockError(itemID, lockTime, userErrorName, userErrorDict, co_name, co_filename, co_lineno)
        return bIsLocked



    def RaiseLockError(self, itemID, lockTime, userErrorName, userErrorDict, co_name, co_filename, co_lineno):
        if len(userErrorName) == 0:
            userErrorName = 'ItemIsLocked'
            userErrorDict = {'reason': mls.UI_GENERIC_NOREASONWASSPECIFIED,
             'lockTime': util.FmtDate(lockTime)}
        if userErrorDict == type({}):
            userErrorDict['lockTime'] = lockTime
        if not self.trace:
            raise UserError(userErrorName, userErrorDict)
        message = cfg.GetMessage(userErrorName, userErrorDict)
        msgDict = {}
        if co_name is None:
            co_name = mls.UI_GENERIC_UNKNOWN
        if co_filename is None:
            co_filename = mls.UI_GENERIC_UNKNOWN
        if co_lineno is None:
            co_lineno = mls.UI_GENERIC_UNKNOWN
        msgDict['title'] = message.title
        msgDict['text'] = message.text
        msgDict['itemID'] = itemID
        msgDict['co_name'] = co_name
        msgDict['co_filename'] = co_filename
        msgDict['co_lineno'] = co_lineno
        msgDict['lockTime'] = util.FmtDate(lockTime)
        raise UserError('AdminReportItemLocked', msgDict)



    def UnlockItem(self, itemID):
        try:
            self.lockedItemsSemaphore.acquire()
            self.UnlockItem_NoLock(itemID)

        finally:
            self.lockedItemsSemaphore.release()




    def UnlockItem_NoLock(self, itemID):
        self.LogInfo('UnlockItem_NoLock', itemID)
        if self.lockedItems.has_key(itemID):
            del self.lockedItems[itemID]
            self.LogInfo('Unlocked Item:', itemID)
            sm.ScatterEvent('OnItemUnlocked', itemID)
        else:
            self.LogInfo('UnlockItem_NoLock irrelevant item:', itemID)



    def IsItemLocked(self, itemID, raiseIfLocked = 0):
        (bIsLocked, lockTime, userErrorName, userErrorDict, co_name, co_filename, co_lineno,) = (0,
         0,
         '',
         {},
         None,
         None,
         None)
        try:
            self.lockedItemsSemaphore.acquire()
            (bIsLocked, lockTime, userErrorName, userErrorDict, co_name, co_filename, co_lineno,) = self.IsItemLocked_NoLock(itemID)

        finally:
            self.lockedItemsSemaphore.release()

        if bIsLocked and raiseIfLocked:
            self.RaiseLockError(itemID, lockTime, userErrorName, userErrorDict, co_name, co_filename, co_lineno)
        return bIsLocked



    def IsItemLocked_NoLock(self, itemID):
        if not self.lockedItems.has_key(itemID):
            return (0,
             0,
             '',
             {},
             None,
             None,
             None)
        (lockTime, userErrorName, userErrorDict, co_name, co_filename, co_lineno,) = self.lockedItems[itemID]
        return (1,
         lockTime,
         userErrorName,
         userErrorDict,
         co_name,
         co_filename,
         co_lineno)



    def RemoveInventoryContainer(self, containerItem):
        self.LogInfo('Removing', cfg.invtypes.Get(containerItem.typeID).typeName, 'container', containerItem.itemID, 'from cache as ownership has changed.')
        if not self.inventories.has_key((containerItem.itemID, None)):
            self.LogInfo('RemoveInventoryContainer container not found in inventories')
            return 
        for (itemID, item,) in self.inventories[(containerItem.itemID, None)].cachedItems.iteritems():
            if cfg.IsContainer(item):
                self.RemoveInventoryContainer(item)

        self.CloseContainer(containerItem.itemID)
        del self.inventories[(containerItem.itemID, None)]



    def CloseContainer(self, id_):
        wnd = sm.GetService('window').GetWindow('loot_%s' % id_)
        if wnd is None:
            wnd = sm.GetService('window').GetWindow('shipCargo_%s' % id_)
            if wnd is None:
                wnd = sm.GetService('window').GetWindow('drones_%s' % id_)
        if wnd is not None and not wnd.destroyed:
            wnd.SelfDestruct()
        else:
            self.LogInfo('CloseContainer window NOT found')



    def GetInventoryMgr(self):
        return self.inventorymgr



    def GetItemHeader(self, force = 0):
        if self._invCache__itemhdr is None or force:
            self._invCache__itemhdr = sm.RemoteSvc('invbroker').GetItemDescriptor()
            self.LogInfo('invCache got remote itemhdr', self._invCache__itemhdr)
        return self._invCache__itemhdr



    def GetInventory(self, containerid, param1 = None):
        if self._invCache__invlocID != eve.session.locationid:
            self.InvalidateCache()
        specials = [const.containerWallet,
         const.containerStationCharacters,
         const.containerOffices,
         const.containerGlobal,
         const.containerSolarSystem,
         const.containerRecycler,
         const.containerCharacter]
        if containerid in specials:
            if containerid == const.containerGlobal:
                if self.containerGlobal is None:
                    inv = util.Moniker('charMgr', (session.charid, containerid))
                    self.containerGlobal = inv5MinCacheContainer(inv)
                return self.containerGlobal
            inv = self.inventorymgr.GetInventory(containerid, param1)
            inv.SetSessionCheck({'locationid': self._invCache__invlocID})
            return inv
        key = (containerid, param1)
        if not self.inventories.has_key(key):
            inv = self.inventorymgr.GetInventory(containerid, param1)
            inv.SetSessionCheck({'locationid': self._invCache__invlocID})
            self.inventories[key] = invCacheContainer(inv, key)
        return self.inventories[key]



    def GetInventoryFromId(self, itemid, passive = 0):
        if itemid is None:
            log.LogTraceback('Thou shalt not send None in as itemid to GetInventoryFromId')
            raise IndexError
        try:
            if self._invCache__invlocID != eve.session.locationid:
                self.InvalidateCache()
            key = (itemid, None)
            if self.inventories.has_key(key):
                return self.inventories[key]
            else:
                inv = self.inventorymgr.GetInventoryFromId(itemid, passive)
                inv.SetSessionCheck({'locationid': self._invCache__invlocID})
                self.inventories[key] = invCacheContainer(inv, key)
                return self.inventories[key]
        except UserError as e:
            if e.args[0] == 'CrpAccessDenied':
                self.CloseContainer(itemid)
            raise 



    def IsInventoryPrimedAndListed(self, itemid):
        key = (itemid, None)
        inv = self.inventories.get(key, None)
        if inv is not None and inv.listed == 1:
            return True
        return False



    def InvalidateGlobal(self):
        self.containerGlobal = None
        self.cachedStations = (0, [])
        self.cachedStationsBp = (0, [])



    def InvalidateCache(self):
        self._invCache__invmgr = None
        self.containerGlobal = None
        for containerGuard in self.inventories.itervalues():
            containerGuard.moniker = None

        self.inventories = {}
        self.lockedItems = {}
        lockKeys = self.locks.keys()
        for lockKey in lockKeys:
            uthread.UnLock(self, lockKey)

        self.locks = {}



    def InvalidateLocationCache(self, itemID):
        key = itemID if isinstance(itemID, tuple) else (itemID, None)
        try:
            self.inventories[key].moniker = None
            del self.inventories[key]
            self.LogInfo('Invalidated location cache for ', key)
        except KeyError:
            pass



    def OnCapacityChange(self, moduleID):
        key = (moduleID, None)
        if self.inventories.has_key(key):
            self.inventories[key].capacityByFlag = {}
            self.inventories[key].capacityByLocation = None



    def GetStationIDOfItem(self, item):
        return self.GetStationIDOfficeFolderIDOfficeIDOfItem(item)[0]



    def GetStationIDOfficeFolderIDOfficeIDOfItem(self, item):
        if util.IsStation(item.locationID):
            return (item.locationID, None, None)
        offices = sm.GetService('corp').GetMyCorporationsOffices().SelectByUniqueColumnValues('officeID', [item.locationID])
        if offices and len(offices):
            for office in offices:
                if item.locationID == office.officeID:
                    return (office.stationID, office.officeFolderID, office.officeID)

        return (None, None, None)




class inv5MinCacheContainer():
    __guid__ = 'invCache.inv5MinCacheContainer'
    __update_on_reload__ = 1

    def __init__(self, moniker):
        self.moniker = moniker
        self.listed = None
        self.cachedItems = {}
        self.listTime = None
        self.cachedStationItems = {}
        self.cachedStationBpItems = {}
        self.cachedStationBpItemsCorp = {}
        self.cachedStations = (0, [])
        self.cachedStationsBp = (0, [])
        self.cachedStationsCorp = (0, [])
        self.cachedStationsBpCorp = (0, [])
        self.crits = {}



    def __EnterCriticalSection(self, k, v = None):
        if (k, v) not in self.crits:
            self.crits[(k, v)] = uthread.CriticalSection((k, v))
        self.crits[(k, v)].acquire()



    def __LeaveCriticalSection(self, k, v = None):
        self.crits[(k, v)].release()
        if (k, v) in self.crits and self.crits[(k, v)].IsCool():
            del self.crits[(k, v)]



    def __str__(self):
        try:
            return 'Global inventory for %s:%d' % (cfg.eveowners.Get(eve.session.charid).name, eve.session.charid)
        except:
            sys.exc_clear()
            return 'inventory.Global instance - failed to __str__ self'



    def ListStations(self, blueprintsOnly = 0, forCorp = 0):
        self._inv5MinCacheContainer__EnterCriticalSection('ListStations')
        try:
            now = blue.os.GetTime()
            if forCorp:
                if util.IsNPC(eve.session.corpid):
                    return []
                else:
                    if blueprintsOnly:
                        if self.cachedStationsBpCorp[0] + MIN * 5 < now:
                            self.cachedStationsBpCorp = (now, self.moniker.ListStations(blueprintsOnly, forCorp))
                        return self.cachedStationsBpCorp[1]
                    if self.cachedStationsCorp[0] + MIN * 5 < now:
                        self.cachedStationsCorp = (now, self.moniker.ListStations(blueprintsOnly, forCorp))
                    return self.cachedStationsCorp[1]
            else:
                if blueprintsOnly:
                    if self.cachedStationsBp[0] + MIN * 5 < now:
                        self.cachedStationsBp = (now, self.moniker.ListStations(blueprintsOnly, forCorp))
                    return self.cachedStationsBp[1]
                else:
                    if self.cachedStations[0] + MIN * 5 < now:
                        self.cachedStations = (now, self.moniker.ListStations(blueprintsOnly, forCorp))
                    return self.cachedStations[1]

        finally:
            self._inv5MinCacheContainer__LeaveCriticalSection('ListStations')




    def ListStationBlueprintItems(self, locationID, stationID, forCorp = 0):
        try:
            self._inv5MinCacheContainer__EnterCriticalSection('ListStationBlueprintItems', locationID)
            now = blue.os.GetTime()
            if forCorp:
                if self.cachedStationBpItemsCorp.has_key(locationID):
                    if self.cachedStationBpItemsCorp[locationID][0] + MIN * 5 < now:
                        del self.cachedStationBpItemsCorp[locationID]
                if not self.cachedStationBpItemsCorp.has_key(locationID):
                    self.cachedStationBpItemsCorp[locationID] = (now, self.moniker.ListStationBlueprintItems(locationID, stationID, forCorp))
                return self.cachedStationBpItemsCorp[locationID][1]
            else:
                if self.cachedStationBpItems.has_key(locationID):
                    if self.cachedStationBpItems[locationID][0] + MIN * 5 < now:
                        del self.cachedStationBpItems[locationID]
                if not self.cachedStationBpItems.has_key(locationID):
                    self.cachedStationBpItems[locationID] = (now, self.moniker.ListStationBlueprintItems(locationID, stationID, forCorp))
                return self.cachedStationBpItems[locationID][1]

        finally:
            self._inv5MinCacheContainer__LeaveCriticalSection('ListStationBlueprintItems', locationID)




    def ListStationItems(self, stationID):
        try:
            self._inv5MinCacheContainer__EnterCriticalSection('ListStationItems', stationID)
            now = blue.os.GetTime()
            if self.cachedStationItems.has_key(stationID):
                if self.cachedStationItems[stationID][0] + MIN * 5 < now:
                    del self.cachedStationItems[stationID]
            if not self.cachedStationItems.has_key(stationID):
                self.cachedStationItems[stationID] = (now, self.moniker.ListStationItems(stationID))
            return self.cachedStationItems[stationID][1]

        finally:
            self._inv5MinCacheContainer__LeaveCriticalSection('ListStationItems', stationID)




    def InvalidateStationItemsCache(self, stationID):
        if self.cachedStationItems.has_key(stationID):
            del self.cachedStationItems[stationID]



    def List(self):
        now = blue.os.GetTime()
        if self.listed is not None:
            if self.listTime + MIN * 5 < now:
                self.listed = None
                self.cachedItems = {}
        if self.listed is None:
            self.listTime = now
            realItems = self.moniker.List()
            for realItem in realItems:
                self.cachedItems[realItem.itemID] = realItem

            self.listed = 1
        return self.cachedItems.values()



    def TrashItem(self, stationID, itemID, locationID):
        if self.cachedStationItems.has_key(stationID):
            for item in self.cachedStationItems[stationID][1]:
                if item.itemID == itemID:
                    item.locationID = locationID
                    break




    def CreateBookmarkVouchers(self, bookmarkIDs, flag, isMove):
        raise UserError('CannotAddToThatLocation')




class invCacheContainer():
    __guid__ = 'invCache.invCacheContainer'
    __update_on_reload__ = 1

    def __init__(self, moniker, key):
        self.key = key
        self.moniker = PasswordHandlerObjectWrapper(moniker)
        self.cachedItems = {}
        self.listed = None
        self.itemID = None
        self.typeID = None
        self.item = None
        self.capacityByFlag = {}
        self.capacityByLocation = None
        self.roleByFlag = {const.flagHangar: const.corpRoleHangarCanQuery1,
         const.flagCorpSAG2: const.corpRoleHangarCanQuery2,
         const.flagCorpSAG3: const.corpRoleHangarCanQuery3,
         const.flagCorpSAG4: const.corpRoleHangarCanQuery4,
         const.flagCorpSAG5: const.corpRoleHangarCanQuery5,
         const.flagCorpSAG6: const.corpRoleHangarCanQuery6,
         const.flagCorpSAG7: const.corpRoleHangarCanQuery7}
        containerIDs = (const.containerHangar,
         const.containerWallet,
         const.containerStationCharacters,
         const.containerOffices,
         const.containerGlobal,
         const.containerSolarSystem,
         const.containerRecycler,
         const.containerCharacter,
         const.containerCorpMarket)
        if key[0] not in containerIDs:
            self.itemID = key[0]



    def __str__(self):
        try:
            return 'invCacheContainer %d for %s' % (self.itemID, self.key)
        except:
            sys.exc_clear()
            return 'invCacheContainer instance - failed to __str__ self'



    def LogInfo(self, *k, **v):
        lg.Info('invCacheContainer', *k, **v)



    def LogWarn(self, *k, **v):
        lg.Warn('invCacheContainer', *k, **v)



    def LogError(self, *k, **v):
        lg.Error('invCacheContainer', *k, **v)



    def MakeDBLessItemReal(self, itemKey, quantity = None, preferMerge = True):
        inv = eve.GetInventoryFromId(itemKey[0])
        useHangar = False
        useCargoBay = False
        if session.stationid:
            if itemKey[0] == self.itemID:
                useCargoBay = True
            else:
                useHangar = True
        elif session.solarsystemid:
            useCargoBay = True
        if useHangar:
            newItemID = inv.RemoveChargeToHangar(itemKey, quantity)
        elif useCargoBay:
            newItemID = inv.RemoveChargeToCargo(itemKey, quantity, preferMerge=preferMerge)
        return newItemID



    def Add(self, itemID, sourceID, **kw):
        self.GetItemID()
        if sm.GetService('corp').IsItemIDLocked(itemID):
            raise UserError('CrpItemIsLocked')
        if itemID == self.itemID:
            raise UserError('CannotPlaceItemInsideItself')
        success = False
        oldItemID = itemID
        sm.GetService('invCache').TryLockItem(itemID, 'lockAddItemToContainer', {'containerType': cfg.invtypes.Get(self.GetTypeID()).typeName}, 1)
        try:
            if type(itemID) is tuple:
                itemID = self.MakeDBLessItemReal(itemID)
                if itemID is None:
                    return 
            success = True

        finally:
            if not success or oldItemID != itemID:
                sm.GetService('invCache').UnlockItem(oldItemID)

        if 'qty' in kw and kw['qty'] == 0:
            self.LogError('Trying to add a stack with 0 quantity to a container. Fix your code.')
            return 
        if oldItemID != itemID:
            sm.GetService('invCache').TryLockItem(itemID, 'lockAddItemToContainer', {'containerType': cfg.invtypes.Get(self.GetTypeID()).typeName}, 1)
        try:
            return self.moniker.Add(itemID, sourceID, **kw)

        finally:
            sm.GetService('invCache').UnlockItem(itemID)




    def MultiAdd(self, itemIDs, sourceID, **kw):
        self.GetItemID()
        lockedItems = set()
        itemIDsToConvert = []
        for itemID in itemIDs:
            if self.itemID is not None and itemID == self.itemID:
                continue
            if sm.GetService('corp').IsItemIDLocked(itemID):
                continue
            if not sm.GetService('invCache').IsItemLocked(itemID):
                if sm.GetService('invCache').TryLockItem(itemID):
                    if type(itemID) is tuple:
                        itemIDsToConvert.append(itemID)
                    lockedItems.add(itemID)

        if not len(lockedItems):
            return 
        preferMerge = self.itemID == session.shipid
        try:
            chargeIDs = set()
            for itemID in itemIDsToConvert:
                chargeID = self.MakeDBLessItemReal(itemID, preferMerge=preferMerge, quantity=kw.get('qty', None))
                sm.GetService('invCache').UnlockItem(itemID)
                lockedItems.remove(itemID)
                sm.GetService('invCache').TryLockItem(chargeID)
                lockedItems.add(chargeID)
                chargeIDs.add(chargeID)

            nonCharges = lockedItems - chargeIDs
            if len(chargeIDs) > 0:
                chargeSourceID = session.shipid
                if session.stationid and itemIDsToConvert[0][0] != self.itemID:
                    chargeSourceID = session.stationid
                self.moniker.MultiAdd(list(chargeIDs), chargeSourceID, **kw)
            if len(nonCharges) > 0:
                self.moniker.MultiAdd(list(nonCharges), sourceID, **kw)

        finally:
            for itemID in lockedItems:
                sm.GetService('invCache').UnlockItem(itemID)





    def CreateBookmarkVouchers(self, bookmarkIDs, flag, isMove):
        self.GetItemID()
        bookmarkIDsToLock = []
        for bookmarkID in bookmarkIDs:
            if self.itemID is not None and bookmarkID == self.itemID:
                continue
            if sm.GetService('corp').IsItemIDLocked(bookmarkID):
                continue
            if not sm.GetService('invCache').IsItemLocked(bookmarkID):
                if sm.GetService('invCache').TryLockItem(bookmarkID):
                    bookmarkIDsToLock.append(bookmarkID)

        if not len(bookmarkIDsToLock):
            return 
        try:
            return self.moniker.CreateBookmarkVouchers(bookmarkIDsToLock, flag, isMove)

        finally:
            for bookmarkID in bookmarkIDsToLock:
                sm.GetService('invCache').UnlockItem(bookmarkID)





    def AddBookmarks(self, bookmarkIDs, flag, isMove):
        bookmarkIDs = bookmarkIDs[:5]
        (bookmarksDeleted, newVouchers,) = self.CreateBookmarkVouchers(bookmarkIDs, flag, isMove)
        if len(newVouchers):
            sm.GetService('voucherCache').OnAdd(newVouchers)
        ids = []
        for bookmark in bookmarksDeleted:
            ids.append(bookmark.bookmarkID)

        if len(ids):
            sm.GetService('addressbook').DeleteBookmarks(ids, alreadyDeleted=1)



    def StackAll(self, *args, **kw):
        self.GetItemID()
        if self.itemID > const.minFakeItem:
            self.LogInfo("StackAll called on a fake location. Why bother.. I won't do it")
            return 
        itemIDsToLock = []
        typeCounts = defaultdict(lambda : 0)
        hasSomethingToStack = False
        for each in self.List(*args, **kw):
            if self.itemID is not None and each.itemID == self.itemID:
                continue
            if each.quantity < 0:
                continue
            if sm.GetService('corp').IsItemLocked(each):
                continue
            if not hasSomethingToStack:
                typeCounts[each.typeID] += 1
                if typeCounts[each.typeID] > 1:
                    hasSomethingToStack = True
            if not sm.GetService('invCache').IsItemLocked(each.itemID):
                if sm.GetService('invCache').TryLockItem(each.itemID):
                    itemIDsToLock.append(each.itemID)

        if not len(itemIDsToLock):
            return 
        try:
            if hasSomethingToStack:
                return self.moniker.StackAll(*args, **kw)

        finally:
            for itemID in itemIDsToLock:
                sm.GetService('invCache').UnlockItem(itemID)





    def MultiMerge(self, ops, sourceContainerID):
        self.GetItemID()
        itemIDsToLock = []
        for (i, (sourceid, destid, qty,),) in enumerate(ops):
            if self.itemID is not None and sourceid == self.itemID:
                continue
            if sm.GetService('corp').IsItemIDLocked(sourceid):
                continue
            if not sm.GetService('invCache').IsItemLocked(sourceid):
                if sm.GetService('invCache').TryLockItem(sourceid):
                    itemIDsToLock.append(sourceid)

        if not len(itemIDsToLock):
            return 
        try:
            for (i, (sourceid, destid, qty,),) in enumerate(ops):
                if type(sourceid) is tuple:
                    args = [sourceid, destid, qty]
                    args[0] = self.MakeDBLessItemReal(args[0])
                    ops[i] = args

            return self.moniker.MultiMerge(ops, sourceContainerID)

        finally:
            for itemID in itemIDsToLock:
                sm.GetService('invCache').UnlockItem(itemID)





    def List(self, *args, **kw):
        flag = None
        if args is not None and len(args):
            flag = args[0]
        if self.listed is None:
            realItems = self.moniker.List()
            for realItem in realItems:
                self.cachedItems[realItem.itemID] = realItem

            godmaSM = sm.GetService('godma').GetStateManager()
            if godmaSM.IsLocationLoaded(self.itemID):
                godmaItem = godmaSM.GetItem(self.itemID)
                if godmaItem is not None:
                    for subloc in godmaItem.sublocations:
                        self.cachedItems[subloc.itemID] = subloc.invItem

            self.listed = 1
        res = dbutil.CRowset(sm.GetService('invCache').GetItemHeader(), [])
        if flag is None:
            if self.key[0] == const.containerHangar:
                flag = const.flagHangar
            elif self.key[0] == const.containerCorpMarket:
                flag = const.flagCorpMarket
        for itemID in self.cachedItems.iterkeys():
            item = self.cachedItems[itemID]
            if flag is not None:
                if item.flagID != flag:
                    continue
            if 'typeID' in kw and item.typeID != kw['typeID']:
                continue
            if len(item) != len(res.header):
                self.LogError('Invalid Item', item)
                continue
            res.append(item)

        return res



    def ListCargo(self):
        return self.List(const.flagCargo)



    def ListDroneBay(self):
        return self.List(const.flagDroneBay)



    def ListHardware(self):
        itemlist = self.List()
        l = []
        for item in itemlist:
            if item.flagID >= const.flagSlotFirst and item.flagID <= const.flagSlotLast:
                l.append(item)

        return l



    def ListHardwareModules(self):
        itemlist = self.List()
        l = []
        for item in itemlist:
            if cfg.IsFittableCategory(item.categoryID) and cfg.IsShipFittingFlag(item.flagID):
                l.append(item)

        return l



    def IsFlagCapacityLocationWide(self, item, flag):
        if item.categoryID == const.categoryShip:
            typeOb = sm.GetService('godma').GetType(item.typeID)
            if typeOb.hasCorporateHangars and self.roleByFlag.has_key(flag):
                return True
        elif item.groupID in (const.groupCorporateHangarArray, const.groupAssemblyArray, const.groupMobileLaboratory):
            return True
        return False



    def GetCapacity(self, flag = None, flags = None):
        self.LogInfo('GetCapacity flag:', flag, 'flags:', flags)
        if self.item is None:
            session.WaitUntilSafe()
            self.item = self.moniker.GetItem()
        if self.item.groupID in (const.groupStation,) or self.item.typeID in (const.typeOffice,):
            capacity = util.Row(['capacity', 'used'], [9000000000000000.0, 0.0])
            return capacity
        listing = None
        if flag is None:
            listing = self.List()
            self.LogInfo('GetCapacity flag None listing:', listing)
            if flags is None:
                flags = []
                for item in listing:
                    if item.flagID is None:
                        continue
                    if item.flagID not in flags:
                        flags.append(item.flagID)

            self.LogInfo('GetCapacity flag None flags:', flags)
            if len(flags):
                capacity = util.Row(['capacity', 'used'], [0, 0.0])
                for flag in flags:
                    cap = self.GetCapacity(flag)
                    if flag is None:
                        continue
                    if capacity.capacity == 0:
                        capacity.capacity = cap.capacity
                    capacity.used += cap.used

                self.LogInfo('GetCapacity returning sum capacity:', capacity)
                return capacity
        flag = flag or const.flagNone
        itemID = self.GetItemID()
        if itemID is not None:
            godmaItem = sm.GetService('godma').GetItem(itemID)
            if godmaItem is not None and godmaItem.statemanager.invByID.has_key(godmaItem.itemID):
                if godmaItem.statemanager.invByID[godmaItem.itemID] != self:
                    self.LogWarn('FIXUP: godma is using an old thrown away invCacheContainer')
                    godmaItem.statemanager.invByID[godmaItem.itemID] = self
                capacity = godmaItem.GetCapacity(flag)
                self.LogInfo('GetCapacity returning godma capacity:', capacity)
                return capacity
        if listing is None:
            listing = self.List()
        typeID = self.GetTypeID()
        capacityAttributeID = None
        if flag == const.flagDroneBay:
            capacityAttributeID = const.attributeDroneCapacity
        elif flag in inventoryFlagsCommon.inventoryFlagData and flag != const.flagCargo:
            capacityAttributeID = inventoryFlagsCommon.inventoryFlagData[flag]['attribute']
        elif self.item.categoryID == const.categoryShip:
            if flag == const.flagShipHangar:
                capacityAttributeID = const.attributeShipMaintenanceBayCapacity
            elif self.roleByFlag.has_key(flag):
                capacityAttributeID = const.attributeCorporateHangarCapacity
        elif flag == const.flagSecondaryStorage:
            capacityAttributeID = const.attributeCapacitySecondary
        elif self.item.groupID == const.groupSilo:
            capacityAttributeID = const.attributeCapacity
        if capacityAttributeID is not None:
            actualCapacity = None
            attribs = [ x for x in cfg.dgmtypeattribs.get(typeID, []) if x.attributeID == capacityAttributeID ]
            if len(attribs):
                actualCapacity = attribs[0].value
            else:
                if self.item.groupID == const.groupSilo and self.item.categoryID == const.categoryStructure:
                    actualCapacity = util.Moniker('posMgr', eve.session.solarsystemid).GetSiloCapacityByItemID(itemID)
                if not actualCapacity:
                    actualCapacity = cfg.dgmattribs.Get(capacityAttributeID).defaultValue
        else:
            actualCapacity = cfg.invtypes.Get(typeID).capacity
        used = 0.0
        isCargoLink = cfg.invtypes.Get(typeID).groupID == const.groupPlanetaryCustomsOffices
        for each in listing:
            if isCargoLink and each.ownerID != session.charid:
                continue
            if each.flagID == flag:
                used = used + cfg.GetItemVolume(each)

        if typeID == const.typePlasticWrap:
            capacity = used
        capacity = util.Row(['capacity', 'used'], [actualCapacity, used])
        self.capacityByLocation = capacity
        self.LogInfo('GetCapacity returning capacity:', capacity)
        return capacity



    def GetItem(self, force = False):
        if self.item is None or force:
            self.item = self.moniker.GetItem()
        return self.item



    def GetItemID(self):
        if self.itemID is not None:
            return self.itemID
        if self.item is None:
            self.item = self.GetItem()
        if self.item is not None:
            self.itemID = self.item.itemID
            self.typeID = self.item.typeID
        return self.itemID



    def GetTypeID(self):
        if self.typeID is not None:
            return self.typeID
        if self.item is None:
            self.item = self.GetItem()
        if self.item is not None:
            self.itemID = self.item.itemID
            self.typeID = self.item.typeID
        return self.typeID



    def OnItemChange(self, item, change):
        oldItem = blue.DBRow(item)
        for (k, v,) in change.iteritems():
            if k in (const.ixStackSize, const.ixSingleton):
                k = const.ixQuantity
            oldItem[k] = v

        location = self.key[0]
        owner = self.key[1]
        if location == const.containerHangar:
            if owner is not None and owner not in [item.ownerID, oldItem.ownerID]:
                return 
            if not eve.session.stationid:
                return 
            if location == const.containerHangar and owner is not None and item.ownerID == owner and const.ixOwnerID in change:
                self.cachedItems[item.itemID] = item
                return 
            if item.locationID != eve.session.stationid or item.stacksize == 0 or item.ownerID != eve.session.charid:
                if self.capacityByFlag.has_key(oldItem.flagID):
                    del self.capacityByFlag[oldItem.flagID]
                elif self.item and self.IsFlagCapacityLocationWide(self.item, oldItem.flagID):
                    self.capacityByLocation = None
                if self.cachedItems.has_key(item.itemID):
                    del self.cachedItems[item.itemID]
                return 
            if item.ownerID == eve.session.charid:
                if self.capacityByFlag.has_key(oldItem.flagID):
                    del self.capacityByFlag[oldItem.flagID]
                elif self.item and self.IsFlagCapacityLocationWide(self.item, oldItem.flagID):
                    self.capacityByLocation = None
                self.cachedItems[item.itemID] = item
        elif location == const.containerCorpMarket:
            if owner is not None and owner not in [item.ownerID, oldItem.ownerID]:
                return 
            if not eve.session.stationid:
                return 
            if item.locationID != eve.session.stationid or item.stacksize == 0 or item.ownerID != eve.session.corpid:
                if self.capacityByFlag.has_key(oldItem.flagID):
                    del self.capacityByFlag[oldItem.flagID]
                elif self.item and self.IsFlagCapacityLocationWide(self.item, oldItem.flagID):
                    self.capacityByLocation = None
                if self.cachedItems.has_key(item.itemID):
                    del self.cachedItems[item.itemID]
                return 
            if item.ownerID == eve.session.corpid:
                if self.capacityByFlag.has_key(oldItem.flagID):
                    del self.capacityByFlag[oldItem.flagID]
                elif self.item and self.IsFlagCapacityLocationWide(self.item, oldItem.flagID):
                    self.capacityByLocation = None
                if oldItem.locationID != eve.session.stationid and item.locationID == eve.session.stationid:
                    if self.cachedItems.has_key(item.itemID):
                        del self.cachedItems[item.itemID]
                    self.cachedItems[item.itemID] = item
                elif self.cachedItems.has_key(item.itemID):
                    del self.cachedItems[item.itemID]
                self.cachedItems[item.itemID] = item
        elif item.locationID != location or item.stacksize == 0:
            if self.cachedItems.has_key(item.itemID):
                del self.cachedItems[item.itemID]
            if self.capacityByFlag.has_key(oldItem.flagID):
                del self.capacityByFlag[oldItem.flagID]
            elif self.item and self.IsFlagCapacityLocationWide(self.item, oldItem.flagID):
                self.capacityByLocation = None
        elif oldItem.locationID != location and item.locationID == location:
            if self.cachedItems.has_key(item.itemID):
                del self.cachedItems[item.itemID]
            self.cachedItems[item.itemID] = item
            if self.capacityByFlag.has_key(item.flagID):
                del self.capacityByFlag[item.flagID]
            elif self.item and self.IsFlagCapacityLocationWide(self.item, item.flagID):
                self.capacityByLocation = None
        elif self.cachedItems.has_key(item.itemID):
            del self.cachedItems[item.itemID]
        self.cachedItems[item.itemID] = item
        if self.capacityByFlag.has_key(item.flagID):
            del self.capacityByFlag[item.flagID]
        elif self.item and self.IsFlagCapacityLocationWide(self.item, item.flagID):
            self.capacityByLocation = None
        if change.has_key(const.ixFlag):
            if self.capacityByFlag.has_key(oldItem.flagID):
                del self.capacityByFlag[oldItem.flagID]
            elif self.item and self.IsFlagCapacityLocationWide(self.item, oldItem.flagID):
                self.capacityByLocation = None



    def __getattr__(self, method):
        if method in self.__dict__:
            return self.__dict__[method]
        if method.startswith('__'):
            raise AttributeError(method)
        if not hasattr(self.moniker, method):
            raise AttributeError(method)
        return FastInvCallWrapper(self.moniker, method)




class PasswordHandlerCallWrapper():

    def __init__(self, object, method):
        self.__method__ = method
        self.__callable__ = object



    def __call__(self, *args, **keywords):
        try:
            try:
                return apply(getattr(self.__callable__, self.__method__), args, keywords)
            except UserError as what:
                if what.args[0] in ('SCGeneralPasswordRequired', 'SCConfigPasswordRequired') and self.__method__ != 'SetPassword':
                    if what.args[0] == 'SCGeneralPasswordRequired':
                        which = const.SCCPasswordTypeGeneral
                        caption = mls.UI_SHARED_ACCESSPASSWORDREQUIRED
                        label = mls.UI_SHARED_PLEASE_ENTER_ACCESSPASSWORD
                    else:
                        which = const.SCCPasswordTypeConfig
                        caption = mls.UI_SHARED_CONFIGURATION_PASSWORD_REQUIRED
                        label = mls.UI_SHARED_PLEASE_ENTER_CONFIGURATIONPASSWORD
                    passw = uix.NamePopup(caption=caption, label=label, setvalue='', icon=-1, modal=1, btns=None, maxLength=16, passwordChar='*')
                    if passw is None:
                        raise 
                    sys.exc_clear()
                    self.__callable__.EnterPassword(which, passw.get('name', ''))
                    return self.__call__(*args, **keywords)
                raise 

        finally:
            self.__dict__.clear()





class PasswordHandlerObjectWrapper():

    def __init__(self, object):
        self._PasswordHandlerObjectWrapper__object = object



    def __getattr__(self, attributeName):
        if attributeName.startswith('__'):
            raise AttributeError(attributeName)
        if not hasattr(self._PasswordHandlerObjectWrapper__object, attributeName):
            raise AttributeError(attributeName)
        return PasswordHandlerCallWrapper(self._PasswordHandlerObjectWrapper__object, attributeName)




class FastInvCallWrapper():

    def __init__(self, object, method):
        self.__method__ = method
        self.__callable__ = object



    def __call__(self, *args, **keywords):
        try:
            return apply(getattr(self.__callable__, self.__method__), args, keywords)

        finally:
            self.__dict__.clear()




