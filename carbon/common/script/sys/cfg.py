import blue
import bluepy
import util
import sys
import types
import copy
import uthread
import log
import service
import macho
import dbutil
import base
import localization
import localizationUtil
globals().update(service.consts)

class DataConfig(service.Service):
    __guid__ = 'svc.dataconfig'
    __startupdependencies__ = []
    __servicename__ = 'dataconfig'
    __displayname__ = 'Data and Configuration Service'
    __exportedcalls__ = {'GetStartupData': [service.ROLE_SERVICE]}
    __notifyevents__ = ['OnCfgDataChanged', 'ProcessInitialData', 'OnConfigRevisionChange']

    def __init__(self):
        service.Service.__init__(self)
        self.cfg = None
        import __builtin__
        __builtin__.DATETIME = const.UE_DATETIME
        __builtin__.DATE = const.UE_DATE
        __builtin__.TIME = const.UE_TIME
        __builtin__.TIMESHRT = const.UE_TIMESHRT
        __builtin__.MSGARGS = const.UE_MSGARGS
        __builtin__.ADD_THE = 22
        __builtin__.ADD_A = 23
        __builtin__.MLS = const.UE_LOC



    def _CreateConfig(self):
        return Config()



    def Run(self, memStream = None):
        service.Service.Run(self, memStream)
        self.state = service.SERVICE_START_PENDING
        import __builtin__
        if not hasattr(__builtin__, 'cfg'):
            __builtin__.cfg = self._CreateConfig()
            cfg.LogError = self.LogError
            cfg.LogInfo = self.LogInfo
            cfg.LogWarn = self.LogWarn
            cfg.LogNotice = self.LogNotice
            cfg.GetStartupData()
        self.state = service.SERVICE_RUNNING



    def Stop(self, memStream = None):
        tmp = cfg
        import __builtin__
        delattr(__builtin__, 'const')
        delattr(__builtin__, 'cfg')
        delattr(__builtin__, 'mls')
        tmp.Release()
        service.Service.Stop(self)



    def ProcessInitialData(self, initdat):
        self.LogInfo('Processing intial data')
        cfg.GotInitData(initdat)
        if boot.role == 'client':
            sm.GetService('bulkSvc').GetUnsubmittedChanges()



    def OnCfgDataChanged(self, what, data):
        uthread.new(cfg.OnCfgDataChanged, what, data)



    def DeleteRowTheHardWay(self, rs, keyIDs, keyCols):
        (keyID, keyID2, keyID3,) = keyIDs
        (keyCol1, keyCol2, keyCol3,) = keyCols
        delRow = None
        if keyCol3:
            for r in rs:
                if r[keyCol1] == keyID and r[keyCol2] == keyID2 and r[keyCol3] == keyID3:
                    delRow = r
                    break

        elif keyCol2:
            for r in rs:
                if r[keyCol1] == keyID and r[keyCol2] == keyID2:
                    delRow = r
                    break

        else:
            for r in rs:
                if r[keyCol1] == keyID:
                    delRow = r
                    break

        if delRow:
            rs.remove(delRow)



    def OnConfigRevisionChange(self, uniqueRefName, cfgEntryName, cacheID, keyIDs, keyCols, oldRow, newRow, source):
        cfgEntry = getattr(cfg, cfgEntryName, None)
        (keyID, keyID2, keyID3,) = keyIDs
        (keyCol1, keyCol2, keyCol3,) = keyCols
        if isinstance(cfgEntry, sys.Recordset):
            if cfgEntry.keycolumn == keyCol1:
                if newRow is None:
                    if keyID in cfgEntry.data:
                        del cfgEntry.data[keyID]
                else:
                    cfgEntry.data[keyID] = newRow
            else:
                if oldRow:
                    specialID = oldRow[cfgEntry.keycolumn]
                    if specialID in cfgEntry.data:
                        del cfgEntry.data[specialID]
                if newRow:
                    specialID = newRow[cfgEntry.keycolumn]
                    cfgEntry.data[specialID] = newRow
        elif isinstance(cfgEntry, dbutil.CFilterRowset):
            if oldRow:
                filterID = oldRow[cfgEntry.columnName]
                if cfgEntry.indexName:
                    if filterID in cfgEntry:
                        indexID = oldRow[cfgEntry.indexName]
                        if indexID in cfgEntry[filterID]:
                            if cfgEntry.allowDuplicateCompoundKeys:
                                rs = cfgEntry[filterID][indexID]
                                if source == 'local':
                                    if oldRow in rs:
                                        rs.remove(oldRow)
                                else:
                                    self.DeleteRowTheHardWay(rs, keyIDs, keyCols)
                                if len(rs) == 0:
                                    del cfgEntry[filterID][indexID]
                            else:
                                del cfgEntry[filterID][indexID]
                            if len(cfgEntry[filterID]) == 0:
                                del cfgEntry[filterID]
                elif filterID in cfgEntry:
                    rs = cfgEntry[filterID]
                    if source == 'local':
                        if oldRow in rs:
                            rs.remove(oldRow)
                    else:
                        self.DeleteRowTheHardWay(rs, keyIDs, keyCols)
                    if len(rs) == 0:
                        del cfgEntry[filterID]
            if newRow:
                filterID = newRow[cfgEntry.columnName]
                if cfgEntry.indexName:
                    indexID = newRow[cfgEntry.indexName]
                    if cfgEntry.allowDuplicateCompoundKeys:
                        if filterID in cfgEntry:
                            if indexID in cfgEntry[filterID]:
                                cfgEntry[filterID][indexID].append(newRow)
                            else:
                                rs = dbutil.CRowset(cfgEntry.header, [newRow])
                                cfgEntry[filterID][indexID] = rs
                        else:
                            rs = dbutil.CRowset(cfgEntry.header, [newRow])
                            cfgEntry[filterID] = {indexID: rs}
                    elif filterID in cfgEntry:
                        cfgEntry[filterID][indexID] = newRow
                    cfgEntry[filterID] = {indexID: newRow}
                elif filterID in cfgEntry:
                    rs = cfgEntry[filterID]
                    rs.append(newRow)
                rs = dbutil.CRowset(cfgEntry.header, [newRow])
                cfgEntry[filterID] = rs
        elif isinstance(cfgEntry, dbutil.CRowset):
            if source == 'remote':
                if oldRow:
                    self.DeleteRowTheHardWay(cfgEntry, keyIDs, keyCols)
                if newRow:
                    cfgEntry.append(newRow)
        if cfgEntryName == 'worldspaces':
            cfg._worldspacesDistrictsCache = {}
        sm.ScatterEvent('OnCfgRevisionChange', uniqueRefName, cfgEntryName, cacheID, keyIDs, keyCols, oldRow, newRow)



    def GetStartupData(self):
        self.LogInfo('Getting startup data')
        cfg.GetStartupData()




