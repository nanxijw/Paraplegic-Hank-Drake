import cef
import log
import types
import util

def GetSpawnPatterns():
    return const.cef.PATTERN_NAMES.keys()



def GetSpawnPatternName(spawnPatternID):
    return const.cef.PATTERN_NAMES.get(spawnPatternID, 'UNKNOWN')



def GetComponentName(componentID):
    componentView = cef.BaseComponentView.GetComponentViewByID(componentID)
    if type(componentID) is str:
        return componentID
    if componentView is None:
        log.LogTraceback('UNKNOWN COMPONENT %s' % componentID)
        return 'UNKNOWN COMPONENT %s' % componentID
    return componentView.__COMPONENT_CODE_NAME__



def GetParentTypeString(parentType):
    if parentType == const.cef.PARENT_TYPEID:
        return 'Type'
    else:
        if parentType == const.cef.PARENT_GROUPID:
            return 'Group'
        if parentType == const.cef.PARENT_CATEGORYID:
            return 'Category'
        return 'UNKNOWN'



def GetIngredientInitialValue(initValueRow, tableName = const.cef.INGREDIENT_INITS_TABLE_FULL_NAME):
    if initValueRow.valueInt is not None:
        return initValueRow.valueInt
    else:
        if initValueRow.valueFloat is not None:
            return initValueRow.valueFloat
        if initValueRow.needsTranslation:
            return (initValueRow.valueString, tableName + '.valueString', initValueRow.dataID)
        return initValueRow.valueString



def GetDBInitValuesFromValue(value):
    if type(value) is types.IntType:
        return util.KeyVal(valueInt=value, valueFloat=None, valueString=None)
    if type(value) is types.FloatType:
        return util.KeyVal(valueInt=None, valueFloat=value, valueString=None)
    if type(value) is not types.StringType:
        try:
            value = str(value)
        except ValueError as e:
            return util.KeyVal(valueInt=None, valueFloat=None, valueString=None)
    try:
        valueInt = int(value)
    except ValueError as e:
        valueInt = None
    if valueInt is not None:
        valueFloat = None
    else:
        try:
            valueFloat = float(value)
        except ValueError as e:
            valueFloat = None
    if valueInt is not None or valueFloat is not None or value.strip() == '':
        value = None
    return util.KeyVal(valueInt=valueInt, valueFloat=valueFloat, valueString=value)


exports = util.AutoExports('entityCommon', locals())

