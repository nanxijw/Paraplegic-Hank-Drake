import log
import blue
import sys
import mathUtil
import util
import uicls
import re
from functools import wraps

def PythonizeResfile(path = 'res:/UI/Component/glassicon.blue'):
    import uiutil
    blueFile = blue.os.LoadObject(path)
    print 'blueFile',
    print blueFile
    PrintObject(blueFile, 'putparenthere')



def PrintObject(obj, parentname):
    import uiutil
    import uiconst
    if obj.__bluetype__ == 'triui.UITransform':
        print '%s = uicls.Transform(' % obj.name,
        print 'parent=%s,' % parentname,
        print 'pos=(%s,%s,%s,%s),' % (obj.left,
         obj.top,
         obj.width,
         obj.height),
        if obj.padLeft or obj.padTop or obj.padRight or obj.padBottom:
            print 'padding=(%s,%s,%s,%s),' % (obj.padLeft,
             obj.padTop,
             obj.padRight,
             obj.padBottom),
        if obj.opacity != 1.0:
            print 'opacity=%s,' % obj.opacity,
        if obj.name != '':
            print "name='%s'," % obj.name,
        print 'state=%s,' % GetDisplayAttribute('state', obj.state),
        if obj.clipChildren:
            print 'clipChildren=%s,' % obj.clipChildren,
        if obj.pickRadius:
            print 'pickRadius=%s,' % obj.pickRadius,
        print 'align=%s,' % GetDisplayAttribute('align', GetAlignX(obj.align, obj.GetAnchors(), obj.autoPos)),
        print ')'
        for each in obj.children:
            PrintObject(each, obj.name)

    elif obj.__bluetype__ == 'triui.UIContainer':
        print '%s = uicls.Container(' % obj.name,
        print 'parent=%s,' % parentname,
        print 'pos=(%s,%s,%s,%s),' % (obj.left,
         obj.top,
         obj.width,
         obj.height),
        if obj.padLeft or obj.padTop or obj.padRight or obj.padBottom:
            print 'padding=(%s,%s,%s,%s),' % (obj.padLeft,
             obj.padTop,
             obj.padRight,
             obj.padBottom),
        if obj.opacity != 1.0:
            print 'opacity=%s,' % obj.opacity,
        if obj.name != '':
            print "name='%s'," % obj.name,
        print 'state=%s,' % GetDisplayAttribute('state', obj.state),
        if obj.clipChildren:
            print 'clipChildren=%s,' % obj.clipChildren,
        if obj.pickRadius:
            print 'pickRadius=%s,' % obj.pickRadius,
        print 'align=%s,' % GetDisplayAttribute('align', GetAlignX(obj.align, obj.GetAnchors(), obj.autoPos)),
        print ')'
        for each in obj.children:
            PrintObject(each, obj.name)

    elif obj.__bluetype__ == 'triui.UISprite':
        print '%s = uicls.Sprite(' % obj.name,
        print 'parent=%s,' % parentname,
        print 'pos=(%s,%s,%s,%s),' % (obj.left,
         obj.top,
         obj.width,
         obj.height),
        if obj.padLeft or obj.padTop or obj.padRight or obj.padBottom:
            print 'padding=(%s,%s,%s,%s),' % (obj.padLeft,
             obj.padTop,
             obj.padRight,
             obj.padBottom),
        if obj.name != '':
            print "name='%s'," % obj.name,
        print 'state=%s,' % GetDisplayAttribute('state', obj.state),
        if obj.noScale:
            print 'noScale=%s,' % obj.noScale,
        if obj.rectLeft:
            print 'rectLeft=%s,' % obj.rectLeft,
        if obj.rectTop:
            print 'rectTop=%s,' % obj.rectTop,
        if obj.rectWidth:
            print 'rectWidth=%s,' % obj.rectWidth,
        if obj.rectHeight:
            print 'rectHeight=%s,' % obj.rectHeight,
        if obj.texture:
            print "texturePath='%s'," % obj.texture.pixels,
        if obj.color:
            print 'color=(%s,%s,%s,%s),' % (obj.color.r,
             obj.color.g,
             obj.color.b,
             obj.color.a),
        print 'align=%s,' % GetDisplayAttribute('align', GetAlignX(obj.align, obj.GetAnchors(), obj.autoPos)),
        print ')'
        if obj.tripass:
            print 'MISSING TRIPASS'
    elif obj.__bluetype__ == 'triui.UIFrame':
        print '%s = uicls.Frame(' % obj.name,
        print 'parent=%s,' % parentname,
        print 'pos=(%s,%s,%s,%s),' % (obj.left,
         obj.top,
         obj.width,
         obj.height),
        if obj.padLeft or obj.padTop or obj.padRight or obj.padBottom:
            print 'padding=(%s,%s,%s,%s),' % (obj.padLeft,
             obj.padTop,
             obj.padRight,
             obj.padBottom),
        if obj.name != '':
            print "name='%s'," % obj.name,
        print 'texturePath=%s' % obj.texture.pixels,
        print 'cornerSize=%s,' % obj.cornerSize,
        if obj.rectLeft:
            print 'rectLeft=%s,' % obj.rectLeft,
        if obj.rectTop:
            print 'rectTop=%s,' % obj.rectTop,
        if obj.rectWidth:
            print 'rectWidth=%s,' % obj.rectWidth,
        if obj.rectHeight:
            print 'rectHeight=%s,' % obj.rectHeight,
        print 'state=%s,' % GetDisplayAttribute('state', obj.state),
        if obj.color:
            print 'color=(%s,%s,%s,%s),' % (obj.color.r,
             obj.color.g,
             obj.color.b,
             obj.color.a),
        print 'align=%s,' % GetDisplayAttribute('align', GetAlignX(obj.align, obj.GetAnchors(), obj.autoPos)),
        print ')'
    elif obj.__bluetype__ == 'triui.UIWindow':
        if len(obj.children):
            for each in obj.children:
                PrintObject(each, obj.name)

        else:
            print 'UIWindow as Sprite'
            if obj.control.model.areas[0].areaMaterials:
                material = obj.control.model.areas[0].areaMaterials[0]
            else:
                material = None
            if obj.control.model.areas[0].areaTextures:
                texture = obj.control.model.areas[0].areaTextures[0]
            else:
                texture = None
            shader = obj.control.model.areas[0].shader
            align = GetAlignX(obj.align, obj.anchors, PosToAutopos(obj.position))
            print '%s = uicls.Sprite(' % obj.name,
            print 'parent=%s,' % parentname,
            if obj.name != '':
                print "name='%s'," % obj.name,
            if align == uiconst.TOALL:
                print 'padding=(%s,%s,%s,%s),' % (obj.left,
                 obj.top,
                 obj.width,
                 obj.height),
            print 'align=%s,' % GetDisplayAttribute('align', align),
            print 'state=%s,' % GetDisplayAttribute('state', obj.state),
            if texture:
                print "texturePath='%s'," % texture.pixels,
                print 'rectLeft=%s,' % int(texture.translation.x * texture.pixelBuffer.width),
                print 'rectTop=%s,' % int(texture.translation.y * texture.pixelBuffer.height),
                print 'rectWidth=%s,' % int(texture.scaling.x * texture.pixelBuffer.width),
                print 'rectHeight=%s,' % int(texture.scaling.y * texture.pixelBuffer.height),
            if material:
                print 'color=(%s,%s,%s,%s),' % (material.emissive.r,
                 material.emissive.g,
                 material.emissive.b,
                 material.emissive.a),
            print ')'
            if obj.control.model.areas[0].shader and obj.control.model.areas[0].shader.passes:
                print 'MISSING TRIPASS'
    else:
        print 'Missing handling for bluetype',
        print obj.__bluetype__



