import service
import blue

class LightAnimationComponent(object):
    __guid__ = 'component.LightAnimationComponent'

    def __init__(self):
        self.resPath = ''
        self.curveSet = None
        self.animationLength = None
        self.animationStartDelay = None
        self.light = None




class LightAnimationComponentManager(service.Service):
    __guid__ = 'svc.LightAnimationComponentManager'
    __componentTypes__ = ['LightAnimationComponent']
    __dependencies__ = []
    __notifyevents__ = []

    def __init__(self):
        service.Service.__init__(self)
        self.uiDesktop = None
        self.isServiceReady = False



    def Run(self, *etc):
        service.Service.Run(self, *etc)
        self.isServiceReady = True



    def CreateComponent(self, name, state):
        component = LightAnimationComponent()
        component.resPath = state['resPath']
        if 'length' in state:
            component.animationLength = state['length']
        if 'startDelay' in state:
            component.animationStartDelay = state['startDelay']
        return component



    def PrepareComponent(self, sceneID, entityID, component):
        component.curveSet = blue.os.LoadObject(component.resPath)



    def SetupComponent(self, entity, component):
        if entity.HasComponent('loadedLight'):
            component.light = entity.GetComponent('loadedLight').renderObject
        if component.curveSet is not None and component.light is not None:
            component.light.curveSets.append(component.curveSet)
            for b in component.curveSet.bindings:
                b.destinationObject = component.light

            for curve in component.curveSet.curves:
                if component.animationLength is not None:
                    curve.length = component.animationLength
                keyCount = curve.GetKeyCount()
                if component.animationStartDelay is not None:
                    for idx in xrange(keyCount):
                        curve.SetKeyTime(idx, curve.GetKeyTime(idx) + component.animationStartDelay)





    def UnRegisterComponent(self, entity, component):
        if component.curveSet is not None and component.light is not None:
            component.light.curveSets.remove(component.curveSet)
            for b in component.curveSet.bindings:
                b.destinationObject = None





