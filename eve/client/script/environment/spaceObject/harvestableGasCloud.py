import spaceObject
import timecurves
import random
import log

class HarvestableGasCloud(spaceObject.Asteroid):
    __guid__ = 'spaceObject.HarvestableGasCloud'

    def LoadModel(self, fileName = None, useInstance = False, loadedModel = None):
        slimItem = sm.StartService('michelle').GetBallpark().GetInvItem(self.id)
        if slimItem is not None:
            type = cfg.invtypes.Get(slimItem.typeID)
            typeName = type.typeName
            model = None
            fileName = cfg.invtypes.Get(slimItem.typeID).GraphicFile()
            spaceObject.SpaceObject.LoadModel(self, fileName)



    def SetRadius(self, r):
        self.model.scaling.SetXYZ(r * 10.0, r * 10.0, r * 10.0)



exports = {'spaceObject.HarvestableGasCloud': HarvestableGasCloud}