def GetAlignX(align = 0, anchor = 0, autoPos = 0):
    import uiconst
    alignmentMappings = {(uiconst.UI_ALNONE, 0, 0): uiconst.TOPLEFT,
     (uiconst.UI_ALNONE, uiconst.UI_ANCHTOP, 0): uiconst.TOPLEFT,
     (uiconst.UI_ALNONE, uiconst.UI_ANCHTOP | uiconst.UI_ANCHRIGHT, 0): uiconst.TOPRIGHT,
     (uiconst.UI_ALABSOLUTE, 0, 0): uiconst.ABSOLUTE,
     (uiconst.UI_ALNONE, uiconst.UI_ANCHRIGHT, 0): uiconst.TOPRIGHT,
     (uiconst.UI_ALNONE, uiconst.UI_ANCHBOTTOM, 0): uiconst.BOTTOMLEFT,
     (uiconst.UI_ALNONE, uiconst.UI_ANCHBOTTOM | uiconst.UI_ANCHLEFT, 0): uiconst.BOTTOMLEFT,
     (uiconst.UI_ALNONE, uiconst.UI_ANCHBOTTOM | uiconst.UI_ANCHRIGHT, 0): uiconst.BOTTOMRIGHT,
     (uiconst.UI_ALNONE, uiconst.UI_ANCHLEFT, 0): uiconst.TOPLEFT,
     (uiconst.UI_ALLEFT, 0, 0): uiconst.TOLEFT,
     (uiconst.UI_ALTOP, 0, 0): uiconst.TOTOP,
     (uiconst.UI_ALBOTTOM, 0, 0): uiconst.TOBOTTOM,
     (uiconst.UI_ALRIGHT, 0, 0): uiconst.TORIGHT,
     (uiconst.UI_ALCLIENT, 0, 0): uiconst.TOALL,
     (uiconst.UI_ALNONE, 0, uiconst.AUTOPOSYCENTER): uiconst.CENTERLEFT,
     (uiconst.UI_ALNONE, uiconst.UI_ANCHRIGHT, uiconst.AUTOPOSYCENTER): uiconst.CENTERRIGHT,
     (uiconst.UI_ALNONE, 0, uiconst.AUTOPOSXCENTER): uiconst.CENTERTOP,
     (uiconst.UI_ALNONE, uiconst.UI_ANCHBOTTOM, uiconst.AUTOPOSXCENTER): uiconst.CENTERBOTTOM,
     (uiconst.UI_ALNONE, 0, uiconst.AUTOPOSCENTER): uiconst.CENTER}
    alignmentDominators = [uiconst.UI_ALCLIENT,
     uiconst.UI_ALLEFT,
     uiconst.UI_ALTOP,
     uiconst.UI_ALBOTTOM,
     uiconst.UI_ALRIGHT,
     uiconst.UI_ALABSOLUTE]
    if align >= uiconst.ABSOLUTE:
        return align
    if align is None:
        align = 0
    if anchor is None:
        anchor = 0
    if autoPos is None:
        autoPos = 0
    if align in alignmentDominators:
        anchor = autoPos = 0
    coreAlign = alignmentMappings.get((align, anchor, autoPos), None)
    if coreAlign is None:
        return GetAlignX(align, 0, autoPos)
    return coreAlign


