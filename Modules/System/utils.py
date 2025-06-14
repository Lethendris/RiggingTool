from codecs import replace_errors

import maya.cmds as cmds


def findHighestTrailingNumber(names, baseName):
    """
    Finds the highest numeric suffix following a given base name in a list of names.

    Args:
        names (list[str]): List of names to inspect.
        baseName (str): Base name prefix to search for.

    Returns:
        int: Highest numeric suffix found after the base name.
    """

    highestValue = 0

    for name in names:
        if name.startswith(baseName):
            suffix = name[len(baseName):]
            if suffix.isdigit():
                highestValue = max(highestValue, int(suffix))

    return highestValue


def stripAllNamespaces(nodeName):
    """
    Splits a Maya node name into its namespace and base name using the last colon.

    Args:
        nodeName (str): Node name which may include namespace(s).

    Returns:
        list[str] or None: [namespace, baseName] if a namespace exists, otherwise None.
    """

    if ':' not in str(nodeName):
        return None

    namespace, _, baseName = str(nodeName).rpartition(':')
    return [namespace, baseName]


def stripLeadingNamespace(nodeName):
    """
    Splits a Maya node name into the first namespace and the rest of the name.

    Args:
        nodeName (str): Node name that may include a namespace.

    Returns:
        list[str] or None: [namespace, baseName] if a namespace exists, otherwise None.
    """
    if ':' not in nodeName:
        return None

    namespace, _, baseName = nodeName.partition(':')
    return [namespace, baseName]


