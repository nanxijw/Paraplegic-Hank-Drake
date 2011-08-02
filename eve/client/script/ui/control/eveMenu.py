import uicls
import uiutil
import uiconst

class DropDownMenu(uicls.DropDownMenuCore):
    __guid__ = 'uicls.DropDownMenu'

    def Prepare_Background_(self, *args):
        self.sr.underlay = uicls.WindowUnderlay(parent=self, transparent=False, padding=(0, 0, 0, 0))




class MenuEntryView(uicls.MenuEntryViewCore):
    __guid__ = 'uicls.MenuEntryView'

    def Prepare_Label_(self, *args):
        self.sr.label = uicls.Label(text='', parent=self, left=8, top=1, letterspace=1, fontsize=10, state=uiconst.UI_DISABLED, align=uiconst.CENTERLEFT)



    def Prepare_Hilite_(self, *args):
        self.sr.hilite = uicls.Fill(parent=self, color=(1.0, 1.0, 1.0, 0.25), padTop=1)