UI_POSCENTER = 2
UI_POSCENTER2 = 3
UI_POSDEFAULT = 1
UI_POSDESIGNED = 0

def PosToAutopos(position):
    import uiconst
    if position in (UI_POSCENTER, UI_POSCENTER2):
        return uiconst.AUTOPOSCENTER
    return uiconst.AUTOPOSNONE



def GetDisplayAttribute(attributeName, attributeValue):
    import uiconst

    def FormatState(attributeValue):
        for stateName in ('UI_NORMAL', 'UI_DISABLED', 'UI_HIDDEN', 'UI_PICKCHILDREN'):
            stateConst = getattr(uiconst, stateName, None)
            if stateConst == attributeValue:
                return 'uiconst.' + stateName

        return attributeValue



    def FormatAlign(attributeValue):
        for stateName in ('ABSOLUTE', 'RELATIVE', 'TOPLEFT', 'TOPRIGHT', 'BOTTOMLEFT', 'BOTTOMRIGHT', 'TOLEFT', 'TOTOP', 'TOBOTTOM', 'TORIGHT', 'TOALL', 'CENTERLEFT', 'CENTERRIGHT', 'CENTERTOP', 'CENTERBOTTOM', 'CENTER'):
            stateConst = getattr(uiconst, stateName, None)
            if stateConst == attributeValue:
                return 'uiconst.' + stateName

        return attributeValue


    if attributeName == 'state':
        attributeValue = FormatState(attributeValue)
    elif attributeName == 'align':
        attributeValue = FormatAlign(attributeValue)
    elif isinstance(attributeValue, basestring):
        attributeValue = '"' + attributeValue + '"'
    return attributeValue



def CropImage():
    ends = True
    import os
    import blue
    import trinity
    from util import ResFile
    sourceRoot = 'C:/Documents and Settings/Fridrik/Desktop/Incarna/bmp126'
    textures = os.listdir(sourceRoot)
    groups = {}
    lastGroupID = None
    for each in textures:
        if not each.endswith('.bmp'):
            continue
        cl = each.lstrip('_').lstrip('0').rstrip('.bmp')
        spl = cl.split('_')
        groupID = spl[0]
        if spl[0] not in groups:
            groups[groupID] = []
        groups[groupID].append((int(spl[-1]), each))
        lastGroupID = groupID

    textureSize = 128
    srcCol = trinity.TriColor()
    for (groupID, subs,) in groups.iteritems():
        print 'colorAmount',
        print groupID,
        print [ bitNo for (bitNo, bitTexture,) in subs ]
        continue
        for (bitNo, bitTexture,) in subs:
            iconSurface = trinity.device.CreateOffscreenPlainSurface(textureSize, textureSize, trinity.TRIFMT_A8R8G8B8, trinity.TRIPOOL_SYSTEMMEM)
            iconSurface.LoadSurfaceFromFile('C:\\Documents and Settings/Fridrik/Desktop/Incarna/bmps128Ends/' + bitTexture)
            iconSurface.LockBuffer()
            leftX = textureSize
            rightX = 0
            topY = textureSize
            bottomY = 0
            for x in xrange(textureSize):
                for y in xrange(textureSize):
                    srcCol.FromInt(iconSurface.GetPixel(x, y))
                    alpha = srcCol.a
                    if alpha:
                        leftX = min(x, leftX)
                        rightX = max(x, rightX)
                        topY = min(y, topY)
                        bottomY = max(y, bottomY)


            iconSurface.FlushBuffer()
            margin = 3
            leftX = max(0, leftX - margin)
            rightX = min(textureSize, rightX + margin)
            topY = max(0, topY - margin)
            bottomY = min(textureSize, bottomY + margin)
            rr = trinity.TriRect(leftX, topY, rightX, bottomY)
            iconID = '%s_%sEnd__%s_%s_%s_%s.dds' % (groupID,
             bitNo,
             leftX,
             topY,
             rightX,
             bottomY)
            iconSurface.SaveSurfaceToFile('C:/Documents and Settings/Fridrik/Desktop/Incarna/bmps128Ends/' + iconID, trinity.TRIIFF_DDS, rr)
            print 'Saving',
            print iconID

        blue.pyos.synchro.Yield()

    print 'Cropping Done'



def GetBuffersize(size):
    if size <= 8:
        return 8
    if size <= 16:
        return 16
    if size <= 32:
        return 32
    if size <= 64:
        return 64
    if size <= 128:
        return 128
    if size <= 256:
        return 256
    if size <= 512:
        return 512
    if size <= 1024:
        return 1024
    if size <= 2048:
        return 2048
    return 128



def StringColorToHex(color):
    colors = {'Black': '0xff000000',
     'Green': '0xff008000',
     'Silver': '0xffC0C0C0',
     'Lime': '0xff00FF00',
     'Gray': '0xff808080',
     'Grey': '0xff808080',
     'Olive': '0xff808000',
     'White': '0xffFFFFFF',
     'Yellow': '0xffFFFF00',
     'Maroon': '0xff800000',
     'Navy': '0xff000080',
     'Red': '0xffFF0000',
     'Blue': '0xff0000FF',
     'Purple': '0xff800080',
     'Teal': '0xff008080',
     'Fuchsia': '0xffFF00FF',
     'Aqua': '0xff00FFFF',
     'Orange': '0xffFF8000',
     'Transparent': '0x00000000',
     'Lightred': '0xffcc3333',
     'Lightblue': '0xff7777ff',
     'Lightgreen': '0xff80ff80'}
    return colors.get(color.capitalize(), None)