def basicStretchyIK(rootJoint, endJoint, container = None, lockMinimumLength = True, poleVectorObject = None, scaleCorrectionAttribute = None):
    """
    Creates a basic stretchy IK system between two joints, with optional container and pole vector.

    Args:
        rootJoint (str): Name of the root joint.
        endJoint (str): Name of the end joint.
        container (str, optional): Name of the container to add new nodes to.
        lockMinimumLength (bool, optional): Reserved for stretch clamping (currently unused).
        poleVectorObject (str, optional): An optional pole vector control object.
        scaleCorrectionAttribute (str, optional): Reserved for scale correction (currently unused).

    Returns:
        dict: Dictionary of created nodes, useful for future references or constraints.
    """

    containedNodes = []

    totalOriginalLength = 0.0
    parent = rootJoint

    childJoints = []

    # Traverse joint chain to gather all joints and measure total original length
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

    # Create IK handle and rename effector
    ikNodes = cmds.ikHandle(startJoint = rootJoint, endEffector = endJoint, solver = 'ikRPsolver',
                            name = f'{rootJoint}_ikHandle')
    ikNodes[1] = cmds.rename(ikNodes[1], f'{rootJoint}_ikEffector')

    ikEffector = ikNodes[1]
    ikHandle = ikNodes[0]

    cmds.setAttr(f'{ikHandle}.visibility', 0)
    containedNodes.extend(ikNodes)

    # Create pole vector if none provided
    if not poleVectorObject:
        poleVectorObject = cmds.spaceLocator(name = f'{ikHandle}_poleVectorLocator')[0]

        cmds.xform(poleVectorObject, worldSpace = True, absolute = True,
                   translation = cmds.xform(rootJoint, query = True, worldSpace = True, translation = True))
        cmds.xform(poleVectorObject, worldSpace = True, relative = True, translation = (0.0, 1.0, 0.0))

        cmds.setAttr(f'{poleVectorObject}.visibility', 0)

    poleVectorConstraint = cmds.poleVectorConstraint(poleVectorObject, ikHandle)[0]
    containedNodes.append(poleVectorConstraint)

    # Create locators for measuring distance
    rootLocator = cmds.spaceLocator(name = f'{rootJoint}_rootPosLocator')[0]
    rootLocator_pointConstraint = \
        cmds.pointConstraint(rootJoint, rootLocator, maintainOffset = False, name = f'{rootLocator}_pointConstraint')[0]

    endLocator = cmds.spaceLocator(name = f'{endJoint}_endPosLocator')[0]
    cmds.xform(endLocator, worldSpace = True, absolute = True,
               translation = cmds.xform(ikHandle, query = True, worldSpace = True, translation = True))
    ikHandle_pointConstraint = cmds.pointConstraint(endLocator, ikHandle, maintainOffset = False, name = f'{ikHandle}_pointConstraint')[0]

    containedNodes.extend([rootLocator, endLocator, rootLocator_pointConstraint, ikHandle_pointConstraint])

    cmds.setAttr(f'{rootLocator}.visibility', 0)
    cmds.setAttr(f'{endLocator}.visibility', 0)

    # Setup distance measurement between locators
    rootLocatorWithoutNamespace = stripAllNamespaces(rootLocator)[1]
    endLocatorWithoutNamespace = stripAllNamespaces(endLocator)[1]
    moduleNamespace = stripAllNamespaces(rootJoint)[0]

    distNode = cmds.createNode('distanceBetween', name = f'{moduleNamespace}:distBetween_{rootLocatorWithoutNamespace}_{endLocatorWithoutNamespace}')

    containedNodes.append(distNode)

    cmds.connectAttr(f'{rootLocator}Shape.worldPosition[0]', f'{distNode}.point1')
    cmds.connectAttr(f'{endLocator}Shape.worldPosition[0]', f'{distNode}.point2')
    scaleAttr = f'{distNode}.distance'

    # Divide distance by original length to get scale factor
    scaleFactor = cmds.createNode('multiplyDivide', name = f'{ikHandle}_scaleFactor')
    containedNodes.append(scaleFactor)

    cmds.setAttr(f'{scaleFactor}.operation', 2)  # divide
    cmds.connectAttr(scaleAttr, f'{scaleFactor}.input1X')
    cmds.setAttr(f'{scaleFactor}.input2X', totalOriginalLength)

    translationDriver = f'{scaleFactor}.outputX'

    # Multiply original translateX by scale factor
    for joint in childJoints:
        multNode = cmds.createNode('multiplyDivide', name = f'{joint}_scaleMultiply')
        containedNodes.append(multNode)

        cmds.setAttr(f'{multNode}.input1X', cmds.getAttr(f'{joint}.translateX'))
        cmds.connectAttr(translationDriver, f'{multNode}.input2X')
        cmds.connectAttr(f'{multNode}.outputX', f'{joint}.translateX')

    # Optionally add all created nodes to the given container
    if container:
        addNodeToContainer(container, containedNodes, includeHierarchyBelow = True)

    return {
        'ikHandle': ikHandle,
        'ikEffector': ikEffector,
        'rootLocator': rootLocator,
        'endLocator': endLocator,
        'poleVectorObject': poleVectorObject,
        'ikHandlePointConstraint': ikHandle_pointConstraint,
        'rootLocatorPointConstraint': rootLocator_pointConstraint
    }



def forceSceneUpdate():
    """
    Forces Maya's scene graph to update by cycling selection and tool context.
    This can help ensure scene elements evaluate or refresh visually.
    """

    cmds.setToolTo('moveSuperContext')

    for node in cmds.ls():
        cmds.select(node, replace = True)

    cmds.select(clear = True)

    cmds.setToolTo('selectSuperContext')


def addNodeToContainer(container, nodesIn, includeHierarchyBelow = False, includeShapes = False, force = False):
    """
    Adds specified nodes to a Maya container, optionally including hierarchy or shapes.

    Args:
        container (str): The name of the container node.
        nodesIn (list or str): Node(s) to add to the container.
        includeHierarchyBelow (bool): Include entire node hierarchies below the specified nodes.
        includeShapes (bool): Include shape nodes in addition to transform nodes.
        force (bool): Force addition even if some nodes are already in the container.
    """

    if isinstance(nodesIn, list):
        nodes = list(nodesIn)

    else:
        nodes = [nodesIn]

    # Add any connected unitConversion nodes
    conversionNodes = []
    for node in nodes:
        node_conversionNodes = cmds.listConnections(node, source = True, destination = True, type = 'unitConversion')

    nodes.extend(conversionNodes)
    cmds.container(container, edit = True, addNode = nodes, includeHierarchyBelow = includeHierarchyBelow, includeShapes = includeShapes, force = force)
