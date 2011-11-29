import blue
import const
import form
import listentry
import localization
import service
import uix
import uiutil
import uthread
import util
import uicls
import uiconst
import weakref
import math
import log

class LPStoreLabel(uicls.EveLabelMedium):
    __guid__ = 'lpstore.LPStoreLabel'
    default_align = uiconst.TOTOP


class LPStoreEntryLabel(uicls.EveLabelMedium):
    __guid__ = 'lpstore.LPStoreEntryLabel'
    default_align = uiconst.CENTERRIGHT
    default_singleline = False


class LPStoreHeaderLabel(uicls.EveLabelSmall):
    __guid__ = 'lpstore.LPStoreHeaderLabel'
    default_align = uiconst.TOTOP


class LPStoreButton(uicls.Container):
    __guid__ = 'lpstore.LPStoreButton'
    default_state = uiconst.UI_PICKCHILDREN
    default_align = uiconst.TOLEFT
    default_name = 'BtnParent'
    default_label = 'unnamed'

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        self.sr.btn = uicls.Button(parent=self, name='btn', align=uiconst.CENTER, label=attributes.get('label', self.default_label))




def GetItemText(typeID, qty, checkIsBlueprint = True):
    isBlueprint = False
    if checkIsBlueprint:
        invtype = cfg.invtypes.Get(typeID)
        invgroup = invtype.Group()
        if invgroup.categoryID == const.categoryBlueprint:
            isBlueprint = True
    if isBlueprint:
        if qty == 1:
            runText = localization.GetByLabel('UI/Agents/Items/BlueprintInfoSingleRun')
        else:
            runText = localization.GetByLabel('UI/Agents/Items/BlueprintInfoMultirun', runsRemaining=qty)
        txt = '%s <br> <b>(%s, %s)</b>' % (cfg.invtypes.Get(typeID).name, runText, localization.GetByLabel('UI/Agents/Items/BlueprintInfoCopy'))
    else:
        txt = localization.GetByLabel('UI/LPStore/RewardItem', quantity=qty, rewardItem=typeID)
    return txt