def Sort(lst):
    lst.sort(lambda x, y: cmp(str(x).upper(), str(y).upper()))
    return lst



def SortListOfTuples(lst, reverse = 0):
    lst = sorted(lst, reverse=reverse, key=lambda data: data[0])
    return [ item[1] for item in lst ]



def SortByAttribute(lst, attrname = 'name', idx = None, reverse = 0):
    newlst = []
    for item in lst:
        if idx is None:
            newlst.append((getattr(item, attrname, None), item))
        else:
            newlst.append((getattr(item[idx], attrname, None), item))

    ret = SortListOfTuples(newlst, reverse)
    return ret



def SmartCompare(x, y, sortOrder):
    for (column, direction,) in sortOrder:
        if direction == 1:
            if x[0][column] > y[0][column]:
                return 1
            if x[0][column] < y[0][column]:
                return -1
        else:
            if x[0][column] < y[0][column]:
                return 1
            if x[0][column] > y[0][column]:
                return -1

    return 0



def Update(*args):
    uicore.uilib.RecalcWindows()



def FindChild(fromParent, *names):
    return fromParent.FindChild(*names)



def GetChild(parent, *names):
    return parent.GetChild(*names)



def FindChildByClass(parent, classes = (), searchIn = [], withAttributes = []):
    children = []
    for each in searchIn:
        for w in parent.Find(each):
            if isinstance(w, classes):
                if withAttributes:
                    for attrTuple in withAttributes:
                        (attr, value,) = attrTuple
                        if getattr(w, attr, None) == value:
                            children.append(w)

                else:
                    children.append(w)


    return children



def SetOrder(child, idx = 0):
    child.SetOrder(idx)



def GetIndex(item):
    if item.parent:
        return item.parent.children.index(item)
    return 0



def Flush(parent):
    parent.Flush()



def FlushList(lst):
    for each in lst[:]:
        if each is not None and not getattr(each, 'destroyed', 0):
            each.Close()

    del lst[:]



def GetWindowAbove(item):
    if item == uicore.desktop:
        return 
    import uicls
    if uicore.registry.IsWindow(item) and not getattr(item, 'isImplanted', False):
        return item
    if item.parent and not item.parent.destroyed:
        return GetWindowAbove(item.parent)



def GetBrowser(item):
    if item == uicore.desktop:
        return 
    if getattr(item, 'IsBrowser', None):
        return item
    import uicls
    if isinstance(item, uicls.EditCore):
        return item
    if item.parent:
        return GetBrowser(item.parent)



def GetAttrs(obj, *names):
    for name in names:
        obj = getattr(obj, name, None)
        if obj is None:
            return 

    return obj



def Transplant(wnd, newParent, idx = None):
    if wnd is None or wnd.destroyed or newParent is None or newParent.destroyed:
        return 
    if idx in (-1, None):
        idx = len(newParent.children)
    wnd.SetParent(newParent, idx)



def IsClickable(wnd):
    if not hasattr(wnd, 'state') or not hasattr(wnd, 'parent'):
        return False
    import uiconst
    if wnd.state not in (uiconst.UI_NORMAL, uiconst.UI_PICKCHILDREN):
        return False
    dad = wnd.parent
    if dad == uicore.desktop:
        return True
    return IsClickable(dad)



def IsUnder(child, ancestor_maybe, retfailed = False):
    dad = child.parent
    if not dad:
        if retfailed:
            return child
        return False
    if dad == ancestor_maybe:
        return True
    return IsUnder(dad, ancestor_maybe, retfailed)



def IsVisible(item):
    if not hasattr(item, 'state') or not hasattr(item, 'parent'):
        return 0
    import uiconst
    if item.state == uiconst.UI_HIDDEN:
        return 0
    dad = item.parent
    if not dad:
        return 0
    if dad.state == uiconst.UI_HIDDEN:
        return 0
    if dad == uicore.desktop:
        return 1
    return IsVisible(dad)



def IsVisible_RectCheck(item, rect = None):
    (il, it, iw, ih,) = item.GetAbsolute()
    if rect is None:
        import trinity
        rect = trinity.TriRect(il, it, il + iw, it + ih)
        if item.parent is None:
            return False
        return IsVisible_RectCheck(item.parent, rect)
    rect.left = max(rect.left, il)
    rect.top = max(rect.top, it)
    rect.right = min(rect.right, il + iw)
    rect.bottom = min(rect.bottom, it + ih)
    if rect.left >= rect.right or rect.top >= rect.bottom:
        return False
    if item.parent is uicore.desktop:
        return True
    if item.parent is None:
        return False
    return IsVisible_RectCheck(item.parent, rect)



def MapIcon(sprite, iconPath, ignoreSize = 0):
    if hasattr(sprite, 'LoadIcon'):
        return sprite.LoadIcon(iconPath, ignoreSize)
    print 'Someone load icon to non icon class',
    print sprite,
    print iconPath
    return uicls.Icon.LoadIcon(sprite, iconPath, ignoreSize)