class ProxyServiceBroker():

    def ConnectToService(self, name):
        sess = base.GetServiceSession('cfg')
        return sess.ConnectToRemoteService(name)




class Config():
    __guid__ = 'util.config'

    def __init__(self):
        self.servicebroker = None
        self.client = 0
        self.server = 0
        self.totalLogonSteps = 10
        self.bulkIDsToCfgNames = {}
        self.bulkEntries = []
        import __builtin__
        __builtin__.const = const
        self.fmtMapping = {}
        self.fmtMapping[const.UE_DATETIME] = lambda value, value2: util.FmtDate(value)
        self.fmtMapping[const.UE_DATE] = lambda value, value2: util.FmtDate(value, 'ln')
        self.fmtMapping[const.UE_TIME] = lambda value, value2: util.FmtDate(value, 'nl')
        self.fmtMapping[const.UE_TIMESHRT] = lambda value, value2: util.FmtDate(value, 'ns')
        self.fmtMapping[const.UE_MSGARGS] = lambda value, value2: cfg.GetMessage(value[0], value[1]).text
        self.fmtMapping[ADD_A] = lambda value, value2: (value[0] in ('a', 'e', 'i', 'o', 'u', 'A', 'E', 'I', 'O', 'U') and 'an ' or 'a ') + value
        self.fmtMapping[ADD_THE] = lambda value, value2: 'the ' + value
        self.fmtMapping[MLS] = lambda value, value2: self._GetMls(value, value2)
        self.fmtMapping[const.UE_LOC] = lambda value, value2: self._GetLocalization(value, value2)
        self.fmtMapping[const.UE_LIST] = lambda value, value2: self._GetList(value, value2)



    def UpdateCfgData(self, data, object, guid):
        if guid == Recordset.__guid__:
            keyidx = object.keyidx or object.header.index(object.keycolumn)
            object.data[data[keyidx]] = data
        elif guid == dbutil.CFilterRowset.__guid__:
            keyidx = object.columnName
            index = data[keyidx]
            if index in object:
                object[data[keyidx]].append(data)
            else:
                object[data[keyidx]] = [data]
        else:
            raise RuntimeError('Call to OnCfgDataChanged unsupported container type.')



    def OnCfgDataChanged(self, what, data):
        if not hasattr(self, what):
            raise RuntimeError('Call to OnCfgDataChanged with invalid container reference.')
        object = getattr(self, what)
        if not object:
            raise RuntimeError('Call to OnCfgDataChanged failed to get a valid container.')
        if type(object) == types.DictType:
            object[data[0]] = data[1]
            return 
        if not hasattr(object, '__guid__'):
            raise RuntimeError('Call to OnCfgDataChanged for unknown container type.')
        guid = getattr(object, '__guid__')
        if not guid:
            raise RuntimeError('Call to OnCfgDataChanged failed to get container type.')
        self.UpdateCfgData(data, object, guid)
        sm.ScatterEvent('OnPostCfgDataChanged', what, data)



    def Release(self):
        self.messages = None
        self.LogError = None



    def GetConfigSvc(self):
        if not self.servicebroker:
            sess = base.GetServiceSession('cfg')
            if 'config' in sm.services:
                config = sess.ConnectToService('config')
                self.servicebroker = sess
                self.server = 1
            elif boot.role == 'proxy':
                self.servicebroker = ProxyServiceBroker()
                self.client = 1
            else:
                self.servicebroker = sess.ConnectToService('connection')
                if not self.servicebroker.IsConnected():
                    raise RuntimeError('NotConnected')
            self.client = 1
        return self.servicebroker.ConnectToService('config')



    def GetSvc(self, serviceid):
        if not self.servicebroker:
            sess = base.GetServiceSession('cfg')
            self.servicebroker = sess
            self.server = 1
        return self.servicebroker.ConnectToService(serviceid)



    def GetStartupData(self):
        if boot.role != 'server':
            if boot.appname != 'EVE' and boot.role == 'client':
                self.messages = mls.LoadMessages()
            return 
        self.AppGetStartupData()
        if self.IsBulkMgrNode():
            sm.GetService('bulkMgr').DoneInitializingBulk()



    def AppGetStartupData(self):
        pass



    def ReportLoginProgress(self, section, stepNum, totalSteps = None):
        pass



    def ConvertData(self, src, dst):
        dst.data.clear()
        dst.header = src.columns
        keycol = src.columns.index(dst.keycolumn)
        for i in src:
            dst.data[i[keycol]] = i




    def GetRawBulkData(self, bulkID):
        if macho.mode != 'server':
            bulkSvc = sm.GetService('bulkSvc')
            if bulkSvc.BulkExists(bulkID):
                return bulkSvc.LoadBulkFromFile(bulkID)
            else:
                self.LogError('#################################################')
                self.LogError('# Bulk file you are requesting does not exist even though the ')
                self.LogError('# server should have made sure we gotten all the bulk files.')
                self.LogError('# This can for example happen if you are running client against ')
                self.LogError('# an old server that does not know about a newly added bulk file.')
                self.LogError('# bulkID in question:', bulkID)
                self.LogError('#################################################')
                return None
        else:
            cache = sm.GetService('cache')
            return cache.Rowset(bulkID)



    @bluepy.CCP_STATS_ZONE_METHOD
    def GetBulkData(self, bulkID, rowset, rawDataFunction, virtualColumns):
        rawData = rawDataFunction(bulkID)
        if rawData is None:
            return 
        if virtualColumns is not None:
            rawData.header.virtual = virtualColumns
        self.ConvertData(rawData, rowset)
        return rowset



    @bluepy.CCP_STATS_ZONE_METHOD
    def LoadBulk(self, cfgName, bulkID, rowset = None, filterParams = None, tableID = None, rawDataFunctionRef = None, virtualColumns = None):
        if cfgName is not None:
            if bulkID not in self.bulkIDsToCfgNames:
                self.bulkIDsToCfgNames[bulkID] = []
            self.bulkIDsToCfgNames[bulkID].append(cfgName)
        if rawDataFunctionRef is None:
            rawDataFunction = self.GetRawBulkData
        else:
            rawDataFunction = rawDataFunctionRef
        if self.IsBulkMgrNode():
            sm.GetService('bulkMgr').AddToBulk(bulkID, tableID)
        self.bulkEntries.append((bulkID, tableID))
        if rowset is None and filterParams is None:
            rawData = rawDataFunction(bulkID)
            if rawData is None:
                return 
            if virtualColumns is not None:
                rawData.header.virtual = virtualColumns
            return rawData
        if rowset is None:
            rawData = rawDataFunction(bulkID)
            if rawData is None:
                return 
            if virtualColumns is not None:
                rawData.header.virtual = virtualColumns
            if isinstance(filterParams, str):
                rowset = rawData.Filter(filterParams)
            elif len(filterParams) != 3:
                raise RuntimeError('Error loading filtered bulk data', bulkID, 'Filtered list must be of length 3')
            rowset = rawData.Filter(filterParams[0], indexName=filterParams[1], allowDuplicateCompoundKeys=filterParams[2])
        else:
            self.GetBulkData(bulkID, rowset, rawDataFunction, virtualColumns)
        return rowset



    def LoadBulkIndex(self, cfgName, cacheID, column, rowClass = None):
        if rowClass is None:
            rowClass = sys.Row
        return self.LoadBulk(cfgName, cacheID, sys.Recordset(rowClass, column))



    def LoadBulkFilter(self, cfgName, cacheID, filterParams, virtualColumns = None):
        return self.LoadBulk(cfgName, cacheID, None, filterParams, None, None, virtualColumns)



    def IsBulkMgrNode(self):
        if macho.mode != 'server':
            return False
        return sm.GetService('bulkMgr').IsBulkMgrNode()



    @bluepy.CCP_STATS_ZONE_METHOD
    def GotInitData(self, initdata):
        self.LogInfo('GotInitData')
        if macho.mode == 'client':
            sm.GetService('bulkSvc').Connect()
            sm.ScatterEvent('OnProcessLoginProgress', 'loginprogress::miscinitdata', 'messages', 2, self.totalLogonSteps)
        if boot.role == 'client':
            mls.LoadTranslations(session.languageID)
        self.graphics = self.LoadBulkIndex('graphics', const.cacheResGraphics, 'graphicID')
        self.icons = self.LoadBulkIndex('icons', const.cacheResIcons, 'iconID')
        self.sounds = self.LoadBulkIndex('sounds', const.cacheResSounds, 'soundID')
        self.detailMeshes = self.LoadBulkIndex('detailMeshes', const.cacheResDetailMeshes, 'detailGraphicID')
        self.detailMeshesByTarget = self.LoadBulkFilter('detailMeshesByTarget', const.cacheResDetailMeshes, 'targetGraphicID')
        self._worldspacesDistrictsCache = {}
        self.worldspaces = self.LoadBulkIndex('worldspaces', const.cacheWorldSpaces, 'worldSpaceTypeID', sys.Worldspaces)
        self.entitySpawns = self.LoadBulkIndex('entitySpawns', const.cacheEntitySpawns, 'spawnID')
        self.entitySpawnsByWorldSpaceID = self.LoadBulkFilter('entitySpawnsByWorldSpaceID', const.cacheEntitySpawns, 'worldSpaceTypeID')
        self.entitySpawnsByRecipeID = self.LoadBulkFilter('entitySpawnsByRecipeID', const.cacheEntitySpawns, 'recipeID')
        self.entityIngredientInitialValues = self.LoadBulkFilter('entityIngredientInitialValues', const.cacheEntityIngredientInitialValues, 'ingredientID')
        self.entityIngredientsByParentID = self.LoadBulkFilter('entityIngredientsByParentID', const.cacheEntityIngredients, 'parentID')
        self.entityIngredientsByRecipeID = self.LoadBulkFilter('entityIngredientsByRecipeID', const.cacheEntityIngredients, 'recipeID')
        self.ingredients = self.LoadBulkIndex('ingredients', const.cacheEntityIngredients, 'ingredientID')
        self.entitySpawnGroups = self.LoadBulkIndex('entitySpawnGroups', const.cacheEntitySpawnGroups, 'spawnGroupID')
        self.entitySpawnsBySpawnGroup = self.LoadBulkFilter('entitySpawnsBySpawnGroup', const.cacheEntitySpawnGroupLinks, 'spawnGroupID')
        self.recipes = self.LoadBulkIndex('recipes', const.cacheEntityRecipes, 'recipeID')
        self.recipesByParentRecipeID = self.LoadBulkFilter('recipesByParentRecipeID', const.cacheEntityRecipes, 'parentRecipeID')
        self.treeNodes = self.LoadBulkIndex('treeNodes', const.cacheTreeNodes, 'treeNodeID')
        self.treeLinks = self.LoadBulkFilter('treeLinks', const.cacheTreeLinks, 'parentTreeNodeID')
        self.treeNodeProperties = self.LoadBulkIndex('treeNodeProperties', const.cacheTreeProperties, 'propertyID')
        self.actionTreeSteps = self.LoadBulkFilter('actionTreeSteps', const.cacheActionTreeSteps, 'actionID')
        self.actionTreeProcs = self.LoadBulkFilter('actionTreeProcs', const.cacheActionTreeProcs, 'actionID')
        self.actionObjects = self.LoadBulkIndex('actionObjects', const.cacheActionObjects, 'actionObjectID')
        self.actionStations = self.LoadBulkIndex('actionStations', const.cacheActionStations, 'actionStationTypeID')
        self.actionStationActions = self.LoadBulkFilter('actionStationActions', const.cacheActionStationActions, 'actionStationTypeID')
        self.actionObjectStations = self.LoadBulkFilter('actionObjectStations', const.cacheActionObjectStations, 'actionObjectID')
        self.actionObjectExits = self.LoadBulkFilter('actionObjectExits', const.cacheActionObjectExits, ['actionObjectID', 'actionStationInstanceID', True])
        self.paperdollModifierLocations = self.LoadBulkIndex('paperdollModifierLocations', const.cachePaperdollModifierLocations, 'modifierLocationID')
        self.paperdollResources = self.LoadBulkIndex('paperdollResources', const.cachePaperdollResources, 'paperdollResourceID')
        self.paperdollSculptingLocations = self.LoadBulkIndex('paperdollSculptingLocations', const.cachePaperdollSculptingLocations, 'sculptLocationID')
        self.paperdollColors = self.LoadBulkIndex('paperdollColors', const.cachePaperdollColors, 'colorID')
        self.paperdollColorNames = self.LoadBulkIndex('paperdollColorNames', const.cachePaperdollColorNames, 'colorNameID')
        self.paperdollColorRestrictions = self.LoadBulkFilter('paperdollColorRestrictions', const.cachePaperdollColorRestrictions, 'colorNameID')
        self.perceptionSenses = self.LoadBulkIndex('perceptionSenses', const.cachePerceptionSenses, 'senseID')
        self.perceptionStimTypes = self.LoadBulkIndex('perceptionStimTypes', const.cachePerceptionStimTypes, 'stimTypeID')
        self.perceptionSubjects = self.LoadBulkIndex('perceptionSubjects', const.cachePerceptionSubjects, 'subjectID')
        self.perceptionTargets = self.LoadBulkIndex('perceptionTargets', const.cachePerceptionTargets, 'targetID')
        self.perceptionBehaviorSenses = self.LoadBulk('perceptionBehaviorSenses', const.cachePerceptionBehaviorSenses)
        self.perceptionBehaviorDecays = self.LoadBulk('perceptionBehaviorDecays', const.cachePerceptionBehaviorDecays)
        self.perceptionBehaviorFilters = self.LoadBulk('perceptionBehaviorFilters', const.cachePerceptionBehaviorFilters)
        self.encounters = self.LoadBulkIndex('encounters', const.cacheEncounterEncounters, 'encounterID')
        self.encounterCoordinateSets = self.LoadBulkIndex('encounterCoordinateSets', const.cacheEncounterCoordinateSets, 'coordinateSetID')
        self.encounterCoordinatesBySet = self.LoadBulkFilter('encounterCoordinatesBySet', const.cacheEncounterCoordinates, 'coordinateSetID')
        self.encounterCoordinates = self.LoadBulkIndex('encounterCoordinates', const.cacheEncounterCoordinates, 'coordinateID')
        self.encounterCoordinateSetsByWorldSpaceID = self.LoadBulkFilter('encounterCoordinateSetsByWorldSpaceID', const.cacheEncounterCoordinateSets, 'worldSpaceTypeID')
        self.encountersByCoordinateSet = self.LoadBulkFilter('encountersByCoordinateSet', const.cacheEncounterEncounters, 'coordinateSetID')



    def GetMessage(self, key, dict = None, onNotFound = 'return', onDictMissing = 'error'):
        if key not in self.messages:
            if onNotFound == 'return':
                return self.GetMessage('ErrMessageNotFound', {'msgid': key,
                 'args': dict})
            if onNotFound == 'raise':
                raise RuntimeError('ErrMessageNotFound', {'msgid': key,
                 'args': dict})
            elif onNotFound == 'pass':
                return 
            raise RuntimeError('GetMessage: WTF', onNotFound)
        msg = self.messages[key]
        (text, title, suppress,) = (msg.messageText, None, 0)
        if dict == -1:
            pass
        elif dict is not None:
            try:
                if dict is not None and dict != -1:
                    dict = self._Config__prepdict(dict)
                if text is not None:
                    text = text % dict
            except KeyError as e:
                if onNotFound == 'raise':
                    raise 
                sys.exc_clear()
                return self.GetMessage('ErrMessageKeyError', {'msgid': key,
                 'text': msg.messageText,
                 'args': dict,
                 'err': strx(e)})
        elif onDictMissing == 'error':
            if text and text.find('%(') != -1:
                if onNotFound == 'raise':
                    raise RuntimeError('ErrMessageDictMissing', {'msgid': key,
                     'text': msg.messageText})
                return self.GetMessage('ErrMessageDictMissing', {'msgid': key,
                 'text': msg.messageText})
        if text is not None:
            ix = text.find('::')
            if ix != -1:
                (title, text,) = text.split('::')
                suppress = 0
            else:
                ix = text.find(':s:')
                if ix != -1:
                    (title, text,) = text.split(':s:')
                    suppress = 1
        else:
            (text, title, suppress,) = (None, None, 0)
        return util.KeyVal(text=text, title=title, type=msg.messageType, audio=msg.urlAudio, icon=msg.urlIcon, suppress=suppress)



    def _GetMls(self, key, keyArgs = None):
        if boot.role == 'server':
            if keyArgs is None:
                return 'mls.' + key
            else:
                return 'mls.' + key + ' - ' + str(keyArgs)
        else:
            if keyArgs is None:
                return getattr(mls, key)
            else:
                return getattr(mls, key) % keyArgs



    def _GetLocalization(self, key, keyArgs = None):
        if boot.role == 'server':
            if keyArgs is None:
                return key
            else:
                return key + ' - ' + str(keyArgs)
        else:
            if keyArgs is None:
                return localization.GetByLabel(key)
            else:
                return localization.GetByLabel(key, **keyArgs)



    def _GetList(self, fmtList, separator = None):
        results = []
        for each in fmtList:
            value2 = None
            if len(each) >= 3:
                value2 = each[2]
            results.append(self.FormatConvert(each[0], each[1], value2))

        if separator is not None:
            return separator.join(results)
        else:
            return localizationUtil.FormatGenericList(results)



    def __prepdict(self, dict):
        dict = copy.deepcopy(dict)
        for (k, v,) in dict.iteritems():
            if type(v) != types.TupleType:
                continue
            value2 = None
            if len(v) >= 3:
                value2 = v[2]
            dict[k] = self.FormatConvert(v[0], v[1], value2)

        return dict


    __numberstrings__ = {1: 'one',
     2: 'two',
     3: 'three',
     4: 'four',
     5: 'five',
     6: 'six',
     7: 'seven',
     8: 'eight',
     9: 'nine',
     10: 'ten',
     11: 'eleven',
     12: 'twelve',
     13: 'thirteen',
     14: 'fourteen',
     15: 'fifteen',
     16: 'sixteen',
     17: 'seventeen',
     18: 'eighteen',
     19: 'nineteen',
     20: 'twenty',
     30: 'thirty',
     40: 'forty',
     50: 'fifty',
     60: 'sixty',
     70: 'seventy',
     80: 'eighty',
     90: 'ninety'}
    for each in range(19, 0, -1):
        __numberstrings__[each * 100] = __numberstrings__[each] + ' hundred'
        __numberstrings__[each * 1000] = __numberstrings__[each] + ' thousand'
        __numberstrings__[each * 100000] = __numberstrings__[each] + ' hundred thousand'
        __numberstrings__[each * 1000000] = __numberstrings__[each] + ' million'
        __numberstrings__[each * 1000000000] = __numberstrings__[each] + ' billion'


    def FormatConvert(self, formatType, value, value2 = None):
        if type(value) == types.TupleType:
            value2 = None
            if len(value) >= 3:
                value2 = value[2]
            value = self.FormatConvert(value[0], value[1], value2)
        if self.fmtMapping.has_key(formatType):
            return self.fmtMapping[formatType](value, value2)
        else:
            return 'INVALID FORMAT TYPE %s, value is %s' % (formatType, value)



    def Format(self, key, dict = None):
        msg = self.GetMessage(key, dict, onNotFound='raise')
        if msg.title:
            return '%s - %s' % (msg.title, msg.text)
        else:
            return msg.text




