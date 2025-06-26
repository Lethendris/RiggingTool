import os
import maya.cmds as cmds
import importlib


def getPythonFiles(directory):
    return [f for f in os.listdir(directory) if f.endswith('.py') and os.path.isfile(os.path.join(directory, f))]


def importModuleFromPath(moduleName, filePath):
    """Dynamically import a module from a file path"""
    if not os.path.exists(filePath):
        raise FileNotFoundError(f"Module file not found: {filePath}")

    spec = importlib.util.spec_from_file_location(moduleName, filePath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def loadAllModulesFromDirectory(directory):
    """
    Loads all Python modules from the specified directory and returns their metadata.

    :param directory: Path to the directory containing Python files.
    :return: Dictionary where keys are module names and values are dicts with:
             {
                 'module': <module object>,
                 'name': <CLASS_NAME or file name>,
                 'description': <MODULE_DESCRIPTION or default>,
                 'icon': <MODULE_ICON or empty string>
             }
    """
    if not directory or not os.path.isdir(directory):
        print(f"Error: Invalid module directory: {directory}")
        return {}

    loadedModules = {}

    for fileName in getPythonFiles(directory):
        modulePath = os.path.join(directory, fileName)
        moduleName = os.path.splitext(fileName)[0]


        try:
            mod = importModuleFromPath(moduleName, modulePath)

            loadedModules[moduleName] = {
                'name' : getattr(mod, 'CLASS_NAME', moduleName),
                'module': mod,
                'description': getattr(mod, 'MODULE_DESCRIPTION', 'No description available'),
                'icon': getattr(mod, 'MODULE_ICON', '')
            }

        except Exception as e:
            print(f'Error loading module {moduleName}: {str(e)}')

    return loadedModules


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
        containedNodes.append(poleVectorObject)

        cmds.xform(poleVectorObject, worldSpace = True, absolute = True,
                   translation = cmds.xform(rootJoint, query = True, worldSpace = True, translation = True))
        cmds.xform(poleVectorObject, worldSpace = True, relative = True, translation = (0.0, 1.0, 0.0))

        cmds.setAttr(f'{poleVectorObject}.visibility', 0)

    poleVectorConstraint = cmds.poleVectorConstraint(poleVectorObject, ikHandle)[0]
    containedNodes.append(poleVectorConstraint)

    # Create locators for measuring distance
    rootLocator = cmds.spaceLocator(name = f'{rootJoint}_rootPosLocator')[0]
    rootLocator_pointConstraint = cmds.pointConstraint(rootJoint, rootLocator, maintainOffset = False, name = f'{rootLocator}_pointConstraint')[0]

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


def addNodeToContainer(container, nodesIn, includeHierarchyBelow = False, includeShapes = True, includeShaders = True, force = False):
    """
    Adds specified nodes to a Maya container, optionally including hierarchy or shapes.

    Args:
        container (str): The name of the container node.
        nodesIn (list or str): Node(s) to add to the container.
        includeHierarchyBelow (bool): Include entire node hierarchies below the specified nodes.
        includeShapes (bool): Include shape nodes.
        includeShaders (bool): Include shader nodes.
        force (bool): Force addition even if some nodes are already in the container.
    """

    if isinstance(nodesIn, list):
        nodes = list(nodesIn)

    else:
        nodes = [nodesIn]

    # Add any connected unitConversion nodes
    # conversionNodes = []
    # for node in nodes:
    #     node_conversionNodes = cmds.listConnections(node, source = True, destination = True, type = 'unitConversion')
    #
    # nodes.extend(conversionNodes)
    cmds.container(container, edit = True, addNode = nodes, includeHierarchyBelow = includeHierarchyBelow, includeShapes = includeShapes, includeShaders = True, force = force)

def createContainer(name, nodesIn, includeHierarchyBelow = True, includeShaders = True, includeTransform = True, includeShapes = True, force = True):
    if isinstance(nodesIn, list):
        nodes = list(nodesIn)

    else:
        nodes = [nodesIn]

    container = cmds.container(name = name, addNode = nodes, includeHierarchyBelow = includeHierarchyBelow, includeShaders = includeShaders, includeTransform = includeTransform, includeShapes = includeShapes, force = force)
    hyperLayout = cmds.listConnections(container, type = 'hyperLayout')
    hyperLayout = cmds.rename(hyperLayout, f'{name}_hyperLayout')

    return container

def assignMaterial(obj, color = (1, 0, 0), diffuse = 0.2):
    """
    Creates a Lambert material, assigns it to the given object,
    and returns both the material and its materialInfo node.

    Args:
        obj (str): The name of the object to assign the material to.
        materialName (str): The name of the material to create.
        color (tuple): RGB values for the diffuse color.
        diffuse (float): Diffuse intensity (0–1 range).

    Returns:
        tuple: (materialNode, materialInfoNode)
    """
    materialName = f'{obj}_m'

    # Create material
    if not cmds.objExists(materialName):
        material = cmds.shadingNode("lambert", asShader = True, name = materialName)
    else:
        material = materialName

    # Set color and diffuse
    cmds.setAttr(f"{material}.color", *color, type = "double3")
    cmds.setAttr(f"{material}.diffuse", diffuse)

    # Create shading group
    shadingGroup = cmds.sets(renderable = True, noSurfaceShader = True, empty = True, name = f"{material}SG")
    cmds.connectAttr(f"{material}.outColor", f"{shadingGroup}.surfaceShader", force = True)

    # Assign material to object
    cmds.sets(obj, edit = True, forceElement = shadingGroup)

    # Return the materialInfo node if connected
    materialInfo = cmds.listConnections(material, type = "materialInfo")
    materialInfoNode = materialInfo[0] if materialInfo else None
    materialInfoNode = cmds.rename(materialInfoNode, f'{obj}_mInfo')

    return [material, materialInfoNode]


def createTranslationControl(name):
    """
    Creates a translation control as a red sphere, assigns a material, and adds it to a container.

    Args:
        name (str): Name of the control object (sphere).

    Returns:
        tuple: (controlObject, materialNode, materialInfoNode, containerNode)
    """
    # Create control sphere
    control = cmds.sphere(name = f'{name}_translation_control', ax = (0, 1, 0), ch = False)[0]

    # Assign red material
    material, materialInfo = assignMaterial(control, color = (1, 0, 0))

    # Create container and add nodes
    container = createContainer(name = f'{name}_translation_container', nodesIn = [control, material, materialInfo], includeHierarchyBelow = True, includeShaders = True, includeTransform = True,
                                includeShapes = True)

    return [container, control]


def createOrientationConnector(name):
    """
    Creates a translation control as a red sphere, assigns a material, and adds it to a container.

    Args:
        name (str): Name of the control object.

    Returns:
        tuple: (controlObject, materialNode, materialInfoNode, containerNode)
    """

    # Create Y axis object
    y_cube = cmds.polyCube(name = f'{name}_y_cube', width = 1, height = 1, depth = 0.1, ch = False)[0]
    cmds.move(0.5, 0, 0, f'{y_cube}.f[5]', relative = True)
    cmds.move(0.5, 0, 0, f'{y_cube}.f[4]', relative = True)


    y_cone = cmds.polyCone(name = f'{name}_y_cone', sx = 8, sy = 1, sz = 0, r = 0.05, h = 0.2, heightBaseline = -1, ch = False)[0]
    y_coneShape = cmds.listRelatives(y_cone, shapes = True, fullPath = True)
    cmds.move(0.5, 0.5, 0, f'{y_cone}.vtx[0:8]', relative = True)

    cmds.parent(y_coneShape, y_cube, shape = True, relative = True, noConnections = True)
    cmds.delete(y_cone)

    y_material, y_materialInfo = assignMaterial(y_cube, color = (0, 1, 0), diffuse = 0.2)

    # Create Z axis object
    z_cube = cmds.polyCube(name = f'{name}_z_cube', width = 1, height = 1, depth = 0.1, ch = False)[0]
    cmds.rotate(90, 0, 0, f'{z_cube}.vtx[0:7]', relative = True)

    cmds.move(0.5, 0, 0, f'{z_cube}.vtx[0:7]', relative = True)


    z_cone = cmds.polyCone(name = f'{name}_z_cone', sx = 8, sy = 1, sz = 0, r = 0.05, h = 0.2, heightBaseline = -1, ch = False)[0]
    z_coneShape = cmds.listRelatives(z_cone, shapes = True, fullPath = True)
    cmds.rotate(90, 0, 0, f'{z_cone}.vtx[0:8]', relative = True, pivot = (0, 0, 0))
    cmds.move(0.5 , 0, 0.5, f'{z_cone}.vtx[0:8]', relative = True)

    cmds.parent(z_coneShape, z_cube, shape = True, relative = True, noConnections = True)


    z_material, z_materialInfo = assignMaterial(z_cube, color = (0, 0, 1), diffuse = 0.2)
    for shape in cmds.listRelatives(z_cube, shapes = True, fullPath = True):
        cmds.parent(shape, y_cube, shape = True, relative = True, noConnections = True)

    cmds.delete(z_cube, z_cone)
    connector = cmds.rename(y_cube, f'{name}_orientation_connector', ignoreShape = True)

    # Create container and add nodes
    container = createContainer(name = f'{name}_orientation_container', nodesIn = [connector, y_material, y_materialInfo, z_material, z_materialInfo], includeHierarchyBelow = True,
                                includeShaders = True, includeTransform = True, includeShapes = True)

    return [container, connector]

def createHierarchyConnector(name):
    cylinder = cmds.polyCylinder(name = f'{name}_cylinder', sx = 8, sy = 1, sz = 1, height = 1, radius = 0.2, heightBaseline = -1, ch = False)[0]
    cmds.delete(f'{cylinder}.f[8:23]')

    cmds.rotate(0, 0, -90, f'{cylinder}.vtx[0:15]', relative = True, pivot = (0, 0, 0))


    cone = cmds.polyCone(name = f'{name}_cone', sx = 8, sy = 1, sz = 0, r = 0.75, h = 0.2, heightBaseline = -1, ch = False)[0]
    coneShape = cmds.listRelatives(cone, shapes = True, fullPath = True)[0]

    cmds.rotate(0, 0, -90, f'{cone}.vtx[0:8]', relative = True)

    cmds.move(0.4, 0, 0, f'{cone}.vtx[0:8]', relative = True)

    cmds.parent(coneShape, cylinder, shape = True, relative = True, noConnections = True)

    material, materialInfo = assignMaterial(cylinder, color = (1.0, 0.8, 0), diffuse = 0.2)

    cmds.delete(cone)
    connector = cmds.rename(cylinder, f'{name}_hierarchy_connector', ignoreShape = True)

    # Create container and add nodes
    container = createContainer(name = f'{name}_hierarchy_container', nodesIn = [connector, material, materialInfo], includeHierarchyBelow = True, includeShaders = True, includeTransform = True,
                                includeShapes = True)

    return [container, connector]

def createHookConnector(name):
    cylinder = cmds.cylinder(name = f'{name}_cylinder', radius = 0.2, heightRatio = 5, ch = False)[0]

    cmds.move(0.5, 0, 0, f'{cylinder}.cv[0:3][0:7]', relative = True)

    material, materialInfo = assignMaterial(cylinder, color = (0.5, 0.8, 0.8), diffuse = 0.2)

    connector = cmds.rename(cylinder, f'{name}_hook_connector', ignoreShape = True)

    # Create container and add nodes
    container = createContainer(name = f'{name}_hook_container', nodesIn = [connector, material, materialInfo], includeHierarchyBelow = True, includeShaders = True, includeTransform = True,
                                includeShapes = True)

    return [container, connector]


def createModuleTransformControl(name):
    control = cmds.polyCube(name = name, width = 2, height = 2, depth = 2, ch = False)[0]

    cubeX = cmds.polyCube(name = f'{name}_cubeX', width = 3, height = 3, depth = 3, ch = False)[0]
    cubeXShape = cmds.listRelatives(cubeX, shapes = True, fullPath = True)[0]
    cmds.move(0, 0, -1.5, f'{cubeXShape}.f[0]', relative = True)
    cmds.move(0, 0, 1.5, f'{cubeXShape}.f[2]', relative = True)
    cmds.move(0, -1.5, 0, f'{cubeXShape}.f[1]', relative = True)
    cmds.move(0, 1.5, 0, f'{cubeXShape}.f[3]', relative = True)

    cubeY = cmds.polyCube(name = f'{name}_cubeY', width = 3, height = 3, depth = 3, ch = False)[0]
    cubeYShape = cmds.listRelatives(cubeY, shapes = True, fullPath = True)[0]
    cmds.move(-1.5, 0, 0, f'{cubeYShape}.f[4]', relative = True)
    cmds.move(1.5, 0, 0, f'{cubeYShape}.f[5]', relative = True)
    cmds.move(0, 0, -1.5, f'{cubeYShape}.f[0]', relative = True)
    cmds.move(0, 0, 1.5, f'{cubeYShape}.f[2]', relative = True)

    cubeZ = cmds.polyCube(name = f'{name}_cubeZ', width = 3, height = 3, depth = 3, ch = False)[0]
    cubeZShape = cmds.listRelatives(cubeZ, shapes = True, fullPath = True)[0]
    cmds.move(-1.5, 0, 0, f'{cubeZShape}.f[4]', relative = True)
    cmds.move(1.5, 0, 0, f'{cubeZShape}.f[5]', relative = True)
    cmds.move(0, -1.5, 0, f'{cubeZShape}.f[1]', relative = True)
    cmds.move(0, 1.5, 0, f'{cubeZShape}.f[3]', relative = True)

    cmds.parent(cubeXShape, cubeYShape, cubeZShape, control, shape = True, relative = True, noConnections = True)
    cmds.delete(cubeX, cubeY, cubeZ)

    for shape in cmds.listRelatives(name, shapes = True, fullPath = True):
        cmds.setAttr(f'{shape}.overrideEnabled', 1)
        cmds.setAttr(f'{shape}.overrideShading', 0)

    return control

def doesBlueprintUserSpecifiedNameExist(name):
    cmds.namespace(setNamespace = ':')
    namespaces = cmds.namespaceInfo(listOnlyNamespaces = True)

    names = []

    for namespace in namespaces:
        if namespace.find('__') != -1:
            names.append(namespace.partition('__')[2])

    return name in names # Returns bool