def ConvertDecimal(qty, fromChar, toChar, numDecimals = None):
    import types
    ret = qty
    if type(ret) in [types.IntType, types.FloatType, types.LongType]:
        if numDecimals is not None:
            ret = '%.*f' % (numDecimals, qty)
        else:
            ret = repr(qty)
    ret = ret.replace(fromChar, toChar)
    return ret



def GetClipboardData():
    import blue
    try:
        return blue.win32.GetClipboardUnicode()
    except blue.error:
        return ''



def GetTrace(item, trace = '', div = '/'):
    trace = div + item.name + trace
    if getattr(item, 'parent', None) is None:
        return trace
    return GetTrace(item.parent, trace, div)



def PrepareDrag_Standard(dragContainer, dragSource, *args):
    uicls.Frame(parent=dragContainer)
    return (0, 0)



def ParseHTMLColor(colorstr, asTuple = 0, error = 0):
    colors = {'Black': '0x000000',
     'Green': '0x008000',
     'Silver': '0xC0C0C0',
     'Lime': '0x00FF00',
     'Gray': '0x808080',
     'Grey': '0x808080',
     'Olive': '0x808000',
     'White': '0xFFFFFF',
     'Yellow': '0xFFFF00',
     'Maroon': '0x800000',
     'Navy': '0x000080',
     'Red': '0xFF0000',
     'Blue': '0x0000FF',
     'Purple': '0x800080',
     'Teal': '0x008080',
     'Fuchsia': '0xFF00FF',
     'Aqua': '0x00FFFF',
     'Transparent': '0x00000000'}
    try:
        colorstr = colors.get(colorstr.capitalize(), colorstr).lower()
    except:
        sys.exc_clear()
        return colorstr
    if colorstr.startswith('#'):
        colorstr = colorstr.replace('#', '0x')
    (r, g, b, a,) = (0.0, 255.0, 0.0, 255.0)
    if colorstr.startswith('0x'):
        try:
            if len(colorstr) == 8:
                r = eval('0x' + colorstr[2:4])
                g = eval('0x' + colorstr[4:6])
                b = eval('0x' + colorstr[6:8])
            elif len(colorstr) == 10:
                a = eval('0x' + colorstr[2:4])
                r = eval('0x' + colorstr[4:6])
                g = eval('0x' + colorstr[6:8])
                b = eval('0x' + colorstr[8:10])
            else:
                log.LogWarn('Invalid color string, has to be in form of 0xffffff or 0xffffffff (with alpha). 0x can be replaced with # (%s)' % colorstr)
                if error:
                    return 
        except:
            log.LogWarn('Invalid color string, has to be in form of 0xffffff or 0xffffffff (with alpha). 0x can be replaced with # (%s)' % colorstr)
            if error:
                return 
    else:
        log.LogError('Unknown color (' + colorstr + '), I only know: ' + strx(', '.join(colors.keys())))
        if error:
            return 
    col = (r / 255.0,
     g / 255.0,
     b / 255.0,
     a / 255.0)
    if asTuple:
        return col
    import trinity
    return trinity.TriColor(*col)



def GetFormWindow(caption = None, buttons = None, okFunc = None, windowClass = None):
    import uicls
    import uiconst
    windowClass = windowClass or uicls.Window
    wnd = windowClass(parent=uicore.layer.main, width=256, height=128)
    if caption is not None:
        wnd.SetCaption(caption)
    wnd.confirmCheckControls = []
    wnd.SetButtons(buttons or uiconst.OKCANCEL, okFunc=ConfirmFormWindow)
    return wnd



def AddFormControl(wnd, control, key, retval = None, required = False, errorcheck = None):
    wnd.confirmCheckControls.append((control,
     key,
     retval,
     required,
     errorcheck))



def AddFormErrorCheck(wnd, errorCheck):
    wnd.errorCheck = errorCheck



def ConfirmFormWindow(sender, *args):
    import uiconst
    import uicls
    uicore.registry.SetFocus(uicore.desktop)
    if sender is None:
        if getattr(uicore.registry.GetFocus(), 'stopconfirm', 0):
            return 
    wnd = GetWindowAbove(sender)
    result = {}
    for each in getattr(wnd, 'confirmCheckControls', []):
        (control, key, retval, required, check,) = each
        checkValue = control.GetValue()
        if required:
            if checkValue is None or checkValue == '':
                uicore.Message('MissingRequiredField', {'fieldname': key})
                return 
        if check:
            hint = check(checkValue)
            if hint == 'silenterror':
                return 
            if hint:
                uicore.Message('CustomInfo', {'info': hint})
                return 
        if type(retval) == dict:
            result.update(retval)
            continue
        result[key] = checkValue

    if not result:
        return 
    formErrorCheck = getattr(wnd, 'errorCheck', None)
    if formErrorCheck:
        if formErrorCheck:
            hint = formErrorCheck(result)
            if hint == 'silenterror':
                return 
            if hint:
                uicore.Message('CustomInfo', {'info': hint})
                return 
    wnd.result = result
    if uicore.registry.GetModalWindow() == wnd:
        wnd.SetModalResult(uiconst.ID_OK)
    else:
        if wnd.sr.queue:
            wnd.sr.queue.put(result)
        wnd.SetModalResult(uiconst.ID_OK)
        return result