class LPStoreSvc(service.Service):
    __guid__ = 'svc.lpstore'
    __notifyevents__ = ['OnAccountChange',
     'ProcessSessionChange',
     'OnLPChange',
     'OnUIRefresh']
    __dependencies__ = ['settings']
    settingsVersion = 4

    def Run(self, *etc):
        service.Service.Run(self, *etc)
        self.cache = uiutil.Bunch()
        self.defaultPreset = localization.GetByLabel('UI/LPStore/PresetAffordable')



    def GetCurrentFilters(self):
        return self.currentFilters.copy()



    def GetCurrentPresetLabel(self):
        return self.currentPreset



    def GetMyLPs(self, corpID = None):
        if self.cache.lps is None:
            if corpID is None:
                if self.cache.corpID:
                    corpID = self.cache.corpID
            if not corpID and util.IsNPC(eve.stationItem.ownerID):
                corpID = eve.stationItem.ownerID
            if corpID:
                self.cache.lps = sm.RemoteSvc('LPSvc').GetLPForCharacterCorp(corpID)
            else:
                self.cache.lps = 0
        return self.cache.lps



    def GetMyConcordLPs(self):
        if self.cache.concordLps is None:
            self.cache.concordLps = sm.RemoteSvc('LPSvc').GetLPForCharacterCorp(const.ownerCONCORD)
        return self.cache.concordLps



    def OpenConcordExchange(self, corpID):
        exchangeRate = self.GetConcordLPExchangeRate()
        myConcordLP = self.GetMyConcordLPs()
        corporationLPs = self.GetMyLPs(corpID)
        form.LPExhangeDialog.CloseIfOpen(windowID='LPExhangeDialog_%s' % corpID)
        wnd = form.LPExhangeDialog.Open(windowID='LPExhangeDialog_%s' % corpID, currentFromCorpLPs=myConcordLP, currentToCorpLPs=corporationLPs, exchangeRate=exchangeRate, toCorpID=corpID)



    def GetConcordLPExchangeRate(self, corpID = None):
        if corpID is None:
            if self.cache.corpID:
                corpID = self.cache.corpID
        if not corpID and util.IsNPC(eve.stationItem.ownerID):
            corpID = eve.stationItem.ownerID
        if self.cache.exchangeRates is None:
            self.cache.exchangeRates = sm.RemoteSvc('LPSvc').GetLPExchangeRates()
        if const.ownerCONCORD in self.cache.exchangeRates and corpID in self.cache.exchangeRates[const.ownerCONCORD]:
            return self.cache.exchangeRates[const.ownerCONCORD][corpID]



    def GetOffers(self):
        if self.cache.offers is None:
            self.cache.offers = sm.RemoteSvc('LPSvc').GetAvailableOffersFromCorp(self.cache.corpID, True)
            typeIDs = set()
            for offer in self.cache.offers:
                typeIDs.add(offer.typeID)
                for (typeID, qty,) in offer.reqItems:
                    typeIDs.add(typeID)


            cfg.invtypes.Prime(list(typeIDs))
            self._RefreshOfferSortValues()
        return self.cache.offers



    def ConvertConcordLP(self, corpID, amount):
        sm.RemoteSvc('LPSvc').ExchangeConcordLP(corpID, amount)



    def GetCurrentCorpName(self):
        return cfg.eveowners.Get(self.cache.corpID).name



    def ChangeFilters(self, newFilters):
        self.currentFilters = newFilters
        self.currentPreset = localization.GetByLabel('UI/LPStore/PresetNone')
        self._PersistFilters()
        sm.ScatterEvent('OnLPStoreCurrentPresetChange')
        sm.ScatterEvent('OnLPStoreFilterChange')



    def ChangeCurrentPreset(self, newPreset):
        self.currentPreset = newPreset
        self.currentFilters = self._GetPresetFilters(newPreset)
        self._PersistFilters()
        sm.ScatterEvent('OnLPStoreCurrentPresetChange')
        sm.ScatterEvent('OnLPStoreFilterChange')



    def GetPresets(self):
        ret = self._GetDefaultPresets() + self.userPresets
        if self.currentPreset == localization.GetByLabel('UI/LPStore/PresetNone'):
            ret.insert(0, uiutil.Bunch(label=localization.GetByLabel('UI/LPStore/PresetNone'), filters=None, editable=False))
        return ret



    def AddPreset(self, name, filters):
        self.userPresets.append(uiutil.Bunch(label=name, filters=filters, editable=True))
        self._PersistPresets()
        sm.ScatterEvent('OnLPStorePresetsChange')



    def OverwritePreset(self, label, filters):
        for (i, p,) in enumerate(self.userPresets):
            if p.label == label:
                self.userPresets[i] = uiutil.Bunch(label=label, filters=filters.copy(), editable=True)
                self.ChangeCurrentPreset(label)
                self._PersistPresets()
                return 
        else:
            log.LogError('svc.lpstore.OverwritePreset: Preset not found.')




    def DeletePreset(self, label):
        if label == self.currentPreset:
            self.ChangeCurrentPreset(self.defaultPreset)
        for p in self.userPresets:
            if p.label == label:
                self.userPresets.remove(p)
                self._PersistPresets()
                sm.ScatterEvent('OnLPStorePresetsChange')
                return 
        else:
            log.LogError('svc.lpstore.DeletePreset: Preset not found.')




    def _GetSetting(self, key, default):
        return settings.user.ui.Get('%s_%s' % (key, self.settingsVersion), default)



    def _SetSetting(self, key, value):
        return settings.user.ui.Set('%s_%s' % (key, self.settingsVersion), value)



    def _InitPresets(self):
        if hasattr(self, 'initedPresets'):
            return 
        self.userPresets = [ uiutil.Bunch(**d) for d in self._GetSetting('lpStoreFilterPresets', []) ]
        self.currentPreset = self._GetSetting('lpStoreCurrentPreset', self.defaultPreset)
        if self.currentPreset == localization.GetByLabel('UI/LPStore/PresetNone'):
            self.currentFilters = settings.user.ui.Get('lpStoreCurrentFilters', self._GetPresetFilters(self.defaultPreset))
        else:
            self.currentFilters = self._GetPresetFilters(self.currentPreset)
        self.initedPresets = True



    def _GetPresetFilters(self, label):
        if label == localization.GetByLabel('UI/LPStore/PresetNone'):
            return self.currentFilters
        for preset in self.GetPresets():
            if preset.label == label:
                return preset.filters

        return self._GetPresetFilters(self.defaultPreset)



    def _PersistPresets(self):
        self._SetSetting('lpStoreFilterPresets', [ {'label': preset.label,
         'filters': preset.filters,
         'editable': True} for preset in self.userPresets ])
        self.settings.SaveSettings()



    def _PersistFilters(self):
        self._SetSetting('lpStoreCurrentPreset', self.currentPreset)
        if self.currentPreset == localization.GetByLabel('UI/LPStore/PresetNone'):
            self._SetSetting('lpStoreCurrentFilters', self.currentFilters)
        self.settings.SaveSettings()



    def _GetDefaultPresets(self):
        affordableFilters = {'reqNotInHangar': True,
         'dynamicMaxLP': True,
         'dynamicMaxISK': True}
        return [uiutil.Bunch(label=localization.GetByLabel('UI/LPStore/PresetAffordable'), filters=affordableFilters, editable=False), uiutil.Bunch(label=localization.GetByLabel('UI/LPStore/PresetAll'), filters={}, editable=False)]



    def _RefreshOfferSortValues(self):
        for offer in self.cache.offers:
            self._SetOfferDataSortOrder(offer)




    def AcceptOffer(self, data):
        if getattr(self, 'acceptingOffer', False) == True:
            return 
        try:
            self.acceptingOffer = True
            offer = GetItemText(data.typeID, data.qty).replace('<br>', ' ')
            price = ''
            if data.lpCost > 0:
                price = localization.GetByLabel('UI/LPStore/PriceInLPPoints', lpPrice=util.FmtAmt(data.lpCost)) + '<br>'
            if data.iskCost > 0:
                price += localization.GetByLabel('UI/LPStore/OfferItems', itemText=util.FmtISK(data.iskCost)) + '<br>'
            for item in data.reqItems:
                price += localization.GetByLabel('UI/LPStore/OfferItems', itemText=GetItemText(item[0], item[1])) + '<br>'

            if eve.Message('ConfirmAcceptLPOffer', {'offer': offer,
             'price': price}, uiconst.OKCANCEL, uiconst.ID_OK) != uiconst.ID_OK:
                return 
            ret = sm.RemoteSvc('LPSvc').TakeOffer(self.cache.corpID, data.offerID)
            if ret:
                eve.Message('LPStoreOfferAccepted', {'name': cfg.eveowners.Get(eve.session.charid).name})
            if self.cache.lps:
                del self.cache.lps
            if len(data.reqItems) > 0 and self.cache.hangarInv:
                del self.cache.hangarInv
            self.DirtyWindow()
            sm.ScatterEvent('OnLPStoreAcceptOffer')

        finally:
            self.acceptingOffer = False




    def HaveItem(self, typeID, qty):
        if self.cache.hangarInv is None:
            hi = {}
            inv = sm.GetService('invCache').GetInventory(const.containerHangar).List()
            for item in inv:
                if not item.singleton:
                    hi[item.typeID] = max(hi.get(item.typeID, 0), item.stacksize)

            self.cache.hangarInv = hi
        return self.cache.hangarInv.get(typeID, 0) >= qty



    def HaveLPs(self, lps):
        return self.GetMyLPs() >= lps



    def HaveISK(self, isk):
        return self.GetMyISK() >= isk



    def GetMyISK(self):
        return sm.GetService('wallet').GetWealth()



    def OpenLPStore(self, corpID):
        if self.cache.corpID and corpID != self.cache.corpID:
            if self.cache.lps:
                del self.cache.lps
        self.cache.corpID = corpID
        self._InitPresets()
        self.cache.hangarInv = None
        wnd = form.LPStore.ToggleOpenClose()
        if wnd:
            wnd.RefreshIfNotAlready()



    def OnUIRefresh(self):
        wnd = form.LPStore.GetIfOpen()
        if wnd:
            wnd.Close()
            self.OpenLPStore(self.cache.corpID)



    def DirtyWindow(self):
        if not getattr(self, 'refreshpending', False):
            self.refreshpending = True
            uthread.pool('lpStore::ReportDirtyWindow', self._LPStoreSvc__DirtyWindow)



    def __DirtyWindow(self):
        blue.pyos.synchro.SleepWallclock(1000)
        if self.cache.offers:
            self._RefreshOfferSortValues()
        w = self._GetWnd()
        if w is not None:
            w.Refresh()
        self.refreshpending = False



    def _GetWnd(self):
        return form.LPStore.GetIfOpen()



    def OnAccountChange(self, accountKey, ownerID, balance):
        if accountKey == 'cash' and ownerID == eve.session.charid:
            self.DirtyWindow()



    def ProcessSessionChange(self, isremote, session, change):
        if 'stationid2' in change:
            self.cache.clear()
            w = self._GetWnd()
            if w:
                w.Close()



    def OnLPChange(self, what):
        currentLPs = self.cache.lps
        if self.cache.lps is not None:
            del self.cache.lps
        if self.cache.concordLps is not None:
            del self.cache.concordLps
        self.DirtyWindow()
        if session.stationid2 and currentLPs == 0:
            sm.GetService('station').ReloadLobby()



    def _SetOfferDataSortOrder(self, data):
        lpCost = data.Get('lpCost', 0)
        iskCost = data.Get('iskCost', 0)
        reqItems = data.Get('reqItems', [])

        def ReqItemsSortVal():
            typeNames = [ cfg.invtypes.Get(typeID).name for (typeID, qty,) in reqItems ]
            typeNames.sort()
            return (len(typeNames), tuple(typeNames))



        def CanAccept():
            lpsvc = sm.GetService('lpstore')
            return lpsvc.HaveLPs(lpCost) and lpsvc.HaveISK(iskCost) and not [ 1 for (typeID, qty,) in reqItems if not lpsvc.HaveItem(typeID, qty) ]


        for (label, sortval,) in [(localization.GetByLabel('UI/LPStore/Reward'), cfg.invtypes.Get(data.typeID).name),
         (localization.GetByLabel('UI/LPStore/LPCost'), lpCost),
         (localization.GetByLabel('UI/LPStore/ISKCost'), iskCost),
         (localization.GetByLabel('UI/LPStore/RequiredItems'), ReqItemsSortVal()),
         (localization.GetByLabel('UI/LPStore/Accept'), not CanAccept())]:
            data.Set('sort_%s' % label, sortval)





