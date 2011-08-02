import spaceObject
import blue
import timecurves
import nodemanager
import trinity
RED = trinity.TriColor(1.0, 0.18, 0.02)
GREEN = trinity.TriColor(0.27, 0.53, 0.22)
YELLOW = trinity.TriColor(0.53, 0.53, 0.08)

class MobileWarpDisruptor(spaceObject.DeployableSpaceObject):
    __guid__ = 'spaceObject.MobileWarpDisruptor'

    def Assemble(self):
        godmaStateManager = sm.StartService('godma').GetStateManager()
        slimItem = sm.StartService('michelle').GetBallpark().GetInvItem(self.id)
        godmaType = godmaStateManager.GetType(slimItem.typeID)
        self.effectRadius = godmaType.warpScrambleRange
        damages = nodemanager.FindNodes(self.model, 'locator_damage', 'trinity.TriTransform')
        self.damages = damages
        spaceObject.DeployableSpaceObject.SetColorBasedOnStatus(self)



    def SetColor(self, col):
        if col == 'red':
            self.SetRadius(self.effectRadius)
            for cs in self.model.curveSets:
                if cs.name == 'State':
                    cs.curves[0].value = RED
                if cs.name == 'Activation':
                    cs.Play()

        elif col == 'yellow':
            for cs in self.model.curveSets:
                if cs.name == 'State':
                    cs.curves[0].value = YELLOW

        elif col == 'green':
            self.SetRadius(0.0)
            for cs in self.model.curveSets:
                if cs.name == 'State':
                    cs.curves[0].value = GREEN




    def SetRadius(self, r):
        self.model.children[0].children[0].children[0].scaling = (-r, r, r)



    def Release(self):
        if self.released:
            return 
        self.damages = None
        spaceObject.SpaceObject.Release(self, 'MobileWarpDisruptor')



exports = {'spaceObject.MobileWarpDisruptor': MobileWarpDisruptor}