def AskAmount(caption = None, question = None, setvalue = '', intRange = None, floatRange = None):
    import uiconst
    import uicls
    if caption is None:
        caption = 'How much?'
    if question is None:
        question = 'How much?'
    wnd = GetFormWindow(caption)
    if question:
        uicls.Label(parent=wnd.sr.content, text=question, align=uiconst.TOTOP, pos=(0, 0, 0, 0))
    edit = uicls.SinglelineEdit(parent=wnd.sr.content, ints=intRange, floats=floatRange, setvalue=setvalue)
    AddFormControl(wnd, edit, 'amount', retval=None, required=True, errorcheck=None)
    if wnd.ShowModal() == uiconst.ID_OK:
        return wnd.result



def AskName(caption = None, label = None, setvalue = '', maxLength = None, passwordChar = None, validator = None):
    import uiconst
    import uicls
    import localization
    if caption is None:
        caption = localization.GetByLabel('UI/Common/Name/TypeInName')
    if label is None:
        label = localization.GetByLabel('UI/Common/Name/TypeInName')
    wnd = GetFormWindow(caption)
    if label:
        uicls.Label(parent=wnd.sr.content, text=label, align=uiconst.TOTOP, pos=(0, 0, 0, 0))
    edit = uicls.SinglelineEdit(parent=wnd.sr.content, maxLength=maxLength, setvalue=setvalue)
    AddFormControl(wnd, edit, 'name', retval=None, required=True, errorcheck=validator or NamePopupErrorCheck)
    if wnd.ShowModal() == uiconst.ID_OK:
        return wnd.result



def AskChoice(caption = '', question = '', choices = [], modal = False):
    import uiconst
    import uicls
    wnd = GetFormWindow(caption)
    if question:
        label = uicls.Label(parent=wnd.sr.content, text=question, align=uiconst.TOTOP, pos=(0, 0, 0, 0))
        wnd.SetMinSize((label.width + 20, wnd.GetMinHeight()))
    combo = uicls.Combo(parent=wnd.sr.content, options=choices, align=uiconst.TOTOP)
    AddFormControl(wnd, combo, 'choice', retval=None, required=True, errorcheck=None)
    if modal:
        if wnd.ShowModal() == uiconst.ID_OK:
            return wnd.result
    elif wnd.ShowDialog() == uiconst.ID_OK:
        return wnd.result



def NamePopupErrorCheck(name):
    if not len(name) or len(name) and len(name.strip()) < 1:
        return localization.GetByLabel('UI/Common/Name/PleaseTypeSomething')
    return ''



def __CopyWithAlpha(srcSurface, dstSurface, srcSize, dstSize):
    srcSurface.LockBuffer()
    dstSurface.LockBuffer()
    import trinity
    tmpCol = trinity.TriColor()
    bpCol = trinity.TriColor()
    srcCol = trinity.TriColor()
    dstCol = trinity.TriColor()
    factor = srcSize / dstSize
    factor2 = factor * factor
    for x in xrange(dstSize):
        for y in xrange(dstSize):
            r = g = b = a = 0.0
            for xi in xrange(factor):
                for yi in xrange(factor):
                    srcCol.FromInt(srcSurface.GetPixel(factor * x + xi, factor * y + yi))
                    r += srcCol.r
                    g += srcCol.g
                    b += srcCol.b
                    a += srcCol.a


            if a:
                a /= factor2
                r /= factor2
                g /= factor2
                b /= factor2
                r *= a
                g *= a
                b *= a
                dstCol.FromInt(dstSurface.GetPixel(x, y))
                dstCol.Scale(1.0 - a)
                dstCol.r = min(1.0, r + dstCol.r)
                dstCol.g = min(1.0, g + dstCol.g)
                dstCol.b = min(1.0, b + dstCol.b)
                dstCol.a = min(1.0, a + dstCol.a)
                dstSurface.SetPixel(x, y, dstCol.AsInt())


    srcSurface.FlushBuffer()
    dstSurface.FlushBuffer()