class LPOfferEntry(uicls.SE_BaseClassCore):
    __guid__ = 'listentry.LPOffer'
    iconSize = 64
    iconMargin = 2
    lineHeight = 1
    labelMargin = 6
    reqItemEntryHeight = 16
    entryHeight = reqItemEntryHeight * 5 + lineHeight

    def ApplyAttributes(self, attributes):
        uicls.SE_BaseClassCore.ApplyAttributes(self, attributes)
        uicls.Line(parent=self, align=uiconst.TOBOTTOM)
        self.sr.rewardParent = uicls.Container(parent=self, name='rewardParent', align=uiconst.TOLEFT, state=uiconst.UI_PICKCHILDREN)
        self.sr.rewardIconParent = uicls.Container(parent=self.sr.rewardParent, name='rewardIconParent', align=uiconst.TOLEFT, width=self.entryHeight)
        self.sr.rewardInfoIcon = uicls.InfoIcon(parent=self.sr.rewardIconParent, align=uiconst.TOPRIGHT, left=10, top=10)
        self.sr.icon = uicls.Icon(parent=self.sr.rewardIconParent, size=self.iconSize, ignoreSize=True, align=uiconst.CENTER, state=uiconst.UI_DISABLED)
        subPar = uicls.Container(parent=self.sr.rewardParent, name='rewardLabelClipper', state=uiconst.UI_DISABLED, align=uiconst.TOALL, clipChildren=True)
        self.sr.rewardLabel = LPStoreEntryLabel(parent=subPar, left=self.labelMargin, align=uiconst.CENTERLEFT)
        subPar = uicls.Container(name='lpCostParent', parent=self, state=uiconst.UI_PICKCHILDREN, align=uiconst.TOLEFT, clipChildren=True)
        self.sr.noLPsIcon = uicls.Icon(name='noLPsIcon', parent=subPar, icon='ui_38_16_194', hint=localization.GetByLabel('UI/LPStore/HintInsufficientLPs'), size=16, left=2, align=uiconst.CENTERLEFT)
        self.sr.lpCostLabel = LPStoreEntryLabel(parent=subPar, name='lpCostLabel', left=self.labelMargin)
        subPar = uicls.Container(name='iskCostParent', parent=self, state=uiconst.UI_PICKCHILDREN, align=uiconst.TOLEFT, clipChildren=True)
        self.sr.noISKIcon = uicls.Icon(name='noISKIcon', parent=subPar, icon='ui_38_16_194', hint=localization.GetByLabel('UI/LPStore/HintInsufficientISK'), size=16, left=2, align=uiconst.CENTERLEFT)
        self.sr.iskCostLabel = LPStoreEntryLabel(parent=subPar, name='iskCostLabel', align=uiconst.CENTERRIGHT, left=self.labelMargin)
        subPar = uicls.Container(name='reqItemsParent', parent=self, state=uiconst.UI_PICKCHILDREN, align=uiconst.TOLEFT, clipChildren=True)
        self.sr.reqItems = uicls.Container(name='reqItems', parent=subPar, align=uiconst.CENTERLEFT)
        subPar = uicls.Container(name='acceptParent', parent=self, state=uiconst.UI_PICKCHILDREN, align=uiconst.TOLEFT, clipChildren=True)
        self.sr.acceptBtn = uicls.Button(name='acceptBtn', parent=subPar, label=localization.GetByLabel('UI/LPStore/Accept'), align=uiconst.CENTER)
        self.sr.cannotAcceptIcon = uicls.Icon(parent=subPar, icon='ui_38_16_194', name='cannotAcceptIcon', size=16, hint=localization.GetByLabel('UI/LPStore/HintCannotAccept'), align=uiconst.CENTER)



    def Startup(self, *etc):
        pass



    def Load(self, data):
        uthread.pool('lpStore::LPOfferEntry.Load_Thread', self.Load_Thread, data)



    def Load_Thread(self, data):
        anyMiss = set()
        lpCost = data.Get('lpCost', 0)
        self.sr.icon.LoadIconByTypeID(typeID=data.typeID, size=64, ignoreSize=True, isCopy=True)
        invtype = cfg.invtypes.Get(data.typeID)
        abstractInfo = None
        if invtype.categoryID == const.categoryBlueprint:
            abstractInfo = util.KeyVal(categoryID=const.categoryBlueprint, runs=data.qty, isCopy=True)
        self.sr.rewardInfoIcon.OnClick = (uix.ShowInfo,
         data.typeID,
         None,
         abstractInfo)
        if lpCost >= 0:
            self.sr.rewardLabel.SetText(GetItemText(data.typeID, data.Get('qty', 1)))
            self.sr.lpCostLabel.SetText(localization.GetByLabel('UI/LPStore/AmountLP', lpAmount=str(util.FmtAmt(lpCost))))
        else:
            self.sr.lpCostLabel.SetText('-')
            self.sr.rewardLabel.SetText(GetItemText(data.typeID, lpCost * -1))
        if sm.GetService('lpstore').HaveLPs(lpCost):
            self.sr.noLPsIcon.state = uiconst.UI_HIDDEN
        else:
            self.sr.noLPsIcon.state = uiconst.UI_NORMAL
            anyMiss.add(True)
        iskCost = data.Get('iskCost', 0)
        self.sr.iskCostLabel.text = util.FmtISK(iskCost)
        if sm.GetService('lpstore').HaveISK(iskCost):
            self.sr.noISKIcon.state = uiconst.UI_HIDDEN
        else:
            self.sr.noISKIcon.state = uiconst.UI_NORMAL
            anyMiss.add(True)
        reqItems = data.Get('reqItems', [])
        self.sr.reqItems.Flush()
        for (idx, (typeID, qty,),) in enumerate(reqItems):
            if idx >= len(self.sr.reqItems.children):
                entry = RequiredItem(parent=self.sr.reqItems, height=self.reqItemEntryHeight)
            else:
                entry = self.sr.reqItems.children[idx]
                entry.state = uiconst.UI_PICKCHILDREN
            entry.sr.infoIcon.OnClick = (uix.ShowInfo, typeID, None)
            entry.sr.label.SetText(GetItemText(typeID, qty, checkIsBlueprint=False))
            if sm.GetService('lpstore').HaveItem(typeID, qty):
                entry.sr.cannotIcon.state = uiconst.UI_HIDDEN
            else:
                entry.sr.cannotIcon.state = uiconst.UI_NORMAL
                anyMiss.add(True)

        for entry in self.sr.reqItems.children[len(reqItems):]:
            entry.state = uiconst.UI_HIDDEN

        self.sr.reqItems.height = self.reqItemEntryHeight * len(reqItems)
        self.sr.acceptBtn.OnClick = lambda *args: sm.GetService('lpstore').AcceptOffer(data)
        if anyMiss:
            alpha = 0.4
            self.sr.acceptBtn.state = uiconst.UI_HIDDEN
            self.sr.cannotAcceptIcon.state = uiconst.UI_NORMAL
        else:
            alpha = 1.0
            self.sr.acceptBtn.state = uiconst.UI_NORMAL
            self.sr.cannotAcceptIcon.state = uiconst.UI_HIDDEN
        self.sr.icon.color.a = self.sr.rewardLabel.color.a = alpha
        self.hint = localization.GetByLabel('UI/LPStore/HintRewardCost', rewardLabel=self.sr.rewardLabel.text, lpCost=localization.GetByLabel('UI/LPStore/LPCost'), lpCostLabel=self.sr.lpCostLabel.text, iskCost=localization.GetByLabel('UI/LPStore/ISKCost'), iskCostLabel=self.sr.iskCostLabel.text)



    def OnColumnResize(self, newCols):
        for (container, width,) in zip(self.children[1:], newCols):
            container.width = width

        self.sr.reqItems.width = self.sr.reqItems.parent.width
        self.sr.rewardLabel.width = self.sr.rewardParent.width - self.sr.rewardIconParent.width - self.sr.rewardLabel.left - self.labelMargin



    def GetHeight(_self, node, width):
        node.height = LPOfferEntry.entryHeight
        return node.height



    def GetColumnWidth(_self, node, column):
        if not hasattr(listentry.LPOffer, 'columnWidths'):
            listentry.LPOffer.columnWidths = {localization.GetByLabel('UI/LPStore/Reward'): 200,
             localization.GetByLabel('UI/LPStore/LPCost'): 80,
             localization.GetByLabel('UI/LPStore/ISKCost'): 115,
             localization.GetByLabel('UI/LPStore/RequiredItems'): 200,
             localization.GetByLabel('UI/LPStore/Accept'): 80}
        return listentry.LPOffer.columnWidths[column]