class Recordset():
    __guid__ = 'sys.Recordset'

    def __init__(self, rowclass, keycolumn, dbfetcher = None, dbMultiFetcher = None):
        self.rowclass = rowclass
        self.dbfetcher = dbfetcher
        self.dbMultiFetcher = dbMultiFetcher
        self.header = []
        self.data = {}
        self.keyidx = None
        self.keycolumn = keycolumn
        self.locks = {}
        self.waitingKeys = set()
        self.knownLuzers = set([None])
        self.singlePrimeCount = 0
        self.singlePrimeTimestamp = 0



    def GetKeyColumn(self):
        return self.keycolumn



    def GetLine(self, key):
        return self.data[key]



    def __len__(self):
        return len(self.data)



    def __str__(self):
        return self.__repr__()



    def __repr__(self):
        try:
            ret = '<Instance of Recordset.%s>\r\n' % (self.rowclass.__name__,)
            ret = ret + 'Key column: %s' % (self.keycolumn,)
            if len(self.header):
                ret = ret + ', Cache entries: %d\r\n' % (len(self),)
                ret = ret + 'Field names: '
                for i in self.header:
                    ret = ret + i + ', '

                ret = ret[:-2]
            else:
                ret = ret + ', No cache entries.'
            return ret
        except:
            sys.exc_clear()
            return '<Instance of Recordset containing crappy data>'



    def __LoadData(self, key):
        if self.dbfetcher is None:
            return 
        if type(self.dbfetcher) == types.StringType:
            conf = cfg.GetConfigSvc()
            fetch = getattr(conf, self.dbfetcher)
            fk = fetch(key)
            if isinstance(fk, Exception):
                raise fk
            if type(fk) == types.TupleType:
                (self.header, data,) = fk
            elif hasattr(fk, '__columns__'):
                self.header = fk.__columns__
                data = [list(fk)]
            elif hasattr(fk, 'columns'):
                self.header = fk.columns
                data = fk
            else:
                raise RuntimeError('_LoadData called with unsupported data type', fk.__class__)
        elif type(self.dbfetcher) in [types.ListType, types.TupleType]:
            (self.header, data,) = self.dbfetcher
        else:
            fetch = self.dbfetcher
            (self.header, data,) = fetch(key)
        if self.keyidx is None:
            self.keyidx = self.header.index(self.keycolumn)
        ix = self.keyidx
        gotit = 0
        for i in data:
            self.data[i[ix]] = i
            if i[ix] == key:
                gotit = 1
            blue.pyos.BeNice()

        if not gotit:
            self.knownLuzers.add(key)
            log.LogTraceback()



    def Hint(self, key, value):
        if key:
            if len(value) < len(self.header):
                log.LogError('Recordset.Hint is receiving a value that is less than the header length, key=', key, '| classType=', self.rowclass, '| value=', value)
            if len(self.header) == len(value):
                self.data[key] = value
            else:
                self.data[key] = value[:len(self.header)]
        elif hasattr(value, 'columns'):
            ix2 = value.columns.index(self.keycolumn)
            for each in value:
                self.data[each[ix2]] = list(each)

        else:
            raise RuntimeError('Hint called with unsupported data type', value.__class__)



    def Prime(self, keys, fuxorcheck = 1):
        if fuxorcheck:
            i = 0
            for each in keys:
                if each not in self.data:
                    i += 1

            if i >= 50:
                flag = [log.LGINFO, log.LGWARN][(i >= 100)]
                log.general.Log('%s - Prime() called for %s items from %s' % (self.dbMultiFetcher, i, log.WhoCalledMe()), flag)
            if boot.role != 'server' and i == 1:
                NUM_SEC = 2
                s = int(blue.os.GetWallclockTime() / (NUM_SEC * const.SEC))
                if s > self.singlePrimeTimestamp + NUM_SEC:
                    self.singlePrimeCount = 0
                self.singlePrimeTimestamp = s
                self.singlePrimeCount += 1
                if self.singlePrimeCount < 100:
                    tick = 10
                    flag = log.LGWARN
                else:
                    tick = 50
                    flag = log.LGERR
                if self.singlePrimeCount >= tick and self.singlePrimeCount % tick == 0:
                    log.general.Log('%s - Prime() called for %s single items. Last caller was %s. Caller might want to consider using Prime()' % (self.dbMultiFetcher, self.singlePrimeCount, log.WhoCalledMe()), flag)
        if keys:
            self.waitingKeys.update(keys)
            uthread.Lock(self, 0)
            try:
                self._Prime()

            finally:
                uthread.UnLock(self, 0)




    def _Prime(self):
        if self.dbMultiFetcher is None:
            return 
        if not self.waitingKeys:
            return 
        keysToGet = self.waitingKeys
        keysIAlreadyHave = set()
        for key in keysToGet:
            if key in self.data:
                keysIAlreadyHave.add(key)

        keysToGet.difference_update(keysIAlreadyHave)
        keysToGet.difference_update(self.knownLuzers)
        self.waitingKeys = set()
        if len(keysToGet) == 0:
            return 
        conf = cfg.GetConfigSvc()
        fetch = getattr(conf, self.dbMultiFetcher)
        fk = fetch(list(keysToGet))
        if isinstance(fk, Exception):
            raise fk
        if type(fk) == types.TupleType:
            (self.header, data,) = fk
        elif hasattr(fk, '__columns__'):
            self.header = fk.__columns__
            data = [list(fk)]
        elif hasattr(fk, 'columns'):
            self.header = fk.columns
            data = fk
        else:
            raise RuntimeError('_Prime called with unsupported data type', fk.__class__)
        if self.keyidx is None:
            self.keyidx = self.header.index(self.keycolumn)
        ix = self.keyidx
        for i in data:
            self.data[i[ix]] = i
            keysToGet.remove(i[ix])

        for luzer in keysToGet:
            self.knownLuzers.add(luzer)
            log.general.Log('Failed to prime ' + strx(luzer), 1, 1)




    def Get(self, key, flush = 0):
        key = int(key)
        if flush or not self.data.has_key(key):
            if boot.role != 'server':
                self.Prime([key])
            else:
                uthread.Lock(self, key)
                try:
                    if flush or not self.data.has_key(key):
                        self._Recordset__LoadData(key)

                finally:
                    uthread.UnLock(self, key)

        if self.data.has_key(key):
            return self.rowclass(self, key)
        raise KeyError('RecordNotFound', key)



    def GetIfExists(self, key):
        if self.data.has_key(key):
            return self.rowclass(self, key)
        else:
            return None



    def xxx__getitem__(self, index):
        if index > len(self.data):
            raise RuntimeError('RecordNotLoaded')
        return self.rowclass(self, self.data.keys()[index])



    def __getitem__(self, key):
        return self.rowclass(self, key)



    def __iter__(self):

        class RecordsetIterator:

            def next(self):
                return self.rowset.rowclass(self.rowset, self.iter.next())



        it = RecordsetIterator()
        it.rowset = self
        it.iter = self.data.iterkeys()
        return it



    def __contains__(self, key):
        return key in self.data