def RenderIconSheets(iconRoot = 'res:/UI/Texture/Icons', bgcolor = (0.5, 0.5, 0.5), putInto = 'CCPIcons'):
    import os
    import blue
    import trinity
    from util import ResFile
    mydocs = blue.win32.SHGetFolderPath(blue.win32.CSIDL_PERSONAL)
    destRoot = mydocs + '\\' + putInto
    try:
        os.makedirs(destRoot)
    except OSError as e:
        pass
    fullIconRoot = iconRoot.replace('res:/', blue.os.ResolvePath(u'res:/'))
    textures = os.listdir(fullIconRoot)
    dev = trinity.device
    iconSurface = dev.CreateOffscreenPlainSurface(256, 256, trinity.TRIFMT_A8R8G8B8, trinity.TRIPOOL_SYSTEMMEM)
    col = trinity.TriColor()
    col.SetRGB(*bgcolor)
    html = '<htm><body>'
    for textureName in textures:
        if not textureName.endswith('.dds'):
            continue
        namesplit = textureName[:-4].split('_')
        if len(namesplit) < 1:
            continue
        try:
            sheetNo = int(namesplit[0])
            iconSize = int(namesplit[1])
        except:
            continue
        resPath = iconRoot + '/' + textureName
        iconSurface.LoadSurfaceFromFile(ResFile(resPath))
        sur = dev.CreateRenderTarget(256, 256, trinity.TRIFMT_A8R8G8B8, 0, 0, 1)
        surrect = trinity.TriRect(0, 0, 256, 256)
        dev.ColorFill(sur, surrect, col)
        sur.FlushBuffer()
        __CopyWithAlpha(iconSurface, sur, 256, 256)
        savesur = dev.CreateOffscreenPlainSurface(256, 256, trinity.TRIFMT_A8R8G8B8, trinity.TRIPOOL_SYSTEMMEM)
        sur.CopySurfaceTo(savesur)
        left = 0
        top = 0
        html += '<table cellspacing=4>'
        for i in xrange((256 / iconSize) ** 2):
            i += 1
            rr = trinity.TriRect(left, top, left + iconSize, top + iconSize)
            iconID = 'ui_%s_%s_%s.jpg' % (sheetNo, iconSize, i)
            savesur.SaveSurfaceToFile(destRoot + '/' + iconID, trinity.TRIIFF_JPG, rr)
            if left == 0:
                html += '<tr height=%s>' % iconSize
            magicStr = 'ui_%s_%s_%s' % (sheetNo, iconSize, i)
            html += '<td><img src=%s></td>' % iconID
            html += '<td><font size=1>%s<br>Col: %s<br>Row: %s<br>Size: %s<br>Magic: %s</td>' % (resPath,
             left / iconSize,
             top / iconSize,
             iconSize,
             magicStr)
            left += iconSize
            if left >= 256:
                left = 0
                top += iconSize
                html += '</tr>'

        html += '</table><br><br>'

    html += '</body></htm>'
    htmlfilePath = destRoot + '/index.htm'
    fout = file(htmlfilePath, 'wb')
    fout.write(html)
    fout.close()



def BreakupUICoreIcons(iconRoot = 'res:/UICore/Texture/Icons'):
    import os
    import blue
    import trinity
    from util import ResFile
    destRoot = blue.os.ResolvePathForWriting(u'res:/UICore/Texture/Icons')
    try:
        os.makedirs(destRoot)
    except OSError as e:
        pass
    fullIconRoot = iconRoot.replace('res:/', blue.os.ResolvePath(u'res:/'))
    textures = os.listdir(fullIconRoot)
    dev = trinity.device
    iconSurface = dev.CreateOffscreenPlainSurface(256, 256, trinity.TRIFMT_A8R8G8B8, trinity.TRIPOOL_SYSTEMMEM)
    print 'textures',
    print fullIconRoot,
    print textures
    iconNo = 1
    for textureName in textures:
        if not textureName.endswith('.dds'):
            continue
        print 'Doing',
        print textureName
        namesplit = textureName[:-4].split('_')
        if len(namesplit) < 1:
            continue
        try:
            sheetNo = int(namesplit[0])
            iconSize = int(namesplit[1])
        except:
            continue
        resPath = iconRoot + '/' + textureName
        iconSurface.LoadSurfaceFromFile(ResFile(resPath))
        savesur = dev.CreateOffscreenPlainSurface(256, 256, trinity.TRIFMT_A8R8G8B8, trinity.TRIPOOL_SYSTEMMEM)
        iconSurface.CopySurfaceTo(savesur)
        left = 0
        top = 0
        for i in xrange((256 / iconSize) ** 2):
            i += 1
            rr = trinity.TriRect(left, top, left + iconSize, top + iconSize)
            iconID = '%s_%s_%s' % (sheetNo, iconSize, i)
            savesur.SaveSurfaceToFile(destRoot + '/' + iconID + '.png', trinity.TRIIFF_PNG, rr)
            left += iconSize
            if left >= 256:
                left = 0
                top += iconSize
            iconNo += 1
            saved = trinity.device.CreateOffscreenPlainSurface(iconSize, iconSize, trinity.TRIFMT_A8R8G8B8, trinity.TRIPOOL_SYSTEMMEM)
            saved.LoadSurfaceFromFile(ResFile(destRoot + '/' + iconID + '.png'))
            saved.LockBuffer()
            srcCol = trinity.TriColor()
            foundAlpha = False
            for x in xrange(iconSize):
                for y in xrange(iconSize):
                    srcCol.FromInt(saved.GetPixel(x, y))
                    alpha = srcCol.a
                    if alpha != 0.0:
                        foundAlpha = True
                        break

                if foundAlpha:
                    break

            saved.FlushBuffer()
            if not foundAlpha:
                print 'Deleting...',
                print destRoot + '/' + iconID + '.png'
                os.remove(destRoot + '/' + iconID + '.png')