class RequiredItem(uicls.Container):
    __guid__ = 'lpstore.RequiredItem'
    default_name = 'reqItemEntry'
    default_align = uiconst.TOTOP
    default_height = 16
    default_state = uiconst.UI_PICKCHILDREN

    def ApplyAttributes(self, attributes):
        uicls.Container.ApplyAttributes(self, attributes)
        par = uicls.Container(name='cannotParent', parent=self, state=uiconst.UI_PICKCHILDREN, width=18, align=uiconst.TOLEFT)
        self.sr.cannotIcon = uicls.Icon(icon='ui_38_16_194', parent=par, hint=localization.GetByLabel('UI/LPStore/HintRequiredItemsMissing'), align=uiconst.CENTER, name='cannotIcon')
        par = uicls.Container(name='infoParent', state=uiconst.UI_PICKCHILDREN, parent=self, align=uiconst.TORIGHT, width=18)
        self.sr.infoIcon = uicls.InfoIcon(name='infoIcon', parent=par, align=uiconst.CENTER)
        par = uicls.Container(parent=self, name='labelClipper', clipChildren=True, align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN)
        self.sr.label = LPStoreEntryLabel(parent=par, name='label', singleline=True, align=uiconst.CENTERLEFT)




class LPStoreWindow(uicls.Window):
    __guid__ = 'form.LPStore'
    __notifyevents__ = ['OnLPStoreFilterChange', 'OnLPStoreCurrentPresetChange', 'OnLPStorePresetsChange']
    default_windowID = 'lpstore'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.SetWndIcon('ui_70_64_11', size=128)
        self.SetMainIconSize(64)
        self.SetCaption(localization.GetByLabel('UI/LPStore/WindowTitle'))
        self.SetTopparentHeight(61)
        self.SetMinSize((685, 300))
        self.ConstructHeader()
        self.ConstructContent()



    def OnUIRefresh(self):
        pass



    def ConstructHeader(self):
        self.sr.topParent.state = uiconst.UI_PICKCHILDREN
        top = uicls.Container(parent=self.sr.topParent, name='top', align=uiconst.TOTOP, margin=2, height=36)
        self.sr.corpLabel = uicls.Label(parent=top, name='corpLabel', align=uiconst.TOPRIGHT, fontsize=18, left=10, state=uiconst.UI_NORMAL)
        self.sr.corpLPsLabel = uicls.EveLabelMedium(parent=top, name='corpLPsLabel', align=uiconst.TOPRIGHT, left=10, top=22, state=uiconst.UI_NORMAL)
        xchangeRate = sm.GetService('lpstore').GetConcordLPExchangeRate()
        self.sr.exchangeButton = uicls.Button(parent=self.sr.topParent, name='exchangeBtn', align=uiconst.TOPRIGHT, top=40, left=5, label=localization.GetByLabel('UI/LPStore/ConcordExchange'))
        filterParent = uicls.Container(parent=self.sr.topParent, name='filterParent', pos=(100, 0, 200, 55), align=uiconst.RELATIVE)
        uicls.EveLabelMedium(parent=filterParent, text=localization.GetByLabel('UI/LPStore/OfferFilter'), left=6, top=2, align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL)
        self.sr.presetCombo = uicls.Combo(parent=filterParent, name='presetCombo', left=5, top=16, adjustWidth=True)
        self.sr.filterBtn = uicls.Button(parent=filterParent, name='filterBtn', left=5, top=40, label=localization.GetByLabel('UI/LPStore/EditFilters'))



    def ConstructContent(self):
        main = uicls.Container(parent=self.sr.main, name='margins', align=uiconst.TOALL, margin=4)
        self.sr.lpStoreScroll = uicls.Scroll(parent=main, name='lpStoreScroll', align=uiconst.TOALL)
        self.sr.lpStoreScroll.sr.id = 'blada'



    def RefreshIfNotAlready(self):
        self.sr.filterBtn.OnClick = lambda *blah: self.OpenFilters()
        self.InitOfferRefreshDespammer()
        self.Refresh()
        self.sr.presetCombo.OnChange = self.OnPresetComboChange


    RefreshIfNotAlready = util.RunOnceMethod(RefreshIfNotAlready)

    def Refresh(self):
        self.ShowLoad()
        try:
            self.factionID = sm.GetService('map').GetItem(eve.session.solarsystemid2).factionID
            self.RefreshPresets()
            self.sr.corpLabel.SetText(sm.GetService('lpstore').GetCurrentCorpName())
            self.sr.corpLPsLabel.SetText(localization.GetByLabel('UI/LPStore/CurrentLPs', lpAmount=sm.GetService('lpstore').GetMyLPs()))

        finally:
            self.HideLoad()

        lpSvc = sm.GetService('lpstore')
        exchangeRate = lpSvc.GetConcordLPExchangeRate()
        if exchangeRate is not None and exchangeRate > 0.0 and lpSvc.GetMyConcordLPs() * exchangeRate > 1:
            self.EnableExchangeButton()
        else:
            self.DisableExchangeButton()
        self.RefreshOffers()



    def _OnClose(self, *etc):
        self.ReleaseOfferRefreshDespammer()



    def OpenFilters(self):
        wnd = form.LPStoreFilters.Open()



    def OpenConcordExchange(self):
        self.DisableExchangeButton(suppressHint=True)
        sm.GetService('lpstore').OpenConcordExchange(eve.stationItem.ownerID)



    def DisableExchangeButton(self, suppressHint = False):
        self.sr.exchangeButton.Disable()
        self.sr.exchangeButton.OnClick = None
        lpSvc = sm.GetService('lpstore')
        fromCorpName = cfg.eveowners.Get(const.ownerCONCORD).ownerName
        toCorpName = cfg.eveowners.Get(lpSvc.cache.corpID).ownerName
        if suppressHint:
            self.sr.exchangeButton.SetHint('')
        else:
            exchangeRate = lpSvc.GetConcordLPExchangeRate()
            if exchangeRate is None or exchangeRate == 0.0:
                hint = localization.GetByLabel('UI/LPStore/ExchangeRateNotDefined', fromCorpName=fromCorpName, toCorpName=toCorpName)
            elif fromCorpName == toCorpName:
                hint = localization.GetByLabel('UI/LPStore/ExchangeProhibited', fromCorpName=fromCorpName)
            else:
                hint = localization.GetByLabel('UI/LPStore/ExchangeUnavailable', fromCorpName=fromCorpName, toCorpName=toCorpName)
            self.sr.exchangeButton.SetHint(hint)



    def EnableExchangeButton(self):
        self.sr.exchangeButton.Enable()
        self.sr.exchangeButton.OnClick = lambda *discard: self.OpenConcordExchange()
        fromCorpName = cfg.eveowners.Get(const.ownerCONCORD).ownerName
        toCorpName = cfg.eveowners.Get(sm.GetService('lpstore').cache.corpID).ownerName
        exchangeRate = sm.GetService('lpstore').GetConcordLPExchangeRate()
        self.sr.exchangeButton.SetHint(localization.GetByLabel('UI/LPStore/ConvertLPMsg', toCorpName=toCorpName, exchangeRate=exchangeRate, fromCorpName=fromCorpName))



    def InitOfferRefreshDespammer(self):

        def RefreshOffers():
            columns = [localization.GetByLabel('UI/LPStore/Reward'),
             localization.GetByLabel('UI/LPStore/LPCost'),
             localization.GetByLabel('UI/LPStore/ISKCost'),
             localization.GetByLabel('UI/LPStore/RequiredItems'),
             localization.GetByLabel('UI/LPStore/Accept')]
            self.ShowLoad()
            try:
                filters = sm.GetService('lpstore').GetCurrentFilters()
                scroll = self.sr.lpStoreScroll
                pos = scroll.GetScrollProportion()
                offers = [ listentry.Get('LPOffer', offer) for offer in sm.GetService('lpstore').GetOffers() if self.Check(offer, filters) ]
                self.sr.lpStoreScroll.sr.minColumnWidth = {localization.GetByLabel('UI/LPStore/Reward'): 200,
                 localization.GetByLabel('UI/LPStore/LPCost'): 80,
                 localization.GetByLabel('UI/LPStore/ISKCost'): 115,
                 localization.GetByLabel('UI/LPStore/RequiredItems'): 100,
                 localization.GetByLabel('UI/LPStore/Accept'): 80}
                scroll.LoadContent(headers=columns, contentList=offers, customColumnWidths=True, noContentHint=localization.GetByLabel('UI/LPStore/NoMatchingOffers'))
                columnWidthSettingsVersion = 1
                settingsKey = 'columnWidthsReset_%s' % columnWidthSettingsVersion
                if offers and not settings.user.ui.Get(settingsKey, False):
                    scroll.ResetColumnWidths()
                    settings.user.ui.Set(settingsKey, True)
                scroll.ScrollToProportion(pos)

            finally:
                self.HideLoad()



        self.offerRefreshDespammer = util.Despammer(RefreshOffers, delay=200)
        self.RefreshOffers = self.offerRefreshDespammer.Send



    def ReleaseOfferRefreshDespammer(self):
        uthread.new(self.offerRefreshDespammer.Stop)
        del self.offerRefreshDespammer



    def OnPresetComboChange(self, blah, bleh, label):
        if label == localization.GetByLabel('UI/LPStore/PresetNone'):
            self.OpenFilters()
        else:
            sm.GetService('lpstore').ChangeCurrentPreset(label)



    def OnLPStoreFilterChange(self):
        self.RefreshOffers()



    def OnLPStorePresetsChange(self):
        self.RefreshPresets()



    def OnLPStoreCurrentPresetChange(self):
        self.RefreshPresets()



    def RefreshPresets(self):
        self.ShowLoad()
        try:
            self.sr.presetCombo.LoadOptions([ (preset.label, preset.label) for preset in sm.GetService('lpstore').GetPresets() ], select=sm.GetService('lpstore').GetCurrentPresetLabel())

        finally:
            self.HideLoad()




    def Check(self, offer, filters):
        for (name, val,) in filters.iteritems():
            if not getattr(self, 'Check_%s' % name)(offer, val):
                return False

        return True



    def CategoryFromType(self, typeID):
        return cfg.invtypes.Get(typeID).categoryID



    def GroupFromType(self, typeID):
        return cfg.invtypes.Get(typeID).groupID



    def Check_rewardCategory(self, offer, val):
        return self.CategoryFromType(offer.typeID) == val



    def Check_rewardGroup(self, offer, val):
        return self.GroupFromType(offer.typeID) == val



    def Check_rewardType(self, offer, val):
        return offer.typeID == val



    def Check_reqCategory(self, offer, val):
        for (typeID, qty,) in offer.reqItems:
            if self.CategoryFromType(typeID) == val:
                return True

        return False



    def Check_reqGroup(self, offer, val):
        for (typeID, qty,) in offer.reqItems:
            if self.GroupFromType(typeID) == val:
                return True

        return False



    def Check_reqType(self, offer, val):
        for (typeID, qty,) in offer.reqItems:
            if typeID == val:
                return True

        return False



    def Check_reqIllegal(self, offer, val):
        for (typeID, qty,) in offer.reqItems:
            if self.factionID in cfg.invtypes.Get(typeID).Illegality():
                return False

        return True



    def Check_reqNotInHangar(self, offer, val):
        for (typeID, qty,) in offer.reqItems:
            if not sm.GetService('lpstore').HaveItem(typeID, qty):
                return False

        return True



    def Check_minLP(self, offer, val):
        return offer.lpCost >= val



    def Check_maxLP(self, offer, val):
        return offer.lpCost <= val



    def Check_minISK(self, offer, val):
        return offer.iskCost >= val



    def Check_maxISK(self, offer, val):
        return offer.iskCost <= val



    def Check_dynamicMaxLP(self, offer, val):
        return self.Check_maxLP(offer, sm.GetService('lpstore').GetMyLPs())



    def Check_dynamicMaxISK(self, offer, val):
        return self.Check_maxISK(offer, sm.GetService('lpstore').GetMyISK())




