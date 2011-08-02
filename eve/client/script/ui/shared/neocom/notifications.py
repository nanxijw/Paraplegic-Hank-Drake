import service
import blue
import uthread
import uix
import uiutil
import xtriui
import form
import util
import listentry
import draw
import uiconst
import math
import base
import notificationUtil
import uicls
HINTCUTOFF = 100
DELETE_INTERVAL = 0.3 * SEC

class NotificationForm(uicls.Container):
    __guid__ = 'form.NotificationForm'
    __notifyevents__ = ['OnNotificationsRefresh', 'OnNewNotificationReceived', 'OnNotificationReadOutside']

    def Setup(self):
        sm.RegisterNotify(self)
        self.scrollHeight = 0
        self.DrawStuff()
        self.readTimer = 0
        self.viewing = None
        self.lastDeleted = 0



    def DrawStuff(self, *args):
        btns = uicls.ButtonGroup(btns=[[mls.UI_EVEMAIL_NOTIFICATIONS_MARKALLASREAD,
          self.MarkAllRead,
          None,
          81], [mls.UI_EVEMAIL_NOTIFICATIONS_DELETEALL,
          self.DeleteAll,
          None,
          81]], parent=self, idx=0, line=1)
        leftContWidth = settings.user.ui.Get('notifications_leftContWidth', 200)
        self.sr.leftCont = uicls.Container(name='leftCont', parent=self, align=uiconst.TOLEFT, pos=(const.defaultPadding,
         0,
         leftContWidth,
         0))
        self.sr.leftScroll = uicls.Scroll(name='leftScroll', parent=self.sr.leftCont, padding=(0,
         const.defaultPadding,
         0,
         const.defaultPadding))
        self.sr.leftScroll.multiSelect = 0
        divider = xtriui.Divider(name='divider', align=uiconst.TOLEFT, width=const.defaultPadding, parent=self, state=uiconst.UI_NORMAL)
        divider.Startup(self.sr.leftCont, 'width', 'x', 180, 250)
        self.sr.rightCont = uicls.Container(name='rightCont', parent=self, align=uiconst.TOALL, pos=(0,
         0,
         const.defaultPadding,
         const.defaultPadding))
        readingContHeight = settings.user.ui.Get('notifications_readingContHeight', 200)
        self.sr.readingPaneCont = uicls.Container(name='readingPaneCont', parent=self.sr.rightCont, align=uiconst.TOBOTTOM, pos=(0,
         0,
         0,
         readingContHeight))
        self.sr.readingPane = uicls.Edit(setvalue='', parent=self.sr.readingPaneCont, align=uiconst.TOALL, readonly=1)
        self.sr.divider = xtriui.Divider(name='divider', align=uiconst.TOBOTTOM, height=const.defaultPadding, parent=self.sr.rightCont, state=uiconst.UI_NORMAL)
        self.sr.divider.Startup(self.sr.readingPaneCont, 'height', 'y', 64, self.scrollHeight)
        self.sr.divider.OnSizeChanged = self.OnReadingScrollSizeChanged
        self.sr.msgCont = uicls.Container(name='msgCont', parent=self.sr.rightCont, align=uiconst.TOALL)
        self.sr.msgScroll = uicls.Scroll(name='msgScroll', parent=self.sr.msgCont, padding=(0,
         const.defaultPadding,
         0,
         0))
        self.sr.msgScroll.sr.id = 'notifications_msgs'
        self.sr.msgScroll.sr.fixedColumns = {mls.UI_EVEMAIL_STATUS: 52}
        self.sr.msgScroll.OnSelectionChange = self.MsgScrollSelectionChange
        self.sr.msgScroll.OnDelete = self.DeleteFromKeyboard
        self.inited = True



    def LoadNotificationForm(self, *args):
        self.LoadLeftSide()



    def OnReadingScrollSizeChanged(self, *args):
        h = self.sr.readingPaneCont.height
        (l, t, w, absHeight,) = self.sr.rightCont.GetAbsolute()
        if h > absHeight:
            h = absHeight
            ratio = float(h) / absHeight
            settings.user.ui.Set('notifications_msgScrollRatio', ratio)
            self._OnResize()
            return 
        ratio = float(h) / absHeight
        settings.user.ui.Set('notifications_msgScrollRatio', ratio)



    def OnClose_(self, *args):
        settings.user.ui.Set('notifications_leftContWidth', self.sr.leftCont.width)
        settings.user.ui.Set('notifications_readingContHeight', self.sr.readingPaneCont.height)
        sm.GetService('mailSvc').SaveChangesToDisk()
        sm.UnregisterNotify(self)



    def _OnResize(self, *args):
        if getattr(self, 'inited', False):
            (l, t, w, absHeight,) = self.sr.rightCont.GetAbsolute()
            self.scrollHeight = absHeight - 64
            ratio = settings.user.ui.Get('notifications_msgScrollRatio', 0.5)
            h = int(ratio * absHeight)
            if h > self.scrollHeight:
                h = self.scrollHeight
            self.sr.readingPaneCont.height = max(64, h)
            self.sr.divider.max = self.scrollHeight



    def LoadLeftSide(self):
        scrolllist = self.GetStaticLabelsGroups()
        self.sr.leftScroll.Load(contentList=scrolllist)
        lastViewedID = settings.char.ui.Get('mail_lastnotification', None)
        for entry in self.sr.leftScroll.GetNodes():
            if entry.groupID is None:
                continue
            if entry.groupID == lastViewedID:
                panel = entry.panel
                if panel is not None:
                    self.UpdateCounters()
                    panel.OnClick()
                    return 

        self.UpdateCounters()
        if len(self.sr.leftScroll.GetNodes()) > 0:
            entry = self.sr.leftScroll.GetNodes()[0]
            panel = entry.panel
            if panel is not None:
                panel.OnClick()



    def GetStaticLabelsGroups(self):
        scrolllist = []
        lastViewedID = settings.char.ui.Get('mail_lastnotification', None)
        for (groupID, label,) in notificationUtil.groupNames.iteritems():
            entry = self.GetGroupEntry(groupID, label, groupID == lastViewedID)
            scrolllist.append((label.lower(), entry))

        scrolllist = uiutil.SortListOfTuples(scrolllist)
        entry = self.GetGroupEntry(const.notificationGroupUnread, mls.UI_GENERIC_UNREAD, const.notificationGroupUnread == lastViewedID)
        scrolllist.insert(0, entry)
        scrolllist.insert(1, listentry.Get('Space', {'height': 12}))
        return scrolllist



    def GetGroupEntry(self, groupID, label, selected = 0):
        data = {'GetSubContent': self.GetLeftGroups,
         'label': label,
         'id': ('notification', id),
         'state': 'locked',
         'BlockOpenWindow': 1,
         'disableToggle': 1,
         'expandable': 0,
         'showicon': 'hide',
         'showlen': 0,
         'groupItems': [],
         'hideNoItem': 1,
         'hideExpander': 1,
         'hideExpanderLine': 1,
         'selectGroup': 1,
         'isSelected': selected,
         'groupID': groupID,
         'OnClick': self.LoadGroupFromEntry,
         'MenuFunction': self.StaticMenu}
        entry = listentry.Get('Group', data)
        return entry



    def GetLeftGroups(self, *args):
        return []



    def LoadGroupFromEntry(self, entry, *args):
        group = entry.sr.node
        self.LoadGroupFromNode(group)



    def LoadGroupFromNode(self, node, refreshing = 0, selectedIDs = [], *args):
        group = node
        settings.char.ui.Set('mail_lastnotification', group.groupID)
        notifications = []
        if group.groupID == const.notificationGroupUnread:
            notifications = sm.GetService('notificationSvc').GetFormattedUnreadNotifications()
            senders = [ value.senderID for value in sm.GetService('notificationSvc').GetUnreadNotifications() ]
        else:
            notifications = sm.GetService('notificationSvc').GetFormattedNotifications(group.groupID)
            senders = [ value.senderID for value in sm.GetService('notificationSvc').GetNotificationsByGroupID(group.groupID) ]
        sm.GetService('mailSvc').PrimeOwners(senders)
        if not self or self.destroyed:
            return 
        pos = self.sr.msgScroll.GetScrollProportion()
        scrolllist = []
        for each in notifications:
            label = ''
            senderName = ''
            if each.senderID is not None:
                senderName = cfg.eveowners.Get(each.senderID).ownerName
            label = '<t>%s<t>%s<t>%s' % (senderName, each.subject, util.FmtDate(each.created, 'ls'))
            if group.groupID == const.notificationGroupUnread:
                typeGroup = notificationUtil.GetTypeGroup(each.typeID)
                typeName = notificationUtil.groupNames.get(typeGroup, '')
                label += '<t>%s' % typeName
            hint = each.body.replace('<br>', '')
            if len(hint) > HINTCUTOFF:
                hint = hint[:HINTCUTOFF] + '...'
            data = util.KeyVal()
            data.cleanLabel = label
            data.parentNode = node
            data.label = label
            data.hint = hint
            data.id = each.notificationID
            data.typeID = each.typeID
            data.senderID = each.senderID
            data.data = util.KeyVal(read=each.processed)
            data.info = each
            data.OnClick = self.LoadReadingPaneFromEntry
            data.OnDblClick = self.DblClickNotificationEntry
            data.GetMenu = self.GetEntryMenu
            data.ignoreRightClick = 1
            data.isSelected = each.notificationID in selectedIDs
            data.Draggable_blockDrag = 1
            scrolllist.append(listentry.Get('MailEntry', data=data))

        scrollHeaders = [mls.UI_EVEMAIL_STATUS,
         mls.UI_EVEMAIL_SENDER,
         mls.UI_EVEMAIL_SUBJECT,
         mls.UI_EVEMAIL_RECEIVED]
        if group.groupID == const.notificationGroupUnread:
            scrollHeaders.append(mls.UI_GENERIC_GROUPNAME)
        if not self or self.destroyed:
            return 
        self.sr.msgScroll.Load(contentList=scrolllist, headers=scrollHeaders, noContentHint=mls.UI_GENERIC_NOITEMSFOUND)
        if not refreshing:
            self.ClearReadingPane()
        else:
            self.sr.msgScroll.ScrollToProportion(pos)
        self.UpdateCounters()



    def StaticMenu(self, node, *args):
        m = []
        if node.groupID != const.notificationGroupUnread:
            m.append((mls.UI_EVEMAIL_NOTIFICATIONS_MARKALLASREAD, self.MarkAllReadInGroup, (node.groupID,)))
            m.append(None)
            m.append((mls.UI_EVEMAIL_NOTIFICATIONS_DELETEALL, self.DeleteAllFromGroup, (node.groupID,)))
        return m



    def DeleteAll(self, *args):
        if eve.Message('EvemailNotificationsDeleteAll', {}, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
            sm.GetService('notificationSvc').DeleteAll()



    def MarkAllRead(self, *args):
        if eve.Message('EvemailNotificationsMarkAllRead', {}, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
            sm.GetService('notificationSvc').MarkAllRead()



    def DeleteAllFromGroup(self, groupID, *args):
        if eve.Message('EvemailNotificationsDeleteGroup', {}, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
            sm.GetService('notificationSvc').DeleteAllFromGroup(groupID)



    def MarkAllReadInGroup(self, groupID, *args):
        sm.GetService('notificationSvc').MarkAllReadInGroup(groupID)



    def GetEntryMenu(self, entry, *args):
        m = []
        sel = self.sr.msgScroll.GetSelected()
        selIDs = [ x.id for x in sel ]
        msgID = entry.sr.node.id
        if msgID not in selIDs:
            selIDs = [msgID]
            sel = [entry.sr.node]
        unread = {}
        for each in sel:
            if not each.data.read:
                unread[each.id] = each

        if len(unread) > 0:
            m.append((mls.UI_EVEMAIL_MARKASREAD, self.MarkAsRead, (unread.values(), unread.keys())))
        m.append(None)
        if len(selIDs) > 0:
            m.append((mls.UI_CMD_DELETE, self.DeleteNotifications, (sel, selIDs)))
        return m



    def MarkAsRead(self, notifications, notificationIDs, *args):
        sm.GetService('notificationSvc').MarkAsRead(notificationIDs)
        self.UpdateCounters()
        self.SetMsgEntriesAsRead(notifications)



    def DblClickNotificationEntry(self, entry):
        messageID = entry.sr.node.id
        info = entry.sr.node.info
        sm.GetService('notificationSvc').OpenNotificationReadingWnd(info)



    def LoadReadingPaneFromEntry(self, entry):
        uthread.new(self.LoadReadingPaneFromNode, entry.sr.node)



    def LoadReadingPaneFromNode(self, node):
        shift = uicore.uilib.Key(uiconst.VK_SHIFT)
        if not shift:
            self.LoadReadingPane(node)



    def LoadReadingPane(self, node):
        self.readTimer = 0
        info = node.info
        txt = sm.GetService('notificationSvc').GetReadingText(node.senderID, info.subject, info.created, info.body)
        self.sr.readingPane.SetText(txt)
        self.viewing = node.id
        if not node.data.read:
            self.MarkAsRead([node], [node.id])



    def ClearReadingPane(self):
        self.sr.readingPane.SetText('')
        self.viewing = None



    def SetMsgEntriesAsRead(self, nodes):
        for node in nodes:
            self.TryReloadNode(node)




    def TryReloadNode(self, node):
        node.data.read = 1
        panel = node.Get('panel', None)
        if panel is None:
            return 
        panel.LoadMailEntry(node)



    def MsgScrollSelectionChange(self, sel = [], *args):
        if len(sel) == 0:
            return 
        node = sel[0]
        if self.viewing != node.id:
            self.readTimer = base.AutoTimer(1000, self.LoadReadingPane, node)



    def DeleteFromKeyboard(self, *args):
        if blue.os.GetTime() - self.lastDeleted < DELETE_INTERVAL:
            eve.Message('uiwarning03')
            return 
        sel = self.sr.msgScroll.GetSelected()
        ids = [ each.id for each in sel ]
        self.DeleteNotifications(sel, ids)
        self.lastDeleted = blue.os.GetTime()



    def DeleteNotifications(self, notificationEntries, ids):
        if len(notificationEntries) < 1:
            return 
        idx = notificationEntries[0].idx
        ids = []
        for entry in notificationEntries:
            ids.append(entry.id)

        sm.GetService('notificationSvc').DeleteNotifications(ids)
        sm.ScatterEvent('OnMessageChanged', const.mailTypeNotifications, ids, 'deleted')
        self.sr.msgScroll.RemoveEntries(notificationEntries)
        if self.viewing in ids:
            self.ClearReadingPane()
        self.UpdateCounters()
        if len(self.sr.msgScroll.GetNodes()) < 1:
            self.sr.msgScroll.Load(contentList=[], headers=[], noContentHint=mls.UI_GENERIC_NOITEMSFOUND)
            return 
        numChildren = len(self.sr.msgScroll.GetNodes())
        newIdx = min(idx, numChildren - 1)
        newSelectedNode = self.sr.msgScroll.GetNode(newIdx)
        if newSelectedNode is not None:
            self.sr.msgScroll.SelectNode(newSelectedNode)



    def OnNotificationsRefresh(self):
        self.LoadLeftSide()



    def OnNewNotificationReceived(self):
        self.UpdateCounters()



    def OnNotificationReadOutside(self, notificationID):
        self.UpdateCounters()
        for node in self.sr.msgScroll.GetNodes():
            if node.id == notificationID:
                self.SetMsgEntriesAsRead([node])
                return 




    def UpdateCounters(self):
        unreadCounts = sm.GetService('notificationSvc').GetAllUnreadCount()
        for each in self.sr.leftScroll.GetNodes():
            if each.groupID is None:
                continue
            count = unreadCounts.get(each.groupID, 0)
            self.TryChangePanelLabel(each, count)




    def TryChangePanelLabel(self, node, count):
        panel = node.Get('panel', None)
        if panel is None:
            return 
        panelLabel = self.GetPanelLabel(node.cleanLabel, count)
        panel.sr.label.text = panelLabel



    def GetPanelLabel(self, label, count):
        if count > 0:
            return '<b>%s (%s)</b>' % (label, count)
        else:
            return label