def BreakupEveIcons():
    import os
    import blue
    import trinity
    import uix
    from util import ResFile
    paths = []

    def CompileIcons(addTo):
        iconRoot = 'res:/UI/Texture/Icons'
        fullIconRoot = iconRoot.replace('res:/', blue.os.ResolvePath(u'res:/'))
        textures = os.listdir(fullIconRoot)
        destRoot = iconRoot.replace('res:/', blue.os.ResolvePath(u'res:/'))
        iconPaths = []
        for textureName in textures:
            if not textureName.endswith('.dds') and not textureName.startswith('icons'):
                continue
            namesplit = textureName[:-4].split('_')
            if len(namesplit) < 1:
                continue
            splits = textureName[5:-4].split('.')
            iconSize = uix.GetIconSize(splits[0])
            sheetNo = int(splits[0])
            oldstyleID = '%s_%s_%%s' % (sheetNo, iconSize)
            if textureName.find('.ZH') != -1:
                oldstyleID += '.ZH'
            resPath = iconRoot + '/' + textureName
            destPath = destRoot + '/' + oldstyleID
            iconPaths.append((resPath, destPath, iconSize))

        addTo.append(iconPaths)


    CompileIcons(paths)

    def CompileAllianceLogos(addTo):
        root = 'res:/UI/Texture/Alliance'
        fullRoot = root.replace('res:/', blue.os.ResolvePath(u'res:/'))
        textures = os.listdir(fullRoot)
        destRoot = root.replace('res:/', blue.os.ResolvePath(u'res:/'))
        iconPaths = []
        for textureName in textures:
            if not textureName.endswith('.dds') and not textureName.startswith('alliance'):
                continue
            iconSize = 128
            sheetNo = int(textureName.replace('alliance', '').replace('.dds', ''))
            oldstyleID = '%s_%s_%%s' % (sheetNo, iconSize)
            if textureName.find('.ZH') != -1:
                oldstyleID += '.ZH'
            resPath = root + '/' + textureName
            destPath = destRoot + '/' + oldstyleID
            iconPaths.append((resPath, destPath, iconSize))

        addTo.append(iconPaths)



    def CompileCorpLogos(addTo):
        root = 'res:/UI/Texture/Corps'
        fullRoot = root.replace('res:/', blue.os.ResolvePath(u'res:/'))
        textures = os.listdir(fullRoot)
        destRoot = root.replace('res:/', blue.os.ResolvePath(u'res:/'))
        iconPaths = []
        for textureName in textures:
            if not textureName.endswith('.dds') and not textureName.startswith('corps'):
                continue
            iconSize = 128
            sheetNo = int(textureName.replace('corps', '').replace('.dds', ''))
            oldstyleID = '%s_%s_%%s' % (sheetNo, iconSize)
            if textureName.find('.ZH') != -1:
                oldstyleID += '.ZH'
            resPath = root + '/' + textureName
            destPath = destRoot + '/' + oldstyleID
            iconPaths.append((resPath, destPath, iconSize))

        addTo.append(iconPaths)



    def CompileRibbons(addTo):
        root = 'res:/UI/Texture/Medals/Ribbons'
        fullRoot = root.replace('res:/', blue.os.ResolvePath(u'res:/'))
        textures = os.listdir(fullRoot)
        iconPaths = []
        for textureName in textures:
            if not textureName.endswith('.dds'):
                continue
            iconSize = 128
            sheetNo = int(textureName.replace('.dds', '')[-2:])
            raceName = textureName.replace('.dds', '')[:-2]
            oldstyleID = '%s_%s_%s_%%s' % (raceName, sheetNo, iconSize)
            if textureName.find('.ZH') != -1:
                oldstyleID += '.ZH'
            resPath = root + '/' + textureName
            destPath = root + '/' + oldstyleID
            iconPaths.append((resPath, destPath, iconSize))

        addTo.append(iconPaths)


    loadSurface = trinity.device.CreateOffscreenPlainSurface(256, 256, trinity.TRIFMT_A8R8G8B8, trinity.TRIPOOL_SYSTEMMEM)
    for iconGroup in paths:
        iconNo = 1
        for (resPath, destPath, iconSize,) in iconGroup:
            loadSurface.LoadSurfaceFromFile(ResFile(resPath))
            left = 0
            top = 0
            for i in xrange((256 / iconSize) ** 2):
                i += 1
                rr = trinity.TriRect(left, top, left + iconSize, top + iconSize)
                saved = loadSurface.SaveSurfaceToFile(destPath % i + '.png', trinity.TRIIFF_PNG, rr)
                left += iconSize
                if left >= 256:
                    left = 0
                    top += iconSize
                iconNo += 1
                blue.pyos.synchro.Yield()
                saved = trinity.device.CreateOffscreenPlainSurface(iconSize, iconSize, trinity.TRIFMT_A8R8G8B8, trinity.TRIPOOL_SYSTEMMEM)
                saved.LoadSurfaceFromFile(ResFile(destPath % i + '.png'))
                saved.LockBuffer()
                srcCol = trinity.TriColor()
                foundAlpha = False
                for x in xrange(iconSize):
                    for y in xrange(iconSize):
                        srcCol.FromInt(saved.GetPixel(x, y))
                        alpha = srcCol.a
                        if alpha != 0.0:
                            foundAlpha = True
                            break

                    if foundAlpha:
                        break

                saved.FlushBuffer()
                if not foundAlpha:
                    print 'Deleting...',
                    print destPath % i + '.png'
                    os.remove(destPath % i + '.png')






def ParanoidDecoMethod(fn, attrs):
    check = []
    if attrs is None:
        check = ['sr']
    else:
        check.extend(attrs)

    @wraps(fn)
    def deco(self, *args, **kw):
        if util.GetAttrs(self, *check) is None:
            return 
        if self.destroyed:
            return 
        return fn(self, *args, **kw)


    return deco



def NiceFilter(func, list):
    ret = []
    for x in list:
        if func(x):
            ret.append(x)
        blue.pyos.BeNice()

    return ret



def AutoExports(namespace, globals_):
    import types
    return dict([ ('%s.%s' % (namespace, name), val) for (name, val,) in globals_.iteritems() if not name.startswith('_') and not isinstance(val, types.ModuleType) if not hasattr(val, '__guid__') ])


exports = AutoExports('uiutil', locals())

