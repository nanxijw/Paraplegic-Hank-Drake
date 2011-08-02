import blue
import trinity
from string import split, find

def GetFilename():
    import app
    if hasattr(app, 'macro'):
        filename = app.macro.currentScript
    else:
        filename = app.Config.currentScript
    if filename.rfind('/') > 0:
        filename = filename[(filename.rfind('/') + 1):]
    elif filename.rfind('\\') > 0:
        filename = filename[(filename.rfind('\\') + 1):]
    if filename.rfind('.') > 0:
        filename = filename[:filename.rfind('.')]
    return filename


New = blue.os.CreateInstance

class PyROT:

    def __init__(self):
        self.rot = New('blue.Rot')



    def GetInstance(self, name, clsid = '', ret = None):
        if clsid == '':
            return self.rot.GetInstance(name, clsid, ret)
        else:
            return self.rot.GetInstance(name, clsid)



    def GetNewInstance(self, name, clsid):
        obj = self.GetInstance(name, clsid)
        fresh = New(clsid)
        fresh.CopyTo(obj)
        return obj



    def Copy(self, name, name2):
        obj = self.rot.GetInstance(name)
        if not obj:
            return 0
        obj2 = self.rot.GetInstance(name2)
        if obj2:
            return 0
        rot.RegisterObject(obj, name2)
        return 1



    def DeepCopy(self, name, name2):
        pass



    def ShallowCopy(self, name, name2):
        pass



    def Move(self, name, name2):
        pass



    def Delete(self, name):
        pass



myRot = PyROT()
rot = myRot
from string import join

class DeepCmp:

    def __init__(self):
        self.fieldList = []
        self.attributeList = []
        self.compMap = {'TriVector': ['z', 'y', 'x'],
         'TriQuaternion': ['w',
                           'z',
                           'y',
                           'x'],
         'TriColor': ['a',
                      'b',
                      'g',
                      'r']}
        self.excludeList = []
        self.compareList = []



    def CompVector(self, var1, var2, variables):
        diff = 0
        for mem in variables:
            self.fieldList.append(mem)
            v1 = str(getattr(var1, mem))
            v2 = str(getattr(var2, mem))
            if v1 != v2:
                diff = 1
                self.attributeList.append(join(self.fieldList, '.') + ' (' + v1 + ', ' + v2 + ')')
            self.fieldList.pop(-1)

        return diff



    def CompBlueList(self, list1, list2):
        if len(list1) != len(list2):
            return 1
        diff = 0
        diffAll = 0
        for i in range(len(list1)):
            savename = self.fieldList[-1]
            self.fieldList[-1] += '[' + str(i) + ']'
            diff = self.CompareMember(list1[i], list2[i])
            if diff:
                diffAll = 1
                self.attributeList.append(join(self.fieldList, '.'))
            self.fieldList[-1] = savename

        return diffAll



    def Cmp(self, obj1, obj2):
        self.fieldList = []
        self.attributeList = []
        yada = self.DeepCompare(obj1, obj2)
        if yada:
            if self.compareList:
                for attrString in self.attributeList[:]:
                    flag = 0
                    for compStr in self.compareList:
                        if attrString.find(compStr) > 0:
                            flag = 1

                    if not flag:
                        self.attributeList.remove(attrString)

            self.attributeList.reverse()
            return self.attributeList
        return []



    def DeepCompare(self, obj1, obj2):
        self.fieldList.append(getattr(obj1, '__typename__', ''))
        import blue
        (BeREAD, BeBOOL, BePERSIST,) = (1, 4, 16)
        type1 = getattr(obj1, '__typename__', None)
        type2 = getattr(obj2, '__typename__', None)
        if type1 != type2:
            self.attributeList.append(join(self.fieldList, '.') + ' (' + str(type1) + ', ' + str(type2) + ')')
            return self.fieldList
        memberDict = obj1.TypeInfo()[2]
        diffAll = 0
        for item in memberDict.iteritems():
            if item[1].has_key('editflags'):
                if item[1]['editflags'] & BePERSIST:
                    if self.excludeList:
                        if item[0] in self.excludeList:
                            continue
                    self.fieldList.append(item[0])
                    if item[1]['type'] == BeBOOL:
                        v1 = getattr(obj1, item[0])
                        v2 = getattr(obj2, item[0])
                        diff = (not v1) != (not v2)
                        if diff:
                            diffAll = 1
                            self.attributeList.append(join(self.fieldList, '.') + ' (' + str(v1) + ', ' + str(v2) + ')')
                    elif type(getattr(obj1, item[0])).__name__ == 'BlueWrapper':
                        diff = self.CompareMember(getattr(obj1, item[0]), getattr(obj2, item[0]))
                        if diff:
                            diffAll = 1
                            self.attributeList.append(join(self.fieldList, '.'))
                    else:
                        v1 = getattr(obj1, item[0])
                        v2 = getattr(obj2, item[0])
                        if v1 != v2:
                            diffAll = 1
                            self.attributeList.append(join(self.fieldList, '.') + ' (' + str(v1) + ', ' + str(v2) + ')')
                    self.fieldList.pop(-1)

        self.fieldList.pop(-1)
        return diffAll



    def CompareMember(self, var1, var2):
        if self.compMap.has_key(var1.__typename__):
            return self.CompVector(var1, var2, self.compMap[var1.__typename__])
        else:
            if var1.__typename__ == 'List':
                return self.CompBlueList(var1, var2)
            return self.DeepCompare(var1, var2)