class LPStoreFiltersWindow(uicls.Window):
    __guid__ = 'form.LPStoreFilters'
    __notifyevents__ = ['OnLPStoreCurrentPresetChange', 'OnLPStorePresetsChange']
    comboParentHeight = 40
    editParentHeight = 40
    checkboxParentHeight = 20
    comboSeparatorHeight = 16
    editSeparatorHeight = 18
    labelSeparatorHeight = 2
    labelParentHeight = 15
    scrollSeparatorHeight = 6
    comboWidth = 120
    default_windowID = 'lpfilter'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.SetCaption(localization.GetByLabel('UI/LPStore/Filters'))
        self.SetMinSize([380, 260])
        self.SetTopparentHeight(0)
        self.SetScope('station')
        try:
            self.ConstructContent()
        except Exception as e:
            import log
            log.LogException(e)
            raise 
        self.filters = {}
        self.resetters = []
        self.OnEdited = self.OnEdited_Inactive
        self.HookCombos()
        self.HookEdits()
        self.HookCheckboxes()
        self.MakeButtons()
        self.InitPresetsScroll()
        self.RefreshCurrentPresetLabel()
        self.OnEdited = self.OnEdited_Active
        self.SyncInputs()



    def ConstructContent(self):
        main = uicls.Container(parent=self.sr.main, name='TabPanelGroupParent', align=uiconst.TOALL)
        tabGroup = uicls.TabGroup(parent=main, name='tabs')
        margin = 0
        xmargin = 6
        ymargin = 6
        innermargin = 4
        panelParent = uicls.Container(parent=main, align=uiconst.TOALL, name='panelParent', state=uiconst.UI_PICKCHILDREN, padding=[const.defaultPadding] * 4)
        tabs = []

        def MakeTab(caption):

            def MakeOnTabSelect(panelWr):

                def OnTabSelect(*blah):
                    panel = panelWr()
                    panel.state = uiconst.UI_PICKCHILDREN
                    for sibling in panel.parent.children:
                        if sibling is not panelWr():
                            sibling.state = uiconst.UI_HIDDEN



                return OnTabSelect


            panel = uicls.Container(parent=panelParent, name=caption, align=uiconst.TOALL)
            panel.OnTabSelect = MakeOnTabSelect(weakref.ref(panel))
            tabs.append((caption,
             panel,
             None,
             (caption + '_args',)))
            return panel


        tab = MakeTab(localization.GetByLabel('UI/LPStore/Reward'))
        uicls.Container(parent=tab, name='rewardComboSeparato', height=self.comboSeparatorHeight, align=uiconst.TOTOP, state=uiconst.UI_DISABLED)
        c = uicls.Container(parent=tab, name='rewardCategoryComboParent', height=self.comboParentHeight, align=uiconst.TOTOP, state=uiconst.UI_PICKCHILDREN)
        self.sr.rewardCategoryCombo = uicls.Combo(parent=c, name='rewardCategoryCombo', label=localization.GetByLabel('UI/Common/Category'), width=self.comboWidth, align=uiconst.RELATIVE)
        c = uicls.Container(parent=tab, name='rewardGroupComboParent', height=self.comboParentHeight, align=uiconst.TOTOP)
        self.sr.rewardGroupCombo = uicls.Combo(parent=c, name='rewardGroupCombo', width=self.comboWidth, label=localization.GetByLabel('UI/Common/Group'))
        c = uicls.Container(parent=tab, name='rewardTypeComboParent', height=self.comboParentHeight, align=uiconst.TOTOP)
        self.sr.rewardTypeCombo = uicls.Combo(parent=c, name='rewardTypeCombo', width=self.comboWidth, label=localization.GetByLabel('UI/Common/Type'))
        tab = MakeTab(localization.GetByLabel('UI/LPStore/LPCost'))
        uicls.Container(parent=tab, name='lpCostEditSeparator', height=self.editSeparatorHeight, align=uiconst.TOTOP)
        c = uicls.Container(parent=tab, name='minLPEditParent', height=self.editParentHeight, align=uiconst.TOTOP)
        self.sr.minLPEdit = uicls.SinglelineEdit(parent=c, name='minLPEdit', label=localization.GetByLabel('UI/LPStore/MinLPCost'), ints=[0, None])
        c = uicls.Container(parent=tab, name='maxLPEditParent', height=self.editParentHeight, align=uiconst.TOTOP)
        self.sr.maxLPEdit = uicls.SinglelineEdit(parent=c, name='maxLPEdit', label=localization.GetByLabel('UI/LPStore/MaxLPCost'), ints=[0, None])
        tab = MakeTab(localization.GetByLabel('UI/LPStore/ISKCost'))
        uicls.Container(parent=tab, name='iskCostEditSeparator', height=self.editSeparatorHeight, align=uiconst.TOTOP)
        c = uicls.Container(parent=tab, name='minISKEditParent', height=self.editParentHeight, align=uiconst.TOTOP)
        self.sr.minISKEdit = uicls.SinglelineEdit(parent=c, name='minISKEdit', label=localization.GetByLabel('UI/LPStore/MinISKCost'), ints=[0, None])
        c = uicls.Container(parent=tab, name='maxISKEditParent', height=self.editParentHeight, align=uiconst.TOTOP)
        self.sr.maxISKEdit = uicls.SinglelineEdit(parent=c, name='maxISKEdit', label=localization.GetByLabel('UI/LPStore/MaxISKCost'), ints=[0, None])
        tab = MakeTab(localization.GetByLabel('UI/LPStore/RequiredItems'))
        c = uicls.Container(parent=tab, name='reqItemsHeaderParent', height=18, align=uiconst.TOTOP)
        LPStoreHeaderLabel(parent=c, text=localization.GetByLabel('UI/LPStore/FilterRequiredItemsHeader'))
        c = uicls.Container(parent=tab, name='reqIllegalCbParent', height=self.checkboxParentHeight, align=uiconst.TOTOP)
        self.sr.reqIllegalCb = uicls.Checkbox(parent=c, name='reqIllegalCb', text=localization.GetByLabel('UI/LPStore/FilterRequiredItemsAreIllegal'), align=uiconst.TOTOP)
        c = uicls.Container(parent=tab, name='reqNotInHangarCbParent', height=self.checkboxParentHeight, align=uiconst.TOTOP)
        self.sr.reqNotInHangarCb = uicls.Checkbox(parent=c, name='reqNotInHangarCb', text=localization.GetByLabel('UI/LPStore/FilterRequiredItemsNotInHangar'), align=uiconst.TOTOP)
        uicls.Container(parent=tab, name='reqItemsOrMatchTypeLabelSeparator', height=10, align=uiconst.TOTOP)
        c = uicls.Container(parent=tab, name='reqItemsOrMatchTypeLabelParent', height=16, align=uiconst.TOTOP)
        LPStoreHeaderLabel(parent=c, text=localization.GetByLabel('UI/LPStore/FilterRequiredItemsType'), height=16)
        uicls.Container(parent=tab, name='reqComboSeparator', height=self.comboSeparatorHeight, align=uiconst.TOTOP)
        c = uicls.Container(parent=tab, name='reqCategoryComboParent', height=self.comboParentHeight, align=uiconst.TOTOP)
        self.sr.reqCategoryCombo = uicls.Combo(parent=c, name='reqCategoryCombo', width=self.comboWidth, label=localization.GetByLabel('UI/Common/Category'))
        c = uicls.Container(parent=tab, name='reqGroupComboParent', height=self.comboParentHeight, align=uiconst.TOTOP)
        self.sr.reqGroupCombo = uicls.Combo(parent=c, name='reqGroupCombo', width=self.comboWidth, label=localization.GetByLabel('UI/Common/Group'))
        c = uicls.Container(parent=tab, name='reqTypeComboParent', height=self.comboParentHeight, align=uiconst.TOTOP)
        self.sr.reqTypeCombo = uicls.Combo(parent=c, name='reqTypeCombo', width=self.comboWidth, label=localization.GetByLabel('UI/Common/Type'))
        tab = MakeTab(localization.GetByLabel('UI/LPStore/FilterPresets'))
        c = uicls.Container(parent=tab, name='presetsHeaderSeparator', height=self.labelSeparatorHeight, align=uiconst.TOTOP)
        c = uicls.Container(parent=tab, name='currentPresetHeaderParent', height=12, align=uiconst.TOTOP)
        LPStoreHeaderLabel(name='currentPresetHeader', parent=c, text=localization.GetByLabel('UI/LPStore/ActivePresetName'), height=12)
        c = uicls.Container(parent=tab, name='currentPresetLabelParent', height=12, align=uiconst.TOTOP)
        self.sr.currentPresetLabel = LPStoreLabel(name='currentPresetLabel', parent=c, text=localization.GetByLabel('UI/LPStore/PresetAll'), height=12)
        c = uicls.Container(parent=tab, name='btnsGrandParent', height=15, align=uiconst.TOBOTTOM)
        self.sr.btnsParent = uicls.Container(parent=c, name='btnsParent', height=20, width=200, align=uiconst.CENTER, state=uiconst.UI_PICKCHILDREN)
        uicls.Container(parent=tab, name='presetsScrollSeparator', height=self.scrollSeparatorHeight, align=uiconst.TOTOP)
        uicls.Container(parent=tab, name='presetsScrollSeparator', height=self.scrollSeparatorHeight, align=uiconst.TOBOTTOM)
        self.sr.presetsScroll = uicls.Scroll(name='presetsScroll', parent=tab, align=uiconst.TOALL)
        tabGroup.Startup(tabs)



    def HookCombos(self):
        all = [(localization.GetByLabel('UI/Common/All'), 'all')]

        def GetInvChoices(cfgList, filter = None):
            if filter is None:
                lst = cfgList
            else:
                (attrName, val,) = filter
                lst = [ x for x in cfgList if getattr(x, attrName) == val ]
            ret = [ (x.name, x.id) for x in lst if x.published ]
            ret.sort()
            return ret



        def PropagateComboSelection(combo, val):
            combo.OnChange(None, None, val)



        def MakeOnTypeComboChange(prefix, metaType, cfgList = None, dependant = None):
            filterKey = prefix + metaType.capitalize()
            idKey = metaType + 'ID'

            def OnTypeComboChange(blah, bleh, id):
                if id == 'all':
                    util.TryDel(self.filters, filterKey)
                else:
                    self.filters[filterKey] = id
                if dependant is not None:
                    if id == 'all':
                        dependant.state = uiconst.UI_HIDDEN
                    else:
                        dependant.state = uiconst.UI_NORMAL
                        dependant.LoadOptions(all + GetInvChoices(cfgList, (idKey, id)))
                    PropagateComboSelection(dependant, 'all')
                self.OnEdited()


            return OnTypeComboChange


        typeSuites = ('reward', 'req')
        for typeSuite in typeSuites:
            typeCombo = self.sr.Get('%sTypeCombo' % typeSuite)
            groupCombo = self.sr.Get('%sGroupCombo' % typeSuite)
            categCombo = self.sr.Get('%sCategoryCombo' % typeSuite)
            typeCombo.OnChange = MakeOnTypeComboChange(typeSuite, 'type')
            groupCombo.OnChange = MakeOnTypeComboChange(typeSuite, 'group', cfg.invtypes, typeCombo)
            categCombo.OnChange = MakeOnTypeComboChange(typeSuite, 'category', cfg.invgroups, groupCombo)
            categCombo.LoadOptions(all + GetInvChoices(cfg.invcategories))
            PropagateComboSelection(categCombo, 'all')


        def ResetCombos():
            for typeSuite in typeSuites:
                for metaType in ('Type', 'Group', 'Category'):
                    combo = self.sr.Get('%s%sCombo' % (typeSuite, metaType))
                    setting = self.filters.get(typeSuite + metaType, 'all')
                    combo.SelectItemByValue(setting)
                    PropagateComboSelection(combo, setting)




        self.resetters.append(ResetCombos)



    def HookEdits(self):

        def MakeOnEditChange(key, type_):

            def OnEditChange(s):
                if s and s != '-':
                    self.filters[key] = type_(s)
                else:
                    util.TryDel(self.filters, key)
                self.OnEdited()


            return OnEditChange


        keysTypes = [('minLP', int),
         ('maxLP', int),
         ('minISK', int),
         ('maxISK', int)]
        for (key, type_,) in keysTypes:
            self.sr.Get(key + 'Edit').OnChange = MakeOnEditChange(key, type_)


        def ResetEdits():
            for (key, type_,) in keysTypes:
                edit = self.sr.Get(key + 'Edit')
                if key in self.filters:
                    edit.SetValue(self.filters[key])
                else:
                    edit.SetText('', format=False)



        self.resetters.append(ResetEdits)



    def HookCheckboxes(self):

        def MakeOnCheckboxChange(key):

            def OnCheckboxChange(cb):
                if cb.checked:
                    self.filters[key] = True
                else:
                    util.TryDel(self.filters, key)
                self.OnEdited()


            return OnCheckboxChange


        keys = ('reqIllegal', 'reqNotInHangar')
        for key in keys:
            self.sr.Get(key + 'Cb').OnChange = MakeOnCheckboxChange(key)


        def ResetCheckboxes():
            for key in keys:
                self.sr.Get(key + 'Cb').SetChecked(self.filters.get(key, False))



        self.resetters.append(ResetCheckboxes)



    def MakeButtons(self):
        buttonSeparation = 0
        for (btnID, labelString, OnClick, hint,) in [('new',
          localization.GetByLabel('UI/Common/Buttons/New'),
          self.OnClickNew,
          localization.GetByLabel('UI/LPStore/HintNewPreset')),
         ('load',
          localization.GetByLabel('UI/Common/Buttons/Load'),
          self.OnClickLoad,
          localization.GetByLabel('UI/LPStore/HintLoadPreset')),
         ('overwrite',
          localization.GetByLabel('UI/Common/Buttons/Overwrite'),
          self.OnClickOverwrite,
          localization.GetByLabel('UI/LPStore/HintOverwritePreset')),
         ('del',
          localization.GetByLabel('UI/Common/Buttons/Delete'),
          self.OnClickDelete,
          localization.GetByLabel('UI/LPStore/HintDeletePreset'))]:
            parent = LPStoreButton(parent=self.sr.btnsParent, name='%sbtnParent' % btnID, label=labelString, hint=localization.GetByLabel('UI/LPStore/HintDeletePreset'))
            btn = parent.sr.btn
            setattr(self.sr, '%sBtn' % btnID, btn)
            btn.sr.hint = hint
            btn.OnClick = OnClick

        maxw = max([ par.sr.btn.width for par in self.sr.btnsParent.children ])
        for par in self.sr.btnsParent.children:
            par.sr.btn.width = maxw
            par.width = maxw + buttonSeparation

        self.sr.btnsParent.width = sum([ child.width for child in self.sr.btnsParent.children ])
        self.RefreshVisibleButtons()



    def InitPresetsScroll(self):
        self.sr.presetsScroll.multiSelect = False
        self.sr.presetsScroll.OnSelectionChange = self.OnPresetsScrollSelectionChange
        self.RefreshPresetsScroll()



    def OnLPStorePresetsChange(self):
        self.RefreshPresetsScroll()



    def RefreshPresetsScroll(self):
        self.sr.presetsScroll.Load(contentList=[ listentry.Get('Generic', data=preset) for preset in sm.GetService('lpstore').GetPresets() if preset.label != localization.GetByLabel('UI/LPStore/PresetNone') ])



    def OnPresetsScrollSelectionChange(self, *etc):
        self.RefreshVisibleButtons()



    def RefreshVisibleButtons(self):
        sel = self.sr.presetsScroll.GetSelected()
        if not sel:
            self.sr.loadBtn.state = uiconst.UI_HIDDEN
            self.sr.overwriteBtn.state = uiconst.UI_HIDDEN
            self.sr.delBtn.state = uiconst.UI_HIDDEN
        elif not sel[0].editable:
            self.sr.loadBtn.state = uiconst.UI_NORMAL
            self.sr.overwriteBtn.state = uiconst.UI_HIDDEN
            self.sr.delBtn.state = uiconst.UI_HIDDEN
        else:
            self.sr.loadBtn.state = uiconst.UI_NORMAL
            self.sr.overwriteBtn.state = uiconst.UI_NORMAL
            self.sr.delBtn.state = uiconst.UI_NORMAL



    def OnClickNew(self, *blah):

        def Validate(data):
            name = data['name']
            if not name:
                return localization.GetByLabel('UI/LPStore/ErrorNoName', cancelLabel=localization.GetByLabel('UI/Common/Buttons/Cancel'))
            if name in [ preset.label for preset in sm.GetService('lpstore').GetPresets() ]:
                return localization.GetByLabel('UI/LPStore/ErrorExstingName', overwriteLabel=localization.GetByLabel('UI/Common/Buttons/Overwrite'))


        result = uix.NamePopup(maxLength=50, validator=Validate)
        if result:
            sm.GetService('lpstore').AddPreset(result['name'], self.filters.copy())



    def SelectedPreset(self):
        return self.sr.presetsScroll.GetSelected()[0]



    def OnClickLoad(self, *blah):
        self.LoadPreset(self.SelectedPreset())



    def LoadPreset(self, preset):
        sm.GetService('lpstore').ChangeCurrentPreset(preset.label)



    def OnLPStoreCurrentPresetChange(self):
        self.RefreshCurrentPresetLabel()
        if sm.GetService('lpstore').GetCurrentPresetLabel() != localization.GetByLabel('UI/LPStore/PresetNone'):
            self.SyncInputs()



    def SyncInputs(self):
        self.OnEdited = self.OnEdited_Inactive
        try:
            self.filters = sm.GetService('lpstore').GetCurrentFilters()
            for Reset in self.resetters:
                Reset()


        finally:
            self.OnEdited = self.OnEdited_Active




    def RefreshCurrentPresetLabel(self):
        self.sr.currentPresetLabel.text = sm.GetService('lpstore').GetCurrentPresetLabel()



    def OnClickOverwrite(self, *blah):
        self.OverwritePreset(self.SelectedPreset())



    def OverwritePreset(self, preset):
        if eve.Message('ConfirmOverwriteLPStoreFilterPreset', {}, uiconst.OKCANCEL, uiconst.ID_OK) == uiconst.ID_OK:
            sm.GetService('lpstore').OverwritePreset(preset.label, self.filters)



    def OnClickDelete(self, *blah):
        self.DeletePreset(self.SelectedPreset())
        self.RefreshVisibleButtons()



    def DeletePreset(self, preset):
        if eve.Message('ConfirmDeleteLPStoreFilterPreset', {}, uiconst.OKCANCEL, uiconst.ID_OK) == uiconst.ID_OK:
            sm.GetService('lpstore').DeletePreset(preset.label)
            self.RefreshPresetsScroll()



    def OnEdited_Active(self):
        sm.GetService('lpstore').ChangeFilters(self.filters)



    def OnEdited_Inactive(self):
        pass




