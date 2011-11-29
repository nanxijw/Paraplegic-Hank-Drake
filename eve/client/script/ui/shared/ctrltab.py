import uix
import xtriui
import uiconst
import math
import uthread
import uiutil
import uicls
import localization
ICONWIDTH = 50
SPACINGWIDTH = 6
NUMCOLS = 5
BORDER = 5
BLOCKSIZE = ICONWIDTH + SPACINGWIDTH
FRAMECOLOR = (0.3, 0.3, 0.3, 0.5)
FILLCOLOR = (0.0, 0.0, 0.0, 0.8)
SELECTCOLOR = (0.5, 0.5, 0.5, 0.5)

class CtrlTabWindow(uicls.Window):
    __guid__ = 'form.CtrlTabWindow'
    default_windowID = 'CtrlTabWindow'

    def ApplyAttributes(self, attributes):
        uicls.Window.ApplyAttributes(self, attributes)
        self._caption = self.name = 'CtrlTabWindow'
        self.HideHeader()
        self.SetWndIcon(None)
        self.SetTopparentHeight(0)
        self.SetMainIconSize(0)
        self.MakeUncollapseable()
        self.MakeUnpinable()
        self.MakeUnMinimizable()
        self.MakeUnResizeable()
        self.MakeUnKillable()
        self.HideUnderlay()
        self.MakeUnstackable()
        uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEDOWN, self.OnGlobalMouseDown)
        uicls.Frame(parent=self, color=FRAMECOLOR)
        uicls.Fill(parent=self, color=FILLCOLOR)
        self.currOpenWindows = uicore.registry.GetWindows()[:]
        self.showOrHide = self.AllWindowsMinimized()
        self.selectionBoxIndex = None
        self.windowIcons = []
        self.showOrHideMessage = [localization.GetByLabel('UI/Common/Windows/HideWindows'), localization.GetByLabel('UI/Common/Windows/ShowWindows')][self.showOrHide]
        self.InitializeWindowIcons()
        self.numIcons = len(self.windowIcons)
        self.numRows = int(math.ceil(float(self.numIcons) / float(NUMCOLS)))
        if self.numRows > 1:
            self.xShift = 0
        else:
            self.xShift = (NUMCOLS - self.numIcons) * BLOCKSIZE / 2
        uthread.new(self.SetWindowSize)
        self.RenderIcons()
        self.sr.selectionBox = uicls.Container(name='selectionBox', parent=self.sr.main, align=uiconst.RELATIVE, pos=(SPACINGWIDTH,
         SPACINGWIDTH,
         ICONWIDTH,
         ICONWIDTH))
        uicls.Fill(parent=self.sr.selectionBox, color=SELECTCOLOR)
        self.sr.selectionBoxMouse = uicls.Container(name='selectionBox', parent=self.sr.main, align=uiconst.RELATIVE, pos=(SPACINGWIDTH,
         SPACINGWIDTH,
         ICONWIDTH,
         ICONWIDTH), state=uiconst.UI_HIDDEN)
        uicls.Fill(parent=self.sr.selectionBoxMouse, color=SELECTCOLOR)
        self.sr.windowText = uicls.EveLabelLarge(parent=self.sr.main, align=uiconst.TOBOTTOM, color=(1, 1, 1, 1), state=uiconst.UI_DISABLED, padding=BORDER)



    def SetWindowSize(self):
        self.width = BLOCKSIZE * NUMCOLS + SPACINGWIDTH + 2 * BORDER + 2
        self.height = BLOCKSIZE * self.numRows + 3 * BORDER + self.sr.windowText.height



    def InitializeWindowIcons(self):
        currOpenWindows = uicore.registry.GetWindows()
        self.windowIcons = []
        i = 0
        for w in currOpenWindows:
            if not hasattr(w, 'iconNum') or w._caption == self._caption or not isinstance(w, uicls.Window):
                continue
            if w.iconNum is not None and not w.iconNum.startswith('c_'):
                iconNum = w.iconNum
            else:
                iconNum = 'ui_9_64_9'
            self.windowIcons.append({'id': i,
             'name': w.windowID,
             'caption': w._caption,
             'iconNum': iconNum})
            i += 1

        self.windowIcons.append({'id': len(self.windowIcons),
         'name': self.showOrHideMessage,
         'caption': self.showOrHideMessage,
         'iconNum': 'ui_9_64_7',
         'isShowOrHideIcon': True})



    def RenderSelectionBox(self):
        (self.sr.selectionBox.left, self.sr.selectionBox.top,) = self.IndexToPosition(self.selectionBoxIndex)



    def RenderSelectionBoxMouse(self):
        (self.sr.selectionBox.left, self.sr.selectionBox.top,) = self.IndexToPosition(self.selectionBoxIndex)



    def RenderIcons(self):
        for (i, w,) in enumerate(self.windowIcons):
            (x, y,) = self.IndexToPosition(i)
            icon = uicls.Icon(icon=w['iconNum'], parent=self.sr.main, pos=(x,
             y,
             ICONWIDTH,
             ICONWIDTH), ignoreSize=1)
            icon.OnMouseEnter = (self.OnMouseEnterIcon, w)
            icon.OnMouseExit = self.OnMouseLeaveIcon
            icon.OnClick = (self.OnMouseClickIcon, w)




    def SetText(self, text):
        self.sr.windowText.text = '<center>' + text
        self.SetWindowSize()



    def OnMouseEnterIcon(self, icon):
        if icon['id'] != self.selectionBoxIndex:
            self.sr.selectionBoxMouse.state = uiconst.UI_NORMAL
            (self.sr.selectionBoxMouse.left, self.sr.selectionBoxMouse.top,) = self.IndexToPosition(icon['id'])
            self.SetText(icon['caption'])



    def OnMouseLeaveIcon(self):
        self.sr.selectionBoxMouse.state = uiconst.UI_HIDDEN
        if self.selectionBoxIndex is not None:
            self.SetText(self.windowIcons[self.selectionBoxIndex]['caption'])



    def OnMouseClickIcon(self, icon):
        self.selectionBoxIndex = icon['id']
        self.ChooseHilited()



    def IndexToPosition(self, index):
        colNum = index % NUMCOLS
        rowNum = (index - colNum) / NUMCOLS
        xPos = self.xShift + SPACINGWIDTH + colNum * BLOCKSIZE + BORDER
        yPos = SPACINGWIDTH + rowNum * BLOCKSIZE + BORDER
        return (xPos, yPos)



    def Next(self):
        self.Maximize()
        if self.selectionBoxIndex is None:
            self.selectionBoxIndex = 0
        else:
            self.selectionBoxIndex = self.selectionBoxIndex + 1
            if self.selectionBoxIndex >= self.numIcons:
                self.selectionBoxIndex = 0
        self.RenderSelectionBox()
        caption = self.windowIcons[self.selectionBoxIndex]['caption']
        if caption is None or len(caption) == 0:
            self.SetText(' ')
        else:
            self.SetText(self.windowIcons[self.selectionBoxIndex]['caption'])



    def Prev(self):
        self.Maximize()
        if self.selectionBoxIndex is None:
            self.selectionBoxIndex = self.numIcons - 1
        else:
            self.selectionBoxIndex = self.selectionBoxIndex - 1
            if self.selectionBoxIndex < 0:
                self.selectionBoxIndex = self.numIcons - 1
        self.RenderSelectionBox()
        caption = self.windowIcons[self.selectionBoxIndex]['caption']
        if caption is None or len(caption) == 0:
            self.SetText(' ')
        else:
            self.SetText(self.windowIcons[self.selectionBoxIndex]['caption'])



    def ChooseHilited(self):
        winIcon = self.windowIcons[self.selectionBoxIndex]
        if 'isShowOrHideIcon' in winIcon:
            self.showOrHide = int(not self.showOrHide)
            if self.showOrHide:
                uicore.cmd.CmdMinimizeAllWindows()
            else:
                for w in self.currOpenWindows:
                    w.Maximize()

        else:
            win = uicls.Window.GetIfOpen(windowID=winIcon['name'])
            self.currOpenWindows.remove(win)
            self.currOpenWindows.insert(0, win)
            win.Maximize()
        self.Close()



    def AllWindowsMinimized(self):
        for w in self.currOpenWindows:
            if w.state != uiconst.UI_HIDDEN and w.sr.stack is None and w._minimizable:
                return False

        return True



    def OnGlobalMouseDown(self, downOn, *args, **kw):
        if not uiutil.IsUnder(downOn, self.sr.main):
            self.Close()