def NewScene(name):
    ret = myRot.GetNewInstance('imports:/' + GetFilename() + '/Scene/' + name, 'trinity.TriScene')
    ret.name = name
    return ret



def NewUI(name):
    ret = myRot.GetNewInstance('imports:/' + GetFilename() + '/UI/' + name, 'trinity.TriUI')
    ret.name = name
    return ret



def NewCamera(name):
    ret = myRot.GetNewInstance('imports:/' + GetFilename() + '/Camera/' + name, 'trinity.TriCamera')
    ret.name = name
    return ret



def NewTransform(name, url = ''):
    if url == '':
        url = 'imports:/' + GetFilename() + '/Transform/' + name
    ret = trinity.TriTransform()
    ret.name = name
    return ret



def NewSplTransform(name, url = ''):
    if url == '':
        url = 'imports:/' + GetFilename() + '/SplTransform/' + name
    ret = trinity.TriSplTransform()
    ret.name = name
    return ret



def NewFlare(name, texture = None, shader = None, url = ''):
    if url == '':
        url = 'imports:/' + GetFilename() + '/Flare/' + name
    ret = myRot.GetNewInstance(url, 'trinity.TriFlare')
    ret.name = name
    if texture and shader:
        ret.flare = NewTransform(name)
        ret.flare.transformBase = trinity.TRITB_CAMERA_ROTATION
        ret.flare.object = NewModel(name + 'Model', 'res:/model/global/Zsprite.tri')
        area = ret.flare.object.areas[0]
        area.name = 'WholeSprite'
        mat = NewMaterial(name + 'Material')
        area.areaMaterials.append(mat)
        tex = NewTexture(name + 'Texture', texture)
        tex.magFilter = trinity.TRITEXF_ANISOTROPIC
        tex.minFilter = trinity.TRITEXF_ANISOTROPIC
        tex.mipFilter = trinity.TRITEXF_LINEAR
        area.areaTextures.append(tex)
        area.shader = shader
    return ret



def NewNebula(name, url = ''):
    if url == '':
        url = 'imports:/' + GetFilename() + '/Nebula/' + name
    ret = myRot.GetNewInstance(url, 'trinity.TriTransform')
    ret.name = name
    return ret



def NewPlanet(name, url = ''):
    if url == '':
        url = 'imports:/' + GetFilename() + '/Planet/' + name
    ret = myRot.GetNewInstance(url, 'trinity.TriTransform')
    ret.name = name
    return ret



def NewControl(name, url = ''):
    if url == '':
        url = 'imports:/' + GetFilename() + '/Control/' + name
    ret = myRot.GetNewInstance(url, 'trinity.TriTransform')
    ret.name = name
    return ret



def NewSun(name, url = ''):
    if url == '':
        url = 'imports:/' + GetFilename() + '/Sun/' + name
    ret = myRot.GetNewInstance(url, 'trinity.TriTransform')
    ret.name = name
    return ret



def NewParticleEmitter(name, url = ''):
    if url == '':
        url = 'imports:/' + GetFilename() + '/ParticleEmitter/' + name
    ret = myRot.GetNewInstance(url, 'trinity.TriTransform')
    ret.name = name
    return ret



def NewModel(name, vertices = '', url = ''):
    if url == '':
        url = 'imports:/' + GetFilename() + '/Model/' + name
    ret = trinity.TriModel()
    ret.name = name
    if vertices != '':
        ret.vertices = vertices
    return ret



def NewShader(name, url = ''):
    if url == '':
        url = 'imports:/' + GetFilename() + '/Shader/' + name
    ret = trinity.TriShader()
    ret.name = name
    return ret



def NewPass(name, url = ''):
    if url == '':
        url = 'imports:/' + GetFilename() + '/Pass/' + name
    ret = trinity.TriPass()
    ret.name = name
    if url == 'imports:/' + GetFilename() + '/Pass/' + name:
        ret.textureStage0 = NewTextureStage('TS0' + name)
        ret.textureStage1 = NewTextureStage('TS1' + name)
    return ret



def NewTextureStage(name, url = ''):
    if url == '':
        url = 'imports:/' + GetFilename() + '/TextureStage/' + name
    ret = trinity.TriTextureStage()
    ret.name = name
    return ret



def NewTexture(name, pixels = '', url = ''):
    name = split(pixels, '/')[-1:][0]
    if url == '':
        url = 'imports:/' + GetFilename() + name
    ret = trinity.TriTexture()
    ret.name = name
    if pixels != '':
        ret.pixels = pixels
    return ret



def NewMaterial(name, url = ''):
    if url == '':
        url = 'imports:/' + GetFilename() + '/Material/' + name
    ret = trinity.TriMaterial()
    ret.name = name
    return ret