class LPExhangeDialog(uicls.Window):
    __guid__ = 'form.LPExhangeDialog'
    __notifyevents__ = ['OnLPStoreFilterChange', 'OnLPStoreCurrentPresetChange', 'OnLPStorePresetsChange']

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.scope = 'station'
        self.SetWndIcon(None)
        self.SetTopparentHeight(0)
        self.SetSize(300, 225)
        self.MakeUnResizeable()
        self.MakeUnMinimizable()
        self.MakeUncollapseable()
        self.MakeUnpinable()
        self.toCorpID = attributes.Get('toCorpID')
        self.toCorpName = cfg.eveowners.Get(self.toCorpID).ownerName
        self.fromCorpName = cfg.eveowners.Get(attributes.get('fromCorpID', const.ownerCONCORD)).ownerName
        self.currentFromCorpLPs = attributes.get('currentFromCorpLPs')
        self.currentToCorpLPs = attributes.get('currentToCorpLPs')
        self.exchangeRate = attributes.get('exchangeRate')
        self.maxCorporationLPs = int(self.currentFromCorpLPs * self.exchangeRate)
        self.SetCaption(localization.GetByLabel('UI/LPStore/LPExchangeDialogTitle'))
        maxLPs = attributes.get('maxLPs', None)
        btns = [[localization.GetByLabel('UI/Common/Buttons/OK'),
          self.OnOK,
          (),
          81], [localization.GetByLabel('UI/Common/Buttons/Cancel'),
          self.OnCancel,
          (),
          81]]
        self.buttons = uicls.ButtonGroup(btns=btns, parent=self.sr.main)
        topCont = uicls.Container(name='topCont', parent=self.sr.main, align=uiconst.TOALL, padding=(4, 4, 4, 4))
        LPStoreLabel(parent=topCont, singleline=False, text=localization.GetByLabel('UI/LPStore/ConvertLPMsg', toCorpName=self.toCorpName, exchangeRate=self.exchangeRate, fromCorpName=self.fromCorpName))
        LPStoreLabel(parent=topCont, text=self.toCorpName, uppercase=True, fontsize=13, bold=True, top=10)
        cont = uicls.Container(name='toCorpLPAmountContainer', parent=topCont, align=uiconst.TOTOP, pos=(0, 0, 100, 18), state=uiconst.UI_PICKCHILDREN)
        label = LPStoreEntryLabel(parent=cont, text=localization.GetByLabel('UI/LPStore/ExchangePurchaseAmount'), align=uiconst.CENTERLEFT)
        label = LPStoreEntryLabel(parent=cont, text=localization.GetByLabel('UI/LPStore/LP'), align=uiconst.TORIGHT)
        self.amountEdit = uicls.SinglelineEdit(name='lpAmountEdit', parent=cont, pos=(17, 0, 80, 0), ints=(1, self.maxCorporationLPs), align=uiconst.TOPRIGHT, setvalue=self.maxCorporationLPs, state=uiconst.UI_NORMAL)
        self.amountEdit.OnChange = self.OnChangeEdit
        zeroLP = 0.0
        cont = uicls.Container(name='toCorpCurrentLPContainer', parent=topCont, align=uiconst.TOTOP, height=18)
        label = LPStoreEntryLabel(parent=cont, text=localization.GetByLabel('UI/Common/Current'), align=uiconst.CENTERLEFT)
        self.toCorpCurrentLP = LPStoreEntryLabel(parent=cont, text=localization.GetByLabel('UI/LPStore/AmountLP', lpAmount=str(util.FmtAmt(zeroLP))), align=uiconst.CENTERRIGHT)
        cont = uicls.Container(name='toCorpTotalLPContainer', parent=topCont, align=uiconst.TOTOP, height=18)
        label = LPStoreEntryLabel(parent=cont, text=localization.GetByLabel('UI/Common/Total'), align=uiconst.CENTERLEFT)
        self.toCorpTotalLP = LPStoreEntryLabel(parent=cont, text=localization.GetByLabel('UI/LPStore/AmountLP', lpAmount=str(util.FmtAmt(zeroLP))), align=uiconst.CENTERRIGHT)
        LPStoreLabel(parent=topCont, text=self.fromCorpName, uppercase=True, fontsize=13, bold=True)
        cont = uicls.Container(name='fromCorpCostLPContainer', parent=topCont, align=uiconst.TOTOP, height=18)
        label = LPStoreEntryLabel(parent=cont, text=localization.GetByLabel('UI/Common/Cost'), align=uiconst.CENTERLEFT)
        self.fromCorpCostLP = LPStoreEntryLabel(parent=cont, text=localization.GetByLabel('UI/LPStore/AmountLP', lpAmount=str(util.FmtAmt(zeroLP))), align=uiconst.CENTERRIGHT)
        cont = uicls.Container(name='fromCorpFinalLPContainer', parent=topCont, align=uiconst.TOTOP, height=18)
        label = LPStoreEntryLabel(parent=cont, text=localization.GetByLabel('UI/Common/Remaining'), align=uiconst.CENTERLEFT)
        self.fromCorpFinalLP = LPStoreEntryLabel(parent=cont, text=localization.GetByLabel('UI/LPStore/AmountLP', lpAmount=str(util.FmtAmt(zeroLP))), align=uiconst.CENTERRIGHT)
        self.SetDetails(1)



    def SetDetails(self, lpToExchange):
        concordLPCost = int(math.ceil(lpToExchange / self.exchangeRate))
        concordLPAfter = self.currentFromCorpLPs - concordLPCost
        corporationLPAfter = self.currentToCorpLPs + lpToExchange
        self.fromCorpCostLP.SetText(localization.GetByLabel('UI/LPStore/AmountLP', lpAmount=str(util.FmtAmt(concordLPCost))))
        self.fromCorpFinalLP.SetText(localization.GetByLabel('UI/LPStore/AmountLP', lpAmount=str(util.FmtAmt(concordLPAfter))))
        self.toCorpTotalLP.SetText(localization.GetByLabel('UI/LPStore/AmountLP', lpAmount=str(util.FmtAmt(corporationLPAfter))))
        self.toCorpCurrentLP.SetText(localization.GetByLabel('UI/LPStore/AmountLP', lpAmount=str(util.FmtAmt(self.currentToCorpLPs))))
        self.amountEdit.SetValue(lpToExchange, docallback=False)



    def OnChangeEdit(self, number):
        number = self.amountEdit.CheckBounds(number, warnsnd=True, allowEmpty=True)
        self.SetDetails(int(number or 1))



    def OnOK(self):
        try:
            sm.GetService('lpstore').ConvertConcordLP(self.toCorpID, int(self.amountEdit.text))

        finally:
            self.EnableButton()
            self.Close()




    def _OnClose(self, *args):
        self.EnableButton()



    def OnCancel(self):
        self.Close()



    def EnableButton(self):
        wnd = form.LPStore.GetIfOpen()
        if wnd:
            wnd.Refresh()




