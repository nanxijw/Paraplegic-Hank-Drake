import effects
import trinity
import blue
import audio2
import util

class EMPWave(effects.GenericEffect):
    __guid__ = 'effects.EMPWave'

    def _Key(trigger):
        return (trigger.shipID,
         trigger.moduleID,
         None,
         None)


    _Key = staticmethod(_Key)

    def __init__(self, trigger):
        self.ballIDs = [trigger.shipID]
        self.gfx = None
        self.gfxModel = None
        self.radius = 5000.0
        self.moduleTypeID = trigger.moduleTypeID
        self.translationCurve = None



    def Stop(self):
        if self.gfx is None:
            raise RuntimeError('ShipEffect: no effect defined')
        scene2 = sm.StartService('sceneManager').GetRegisteredScene2('default')
        scene2.objects.fremove(self.gfxModel)
        self.gfx = None
        self.translationCurve = None
        self.gfxModel = None



    def Prepare(self):
        shipID = self.ballIDs[0]
        michelle = sm.StartService('michelle')
        shipBall = michelle.GetBall(shipID)
        if shipBall is None:
            raise RuntimeError('EMPWave: no ball found')
        if self.moduleTypeID == 0:
            self.moduleTypeID = 15957
        graphicID = cfg.invtypes.Get(self.moduleTypeID).graphicID
        if graphicID is None:
            raise RuntimeError('EMPWave: no graphic ID')
        gfxString = util.GraphicFile(graphicID)
        gfxString = gfxString.replace('.blue', '.red')
        gfxString = gfxString.replace('/Effect2/', '/Effect3/')
        self.gfx = trinity.Load(gfxString)
        if self.gfx is None:
            raise RuntimeError('EMPWave: no effect found')
        entity = audio2.AudEmitter('effect_' + str(shipID))
        obs = trinity.TriObserverLocal()
        obs.observer = entity
        if self.gfx.__bluetype__ in ('trinity.EveTransform',):
            self.gfx.observers.append(obs)
        for curveSet in self.gfx.curveSets:
            for curve in curveSet.curves:
                if curve.__typename__ == 'TriEventCurve' and curve.name == 'audioEvents':
                    curve.eventListener = entity


        self.gfxModel = trinity.EveRootTransform()
        radius = sm.StartService('godma').GetTypeAttribute(self.moduleTypeID, const.attributeEmpFieldRange)
        self.gfxModel.scaling = (radius / 1000, radius / 1000, radius / 1000)
        self.radius = radius
        self.gfxModel.name = self.__guid__
        self.gfxModel.children.append(self.gfx)
        self.gfxModel.translationCurve = shipBall
        scene2 = sm.StartService('sceneManager').GetRegisteredScene2('default')
        scene2.objects.append(self.gfxModel)



    def Start(self, duration):
        if self.gfx is None:
            raise RuntimeError('ShipEffect: no effect defined')
        if self.__scaleTime__ and len(self.gfxModel.curveSets) > 0:
            length = self.gfxModel.curveSets[0].GetMaxCurveDuration()
            if length > 0.0:
                scaleValue = length / (duration / 1000.0)
                self.gfxModel.curveSets[0].scale = scaleValue
        self.gfx.curveSets[0].Play()



    def Repeat(self, duration):
        if self.gfx is None:
            raise RuntimeError('EMPWave: no effect defined')
        shipID = self.ballIDs[0]
        shipBall = sm.GetService('michelle').GetBall(shipID)
        if shipBall is None:
            raise RuntimeError('EMPWave: no ball found')
        self.gfx.curveSets[0].Play()




