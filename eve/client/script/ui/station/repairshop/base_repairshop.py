import const
import listentry
import math
import service
import uix
import uiutil
import uthread
import util
import uicls
import uiconst
import localization

class RepairShopWindow(uicls.Window):
    __guid__ = 'form.RepairShopWindow'
    default_width = 400
    default_height = 300
    default_windowID = 'repairshop'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self.invCookie = None
        self.invReady = 0
        self.optionsByItemType = {}
        self.itemToRepairDescription = ''
        self.repairSvc = util.Moniker('repairSvc', session.stationid2)
        self.invCache = sm.GetService('invCache')
        self.SetCaption(localization.GetByLabel('UI/Station/Repair/RepairShopHeader'))
        self.SetMinSize([350, 270])
        self.SetWndIcon('ui_18_128_4', mainTop=-8)
        uicls.WndCaptionLabel(text=localization.GetByLabel('UI/Station/Repair/RepairFacilities'), parent=self.sr.topParent, align=uiconst.RELATIVE)
        self.scope = 'station'
        btns = uicls.ButtonGroup(btns=[(localization.GetByLabel('UI/Commands/PickNewItem'),
          self.DisplayItems,
          (),
          84), (localization.GetByLabel('UI/Commands/RepairItem'),
          self.QuoteItems,
          (),
          84), (localization.GetByLabel('UI/Commands/RepairAll'),
          self.DoNothing,
          (),
          84)], line=1)
        self.sr.main.children.append(btns)
        self.sr.pickSelect = btns
        self.sr.pickBtn = self.sr.pickSelect.GetBtnByLabel(localization.GetByLabel('UI/Commands/PickNewItem'))
        self.sr.selBtn = self.sr.pickSelect.GetBtnByLabel(localization.GetByLabel('UI/Commands/RepairItem'))
        self.sr.repairAllBtn = self.sr.pickSelect.GetBtnByLabel(localization.GetByLabel('UI/Commands/RepairAll'))
        cont = uicls.Container(name='scroll', align=uiconst.TORIGHT, parent=self.sr.topParent, left=const.defaultPadding, top=const.defaultPadding, width=200)
        self.sr.scroll = uicls.Scroll(parent=self.sr.main, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        self.sr.scroll.sr.minColumnWidth = {localization.GetByLabel('UI/Common/Type'): 30}
        self.sr.avgDamage = uicls.EveLabelSmall(text='', parent=cont, name='avgDamage', left=8, top=0, state=uiconst.UI_NORMAL, align=uiconst.BOTTOMRIGHT)
        self.sr.totalCost = uicls.EveLabelSmall(text='', parent=cont, name='totalCost', left=8, top=12, state=uiconst.UI_NORMAL, align=uiconst.BOTTOMRIGHT)
        self.Register()
        uthread.new(self.DisplayItems)



    def Register(self):
        self.invReady = 1
        self.invCookie = sm.GetService('inv').Register(self)



    def DisplayItems(self, *args):
        self.itemToRepairDescription = ''
        self.HideButtons()
        btnSetup = {self.sr.pickBtn: uiconst.UI_HIDDEN,
         self.sr.selBtn: uiconst.UI_NORMAL,
         self.sr.repairAllBtn: uiconst.UI_HIDDEN}
        self.SetHint()
        self.sr.avgDamage.text = ''
        self.sr.totalCost.text = ''
        try:
            hangarInv = sm.GetService('invCache').GetInventory(const.containerHangar)
            items = hangarInv.List()
            tmplst = []
            for item in items:
                if util.IsItemOfRepairableType(item):
                    if item.categoryID == const.categoryShip:
                        tmplst.append((cfg.evelocations.Get(item.itemID).name, item))
                    else:
                        tmplst.append((cfg.invtypes.Get(item.typeID).name, item))

            if len(tmplst) == 0:
                self.SetHint(localization.GetByLabel('UI/Station/Repair/NothingToRepair', repairShop=localization.GetByLabel('UI/Station/Repair/RepairFacilities')))
            else:
                scrolllist = []
                currIndex = 1
                for (label, item,) in tmplst:
                    scrolllist.append(listentry.Get('Item', {'info': item,
                     'itemID': item.itemID,
                     'typeID': item.typeID,
                     'label': label,
                     'getIcon': 1,
                     'GetMenu': self.GetItemInHangarMenu,
                     'OnDblClick': self.OnDblClick,
                     'name': 'repairEntry%s' % currIndex}))

                currIndex += 1
                self.sr.scroll.sr.id = None
                self.sr.scroll.sr.ignoreTabTrimming = 1
                self.state = uiconst.UI_NORMAL
                self.sr.scroll.Load(contentList=scrolllist, headers=[localization.GetByLabel('UI/Common/Type')])

        finally:
            self.state = uiconst.UI_NORMAL

        self.DisplayButtons(btnSetup)



    def GetSelected(self):
        return [ node.info for node in self.sr.scroll.GetSelected() ]



    def GetAll(self):
        return [ node.info for node in self.sr.scroll.GetNodes() ]



    def QuoteItems(self, *args):
        self.DisplayRepairQuote(self.GetSelected())



    def SetHint(self, hintstr = None):
        if self.sr.scroll:
            self.sr.scroll.ShowHint(hintstr)



    def DoNothing(self, *args):
        pass



    def GetItemInHangarMenu(self, entry):
        item = entry.sr.node.info
        items = self.GetSelected()
        if item not in items:
            items.append(item)
        m = sm.GetService('menu').GetMenuFormItemIDTypeID(item.itemID, item.typeID)
        m += [(localization.GetByLabel('UI/Inventory/ItemActions/GetRepairQuote'), self.DisplayRepairQuote, (items,))]
        return m



    def OnDblClick(self, *args):
        self.DisplayRepairQuote(self.GetSelected())



    def GetItemMenu(self, entry):
        info = entry.sr.node.info
        m = sm.GetService('menu').GetMenuFormItemIDTypeID(info.itemID, info.typeID)
        items = self.GetSelected()
        if info not in items:
            items.append(info)
        if info.damage > 0.0:
            m += [(localization.GetByLabel('UI/Commands/Repair'), self.Repair, (items,))]
        if eve.session.role & service.ROLE_WORLDMOD:
            m += [(localization.GetByLabel('UI/Commands/Damage'), self.Damage, (items,))]
        return m



    def OnItemDblClick(self, entry):
        info = entry.sr.node.info
        items = self.GetSelected()
        if info not in items:
            items.append(info)
        if info.damage > 0.0:
            uthread.new(self.Repair, items)
        elif eve.session.role & service.ROLE_WORLDMOD:
            uthread.new(self.Damage, items)



    def DisplayRepairQuote(self, items, *args):
        if not len(items):
            return 
        self.itemToRepairDescription = ''
        self.HideButtons()
        btnSetup = {self.sr.pickBtn: uiconst.UI_HIDDEN,
         self.sr.selBtn: uiconst.UI_HIDDEN}
        self.SetHint()
        totalitems = 0
        totaldamage = 0.0
        totalcost = 0
        self.itemToRepairDescription = ''
        scrolllist = []
        listEntryData = []
        damageReports = {}
        itemIDs = []
        for item in items:
            itemIDs.append(item.itemID)

        if len(itemIDs):
            damageReports = self.repairSvc.GetDamageReports(itemIDs)
        currIndex = 1
        for item in items:
            for each in damageReports[item.itemID].quote:
                if each.itemID in [ entryData['itemID'] for entryData in listEntryData ]:
                    continue
                damage = math.ceil(each.damage)
                dmg = localization.GetByLabel('UI/Station/Repair/CurrentDamage', curHealth=max(0, int(each.maxHealth - damage)), maxHealth=each.maxHealth, percentHealth=damage / float(each.maxHealth or 1) * 100.0)
                cst = localization.GetByLabel('UI/Station/Repair/RepairCostNumberOnly', isk=int(math.ceil(damage * each.costToRepairOneUnitOfDamage)))
                totalitems = totalitems + 1
                totaldamage = totaldamage + damage / float(each.maxHealth or 1) * 100.0
                totalcost = totalcost + damage * each.costToRepairOneUnitOfDamage
                label = cfg.invtypes.Get(each.typeID).name + '<t>' + dmg + '<t>' + cst
                listEntryData.append({'info': each,
                 'itemID': each.itemID,
                 'typeID': each.typeID,
                 'label': label,
                 'getIcon': 1,
                 'GetMenu': self.GetItemMenu,
                 'OnDblClick': self.OnItemDblClick,
                 'name': 'subRepairEntry%s' % currIndex})
                currIndex += 1


        listEntryData.sort(lambda a, b: -(a['label'].upper() < b['label'].upper()))
        for entryData in listEntryData:
            scrolllist.append(listentry.Get('Item', entryData))

        if not totaldamage:
            activeShip = util.GetActiveShip()
            if activeShip is not None and activeShip in [ item.itemID for item in items ]:
                btnSetup[self.sr.repairAllBtn] = uiconst.UI_HIDDEN
        else:
            self.sr.repairAllBtn.OnClick = self.RepairAll
            self.sr.repairAllBtn.SetLabel(localization.GetByLabel('UI/Commands/RepairAll'))
            btnSetup[self.sr.repairAllBtn] = uiconst.UI_NORMAL
        self.sr.scroll.sr.id = 'repair3'
        self.sr.scroll.sr.ignoreTabTrimming = 0
        self.sr.scroll.Load(fixedEntryHeight=35, contentList=scrolllist, headers=[localization.GetByLabel('UI/Common/Type'), localization.GetByLabel('UI/Common/Damage'), localization.GetByLabel('UI/Common/Cost')])
        self.sr.avgDamage.text = localization.GetByLabel('UI/Station/Repair/AverageDamage', damage=totaldamage / (totalitems or 1))
        self.sr.totalCost.text = localization.GetByLabel('UI/Station/Repair/RepairCost', isk=int(math.ceil(totalcost)))
        self.state = uiconst.UI_NORMAL
        btnSetup[self.sr.pickBtn] = uiconst.UI_NORMAL
        self.DisplayButtons(btnSetup)



    def Repair(self, items, *args):
        self.RepairItems(items)



    def RepairAll(self, *args):
        self.RepairItems(self.GetAll())



    def RepairItems(self, items):
        totalcost = 0
        hasModule = False
        for item in items:
            damage = math.ceil(item.damage)
            totalcost = totalcost + math.ceil(item.damage) * item.costToRepairOneUnitOfDamage
            if cfg.invgroups.Get(item.groupID).categoryID == const.categoryModule:
                hasModule = True

        btnSetup = {self.sr.selBtn: uiconst.UI_HIDDEN,
         self.sr.pickBtn: uiconst.UI_NORMAL}
        if hasModule:
            if eve.Message('RepairNonPartialConfirmation', {'isk': util.FmtISK(totalcost)}, uiconst.YESNO) != uiconst.ID_YES:
                amount = None
            else:
                amount = {'qty': totalcost}
        else:
            amount = uix.QtyPopup(totalcost, 0, totalcost, hint=localization.GetByLabel('UI/Station/Repair/FullRepair', isk=totalcost), label=localization.GetByLabel('UI/Station/Repair/RepairCostLabel'), digits=2)
        if amount is not None:
            itemIDs = []
            try:
                for item in items:
                    if self.invCache.IsItemLocked(item.itemID):
                        raise UserError('ItemLocked', {'item': cfg.invtypes.Get(item.typeID).name})
                    if not self.invCache.TryLockItem(item.itemID, 'lockUnassemblingItem', {}, 1):
                        raise UserError('ItemLocked', {'item': cfg.invtypes.Get(item.typeID).name})
                    itemIDs.append(item.itemID)

                if len(itemIDs):
                    self.repairSvc.RepairItems(itemIDs, amount['qty'])

            finally:
                for itemID in itemIDs:
                    self.invCache.UnlockItem(itemID)

                uthread.new(self.DisplayRepairQuote, self.GetAll())

        else:
            btnSetup[self.sr.repairAllBtn] = uiconst.UI_NORMAL
        self.DisplayButtons(btnSetup)



    def Damage(self, items, *args):
        btnSetup = {self.sr.selBtn: uiconst.UI_HIDDEN,
         self.sr.pickBtn: uiconst.UI_DISABLED}
        temp = uix.QtyPopup(100, 1, 50, hint=localization.GetByLabel('UI/Station/Repair/ApplyDamage'))
        percentage = temp and temp['qty']
        if percentage == 0 or percentage is None:
            self.sr.pickBtn.state = uiconst.UI_NORMAL
            return 
        itemIDAndAmountOfDamageList = []
        try:
            for item in items:
                if self.invCache.IsItemLocked(item.itemID):
                    continue
                if not self.invCache.TryLockItem(item.itemID, 'lockRepairingItem', {}, 1):
                    continue
                amount = int(math.ceil(float(percentage) / 100.0 * float(item.maxHealth - item.damage)))
                itemIDAndAmountOfDamageList.append((item.itemID, amount))

            if len(itemIDAndAmountOfDamageList):
                self.repairSvc.DamageModules(itemIDAndAmountOfDamageList)

        finally:
            for (itemID, amount,) in itemIDAndAmountOfDamageList:
                self.invCache.UnlockItem(itemID)

            uthread.new(self.DisplayRepairQuote, self.GetAll())
            btnSetup[self.sr.pickBtn] = uiconst.UI_NORMAL

        self.DisplayButtons(btnSetup)



    def HideButtons(self):
        btnParent = self.sr.pickBtn.parent
        for btn in btnParent.children:
            btn.state = uiconst.UI_HIDDEN




    def DisplayButtons(self, btnSetup):
        for (btn, state,) in btnSetup.iteritems():
            btn.state = state

        totalWidth = 0
        btnParent = self.sr.pickBtn.parent
        for btn in btnParent.children:
            if btn.state != uiconst.UI_HIDDEN:
                totalWidth = totalWidth + btn.width

        left = self.sr.pickBtn.parent.width / 2 - totalWidth / 2
        for btn in btnParent.children:
            if btn.state != uiconst.UI_HIDDEN:
                btn.left = left
                left = left + btn.width





