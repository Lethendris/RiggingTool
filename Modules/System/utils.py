from codecs import replace_errors

import maya.cmds as cmds


def findHighestTrailingNumber(names, baseName):
    highestValue = 0

    for name in names:
        if name.startswith(baseName):
            suffix = name[len(baseName):]
            if suffix.isdigit():
                highestValue = max(highestValue, int(suffix))

    return highestValue

def stripAllNamespaces(nodeName):
    """
        Splits the given node name into namespace and base name.

        Args:
            nodeName (str): The node name that may include a namespace.

        Returns:
            tuple or None: (namespace, baseName) if a namespace exists, otherwise None.
        """

    if ':' not in str(nodeName):
        return None

    namespace, _, baseName = str(nodeName).rpartition(':')
    return [namespace, baseName]


def stripLeadingNamespace(nodeName):
    """
    Splits a node name into namespace and base name.

    Args:
        nodeName (str): The full node name potentially with a namespace.

    Returns:
        list[str] or None: [namespace, baseName] if a namespace exists, otherwise None.
    """
    if ':' not in nodeName:
        return None

    namespace, _, baseName = nodeName.partition(':')
    return [namespace, baseName]


def basicStretchyIK(rootJoint, endJoint, container = None, lockMinimumLength = True, poleVectorObject = None, scaleCorrectionAttribute = None):
    """
    Creates a basic stretchy IK setup with optional pole vector and visibility controls.

    :param rootJoint: Name of the root joint in the IK chain.
    :param endJoint: Name of the end joint in the IK chain.
    :param container: Optional DG container to include all created nodes.
    :param lockMinimumLength: Reserved for stretch clamping.
    :param poleVectorObject: Optional object to use for pole vector control. If None, one will be created.
    :param scaleCorrectionAttribute: Reserved for scale compensation.
    :return: Dictionary with created nodes and constraints.
    """

    containedNodes = []

    totalOriginalLength = 0.0
    parent = rootJoint

    childJoints = []

    while True:
        children = cmds.listRelatives(parent, children = True)
        children = cmds.ls(children, type = 'joint')

        if not children:
            break

        child = children[0]
        childJoints.append(child)

        totalOriginalLength += cmds.getAttr(f'{child}.translateX')

        parent = child

        if child == endJoint:
            break


    # create RP IK on joint chain
    ikNodes = cmds.ikHandle(startJoint = rootJoint, endEffector = endJoint, solver = 'ikRPsolver',
                            name = f'{rootJoint}_ikHandle')
    ikNodes[1] = cmds.rename(ikNodes[1], f'{rootJoint}_ikEffector')

    ikEffector = ikNodes[1]
    ikHandle = ikNodes[0]

    cmds.setAttr(f'{ikHandle}.visibility', 0)
    containedNodes.extend(ikNodes)

    # create pole vector locator
    if not poleVectorObject:
        poleVectorObject = cmds.spaceLocator(name = f'{ikHandle}_poleVectorLocator')[0]

        cmds.xform(poleVectorObject, worldSpace = True, absolute = True,
                   translation = cmds.xform(rootJoint, query = True, worldSpace = True, translation = True))
        cmds.xform(poleVectorObject, worldSpace = True, relative = True, translation = (0.0, 1.0, 0.0))

        cmds.setAttr(f'{poleVectorObject}.visibility', 0)

    poleVectorConstraint = cmds.poleVectorConstraint(poleVectorObject, ikHandle)[0]
    containedNodes.append(poleVectorConstraint)

    # create root and end locators
    rootLocator = cmds.spaceLocator(name = f'{rootJoint}_rootPosLocator')[0]
    rootLocator_pointConstraint = \
        cmds.pointConstraint(rootJoint, rootLocator, maintainOffset = False, name = f'{rootLocator}_pointConstraint')[0]

    endLocator = cmds.spaceLocator(name = f'{endJoint}_endPosLocator')[0]
    cmds.xform(endLocator, worldSpace = True, absolute = True,
               translation = cmds.xform(ikHandle, query = True, worldSpace = True, translation = True))
    ikHandle_pointConstraint = \
        cmds.pointConstraint(endLocator, ikHandle, maintainOffset = False, name = f'{ikHandle}_pointConstraint')[0]

    containedNodes.extend([rootLocator, endLocator, rootLocator_pointConstraint, ikHandle_pointConstraint])

    cmds.setAttr(f'{rootLocator}.visibility', 0)
    cmds.setAttr(f'{endLocator}.visibility', 0)

    # distance between locators
    rootLocatorWithoutNamespace = stripAllNamespaces(rootLocator)[1]
    endLocatorWithoutNamespace = stripAllNamespaces(endLocator)[1]
    moduleNamespace = stripAllNamespaces(rootJoint)[0]

    distNode = cmds.createNode('distanceBetween', name = f'{moduleNamespace}:distBetween_{rootLocatorWithoutNamespace}_{endLocatorWithoutNamespace}')

    containedNodes.append(distNode)

    cmds.connectAttr(f'{rootLocator}Shape.worldPosition[0]', f'{distNode}.point1')
    cmds.connectAttr(f'{endLocator}Shape.worldPosition[0]', f'{distNode}.point2')
    scaleAttr = f'{distNode}.distance'

    # divide distance by total original length * scale factor
    scaleFactor = cmds.createNode('multiplyDivide', name = f'{ikHandle}_scaleFactor')
    containedNodes.append(scaleFactor)

    cmds.setAttr(f'{scaleFactor}.operation', 2) # divide
    cmds.connectAttr(scaleAttr  , f'{scaleFactor}.input1X')
    cmds.setAttr(f'{scaleFactor}.input2X', totalOriginalLength)

    translationDriver = f'{scaleFactor}.outputX'

    # connect joints to stretchy calculations
    for joint in childJoints:
        multNode = cmds.createNode('multiplyDivide', name = f'{joint}_scaleMultiply')
        containedNodes.append(multNode)

        cmds.setAttr(f'{multNode}.input1X', cmds.getAttr(f'{joint}.translateX'))
        cmds.connectAttr(translationDriver, f'{multNode}.input2X')
        cmds.connectAttr(f'{multNode}.outputX', f'{joint}.translateX')



    if container:
        addNodeToContainer(container, containedNodes, includeHierarchyBelow = True)

    returnDict = {}
    returnDict['ikHandle'] = ikHandle
    returnDict['ikEffector'] = ikEffector
    returnDict['rootLocator'] = rootLocator
    returnDict['endLocator'] = endLocator
    returnDict['poleVectorObject'] = poleVectorObject
    returnDict['ikHandlePointConstraint'] = ikHandle_pointConstraint
    returnDict['rootLocatorPointConstraint'] = rootLocator_pointConstraint

    return returnDict


def forceSceneUpdate():
    cmds.setToolTo('moveSuperContext')

    for node in cmds.ls():
        cmds.select(node, replace = True)

    cmds.select(clear = True)

    cmds.setToolTo('selectSuperContext')


def addNodeToContainer(container, nodesIn, includeHierarchyBelow = False, includeShapes = False, force = False):
    if isinstance(nodesIn, list):
        nodes = list(nodesIn)

    else:
        nodes = [nodesIn]

    conversionNodes = []
    for node in nodes:
        node_conversionNodes = cmds.listConnections(node, source = True, destination = True, type = 'unitConversion')

    nodes.extend(conversionNodes)
    cmds.container(container, edit = True, addNode = nodes, includeHierarchyBelow = includeHierarchyBelow, includeShapes = includeShapes, force = force)