def NewRadar(name, url = ''):
    if url == '':
        url = 'imports:/' + GetFilename() + '/Radar/' + name
    ret = myRot.GetNewInstance(url, 'trinity.TriRadar')
    ret.name = name
    return ret



def NewRadarObject(name, url = ''):
    if url == '':
        url = 'imports:/' + GetFilename() + '/RadarObject/' + name
    ret = myRot.GetNewInstance(url, 'trinity.TriRadarObject')
    ret.name = name
    return ret



def NewPointStarfield(name, url = ''):
    if url == '':
        url = 'imports:/' + GetFilename() + '/PointStarfield/' + name
    ret = myRot.GetNewInstance(url, 'trinity.TriPointStarfield')
    ret.name = name
    return ret



def NewLight(name, url = ''):
    if url == '':
        url = 'imports:/' + GetFilename() + '/Light/' + name
    ret = myRot.GetNewInstance(url, 'trinity.TriLight')
    ret.name = name
    return ret



def NewLine(name, url = ''):
    if url == '':
        url = 'imports:/' + GetFilename() + '/Line/' + name
    ret = myRot.GetNewInstance(url, 'trinity.TriLine')
    ret.name = name
    return ret



def NewLensFlare(name, url = ''):
    if url == '':
        url = 'imports:/' + GetFilename() + '/LensFlare/' + name
    ret = myRot.GetNewInstance(url, 'trinity.TriLensFlare')
    ret.name = name
    return ret



def AddModel(tf):
    dev = trinity.device
    if not dev:
        print 'no device available'
    else:
        AddToListUnique(dev.scene.models, tf)



def NewSimpleOnePassShader(name, texture1, matSrc, texSrc):
    ret = NewShader(name)
    pass0 = NewPass(name + 'Pass0')
    pass0.materialSource = matSrc
    pass0.materialSourceIndex = 0
    pass0.textureStage0.textureSource = texSrc
    pass0.textureStage0.textureSourceIndex = 0
    pass0.textureStage1.display = 0
    AddToListUnique(ret.passes, pass0)
    if texture1 != '':
        tex = NewTexture(name + 'Texture', texture1)
        AddToListUnique(ret.shaderTextures, tex)
    elif texSrc == trinity.TRITEXSRC_SHADER or texSrc == trinity.TRITEXSRC_NONE:
        pass0.textureStage0.colorOp = trinity.TRITOP_DISABLE
    mat = NewMaterial(name + 'Material')
    AddToListUnique(ret.shaderMaterials, mat)
    return ret



def AssignShaderToModel(model, areaNum, areaName, shader):
    if areaNum < len(model.areas):
        model.areas[areaNum].shader = shader
        model.areas[areaNum].name = areaName



def SetNebula(scene, tex):
    tf = New('trinity.TriTransform')
    tf.scaling.SetXYZ(19000.0, 19000.0, 19000.0)
    tf.transformBase = 2
    model = New('trinity.TriModel')
    tf.object = model
    model.vertices = 'res:/Model/Global/sphereOneAreaShape.tri'
    area = model.areas[0]
    tx = New('trinity.TriTexture')
    tx.pixels = tex
    area.areaTextures.append(tx)
    tx.magFilter = 2
    tx.minFilter = 2
    tx.mipFilter = 2
    tx.addressU = 2
    tx.addressV = 2
    tx.addressW = 1
    tx.transformBase = 4
    area.areaMaterials.append()
    shader = rot.GetInstance('tri:/Shader/nebula', '', None)
    if not shader:
        shader = rot.GetInstance('tri:/Shader/nebula', 'trinity.TriShader')
        shader.writeZ = 0
        shader.zFunc = 4
        shader.opaque = 1
        shader.cull = 2
        shader.zBias = 0
        pa = New('trinity.TriPass')
        pa.materialSource = 2
        pa.materialSourceIndex = 0
        pa.shading = 2
        pa.fill = 3
        pa.blendOp = 1
        pa.srcBlend = 10
        pa.dstBlend = 2
        pa.textureStage0 = New('trinity.TriTextureStage')
        shader.passes.append(pa)
        stg = pa.textureStage0
        stg.display = 1
        stg.name = 'Stage0 of neb_Pass'
        stg.colorOp = 3
        stg.colorArg1 = 1
        stg.colorArg2 = 2
        stg.alphaOp = 1
        stg.alphaArg1 = 0
        stg.alphaArg2 = 2
        stg.textureSource = 2
        stg.textureSourceIndex = 0
        stg.texCoordIndex = 0
        stg.texCoordIndexFlags = 65536
        stg.textureTransFormFlags = 2
    area.shader = shader
    scene.nebula = tf



def AddToListUnique(list, item):
    if item in list:
        return 
    list.append(item)



def FindParent(tf, list):
    for item in list:
        for child in item.children:
            if child == tf:
                return item

        return FindParent(tf, item.children)




def PrintTransformHierarchy(list, tab = '', prnRot = 0):
    for item in list:
        if prnRot:
            print tab,
            print item.name,
            print '    ',
            print rot.GetObjectPathName(item)
        else:
            print tab,
            print item.name
        PrintTransformHierarchy(item.children, tab + '    ')