class Row(util.Row):
    __guid__ = 'sys.Row'
    __persistvars__ = ['header', 'line', 'id']

    def __init__(self, recordset = None, key = None):
        if recordset == None:
            self.__dict__['header'] = None
            self.__dict__['line'] = None
            self.__dict__['id'] = None
        else:
            self.__dict__['header'] = recordset.header
            self.__dict__['line'] = recordset.data[key]
            self.__dict__['id'] = key



    def __setattr__(self, name, value):
        if name in ('id', 'header', 'line'):
            self.__dict__[name] = value
        else:
            raise RuntimeError('ReadOnly', name)



    def __setitem__(self, key, value):
        raise RuntimeError('ReadOnly', key)



    def __str__(self):
        return self.__repr__()



    def __repr__(self):
        try:
            ret = '<Instance of class ' + self.__guid__ + '>\r\n'
            header = self.header
            fields = self.line
            for i in xrange(len(header)):
                ret = ret + '%s:%s%s\r\n' % (header[i], ' ' * (23 - len(header[i])), fields[i])

            return ret
        except:
            sys.exc_clear()
            return '<Instance of Row containing crappy data>'



    def __coerce__(self, object):
        if type(object) == type(0):
            return (self.__dict__['id'], object)



    def __int__(self):
        return self.__dict__['id']




class Worldspaces(Row):
    __guid__ = 'sys.Worldspaces'

    def __getattr__(self, name):
        value = Row.__getattr__(self, name)
        if name == 'districtID' and value is None:
            try:
                return cfg._worldspacesDistrictsCache[Row.__getattr__(self, 'worldSpaceTypeID')]
            except KeyError:
                parentID = Row.__getattr__(self, 'parentWorldSpaceTypeID')
                if parentID is None:
                    districtID = None
                else:
                    districtID = cfg.worldspaces.Get(parentID).districtID
                cfg._worldspacesDistrictsCache[Row.__getattr__(self, 'worldSpaceTypeID')] = districtID
                return districtID
        else:
            return value



    def __str__(self):
        return 'Worldspaces ID: %d, districtID: %d' % (self.worldSpaceTypeID, self.districtID)




