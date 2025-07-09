import os
from dis import Positions

import maya.cmds as cmds
import importlib


def getPythonFiles(directory):
    """
    Retrieves a list of Python files (.py) from the specified directory.

    Args:
        directory (str): The path to the directory to search.

    Returns:
        list: A list of Python filenames found in the directory.
    """

    return [f for f in os.listdir(directory) if f.endswith('.py') and os.path.isfile(os.path.join(directory, f))]


def importModuleFromPath(moduleName, filePath):
    """
    Dynamically imports a Python module from a given file path.

    Args:
        moduleName (str): The name to assign to the imported module.
        filePath (str): The full path to the Python file.

    Returns:
        module: The imported module object.

    Raises:
        FileNotFoundError: If the module file does not exist.
    """
    if not os.path.exists(filePath):
        raise FileNotFoundError(f"Module file not found: {filePath}")

    spec = importlib.util.spec_from_file_location(moduleName, filePath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def loadAllModulesFromDirectory(directory):
    """
    Loads all Python modules from the specified directory and returns their metadata.
    Each module is expected to potentially have CLASS_NAME, MODULE_DESCRIPTION, and MODULE_ICON attributes.

    Args:
        directory (str): Path to the directory containing Python files.

    Returns:
        dict: A dictionary where keys are module filenames (without .py extension)
              and values are dictionaries containing:
              - 'module': The imported module object.
              - 'name': The CLASS_NAME attribute from the module, or the filename if not found.
              - 'description': The MODULE_DESCRIPTION attribute, or a default string.
              - 'icon': The MODULE_ICON attribute, or an empty string.
    """
    if not directory or not os.path.isdir(directory):
        print(f"Error: Invalid module directory: {directory}")
        return {}

    loadedModules = {}

    for fileName in getPythonFiles(directory):
        modulePath = os.path.join(directory, fileName)
        moduleName = os.path.splitext(fileName)[0] # Get module name without .py extension

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
    Useful for generating unique names (e.g., 'object1', 'object2').

    Args:
        names (list[str]): List of names to inspect.
        baseName (str): Base name prefix to search for (e.g., 'object').

    Returns:
        int: Highest numeric suffix found after the base name. Returns 0 if no suffix is found.
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
    Splits a Maya node name into its full namespace path and base name,
    using the last colon as the separator.

    Args:
        nodeName (str): Node name which may include namespace(s) (e.g., 'ns1:ns2:node').

    Returns:
        list[str] or None: A list containing [namespace_path, baseName] if a namespace exists,
                           otherwise None.
    """

    if ':' not in str(nodeName):
        return None

    namespace, _, baseName = str(nodeName).rpartition(':')
    return [namespace, baseName]



def stripLeadingNamespace(nodeName):
    """
    Splits a Maya node name into its first namespace and the rest of the name.

    Args:
        nodeName (str): Node name that may include a namespace (e.g., 'ns1:ns2:node').

    Returns:
        list[str] or None: A list containing [first_namespace, rest_of_name] if a namespace exists,
                           otherwise None.
    """
    if ':' not in nodeName:
        return None

    namespace, _, baseName = nodeName.partition(':')
    return [namespace, baseName]


def basicStretchyIK(rootJoint, endJoint, container = None, lockMinimumLength = True, poleVectorObject = None, scaleCorrectionAttribute = None):

    containedNodes = []

    totalOriginalLength = 0.0
    done = False
    parent = rootJoint

    childJoints = []

    while True:
        children = cmds.listRelatives(parent, children = True, type = 'joint')

        if not children:
            break

        child = children[0]
        childJoints.append(child)

        totalOriginalLength += abs(cmds.getAttr(f'{child}.translateX'))

        if child == endJoint:
            break

        parent = child

    ikNodes = cmds.ikHandle(startJoint = rootJoint, endEffector = endJoint, solver = 'ikRPsolver', name = f'{rootJoint}_ikHandle')
    ikNodes[1] = cmds.rename(ikNodes[1], f'{rootJoint}_ikEffector')
    ikHandle = ikNodes[0]
    ikEffector = ikNodes[1]

    cmds.setAttr(f'{ikHandle}.visibility', 0)
    containedNodes.extend(ikNodes)

    if not poleVectorObject:
        poleVectorObject = cmds.spaceLocator(name = f'{ikHandle}_poleVectorLocator')[0]
        containedNodes.append(poleVectorObject)

        rootJointPos = cmds.xform(rootJoint, query = True, worldSpace = True, translation = True)
        cmds.xform(poleVectorObject, worldSpace = True, absolute = True, translation = rootJointPos)

        cmds.xform(poleVectorObject, worldSpace = True, relative = True, translation = (0.0, 1.0, 0.0))

    poleVectorConstraint = cmds.poleVectorConstraint(poleVectorObject, ikHandle)[0]
    containedNodes.append(poleVectorConstraint)

    rootLocator = cmds.spaceLocator(name = f'{rootJoint}_rootPosLocator')[0]
    rootLocator_pointConstraint = cmds.pointConstraint(rootJoint, rootLocator, maintainOffset = False, name = f'{rootLocator}_pointConstraint')[0]

    endLocator = cmds.spaceLocator(name = f'{endJoint}_endPosLocator')[0]
    ikHandlePos = cmds.xform(ikHandle, query = True, worldSpace = True, translation = True)
    cmds.xform(endLocator, worldSpace = True, absolute = True, translation = ikHandlePos)
    ikHandle_pointConstraint = cmds.pointConstraint(endLocator, ikHandle, maintainOffset = False, name = f'{ikHandle}_pointConstraint')[0]

    containedNodes.extend([rootLocator, endLocator, rootLocator_pointConstraint, ikHandle_pointConstraint])

    cmds.setAttr(f'{rootLocator}.visibility', 0)
    cmds.setAttr(f'{endLocator}.visibility', 0)

    rootLocatorWithoutNamespace = stripAllNamespaces(rootLocator)[1]
    endLocatorWithoutNamespace = stripAllNamespaces(endLocator)[1]

    moduleNamespace = stripAllNamespaces(rootJoint)[0]

    distNode = cmds.createNode('distanceBetween', name = f'{moduleNamespace}:distBetween_{rootLocatorWithoutNamespace}_{endLocatorWithoutNamespace}')
    containedNodes.append(distNode)

    cmds.connectAttr(f'{rootLocator}Shape.worldPosition[0]', f'{distNode}.point1')
    cmds.connectAttr(f'{endLocator}Shape.worldPosition[0]', f'{distNode}.point2')

    scaleAttr = f'{distNode}.distance'

    scaleFactor = cmds.createNode('multiplyDivide', name = f'{ikHandle}_scaleFactor')
    containedNodes.append(scaleFactor)

    cmds.setAttr(f'{scaleFactor}.operation', 2)
    cmds.connectAttr(scaleAttr, f'{scaleFactor}.input1X')
    cmds.setAttr(f'{scaleFactor}.input2X', totalOriginalLength)

    translationDriver = f'{scaleFactor}.outputX'

    for joint in childJoints:
        multNode = cmds.createNode('multiplyDivide', name = f'{joint}_scaleMultiply')
        containedNodes.append(multNode)

        cmds.setAttr(f'{multNode}.input1X', cmds.getAttr(f'{joint}.translateX'))
        cmds.connectAttr(translationDriver, f'{multNode}.input2X')
        cmds.connectAttr(f'{multNode}.outputX', f'{joint}.translateX')




    if container:
        addNodeToContainer(container = container, nodesIn = [containedNodes], includeHierarchyBelow = True)

    return {
        'ikHandle': ikHandle,
        'ikEffector': ikEffector,
        'rootLocator': rootLocator,
        'endLocator': endLocator,
        'poleVectorObject': poleVectorObject,
        'ikHandlePointConstraint': ikHandle_pointConstraint,
        'rootLocatorPointConstraint': rootLocator_pointConstraint
    }


# totalOriginalLength = 0.0
    # parent = rootJoint
    #
    # childJoints = []
    #
    # # Traverse joint chain to gather all joints and measure total original length
    # while True:
    #     children = cmds.listRelatives(parent, children = True)
    #     children = cmds.ls(children, type = 'joint')
    #
    #     if not children:
    #         break
    #
    #     child = children[0]
    #     childJoints.append(child)
    #
    #     totalOriginalLength += cmds.getAttr(f'{child}.translateX')
    #
    #     parent = child
    #
    #     if child == endJoint:
    #         break
    #
    # # Create IK handle and rename effector
    # ikNodes = cmds.ikHandle(startJoint = rootJoint, endEffector = endJoint, solver = 'ikRPsolver',
    #                         name = f'{rootJoint}_ikHandle')
    # ikNodes[1] = cmds.rename(ikNodes[1], f'{rootJoint}_ikEffector')
    #
    # ikEffector = ikNodes[1]
    # ikHandle = ikNodes[0]
    #
    # cmds.setAttr(f'{ikHandle}.visibility', 0)
    # containedNodes.extend(ikNodes)
    #
    # # Create pole vector if none provided
    # if not poleVectorObject:
    #     poleVectorObject = cmds.spaceLocator(name = f'{ikHandle}_poleVectorLocator')[0]
    #     containedNodes.append(poleVectorObject)
    #
    #     cmds.xform(poleVectorObject, worldSpace = True, absolute = True, translation = cmds.xform(rootJoint, query = True, worldSpace = True, translation = True))
    #     cmds.xform(poleVectorObject, worldSpace = True, relative = True, translation = (0.0, 1.0, 0.0))
    #
    #     cmds.setAttr(f'{poleVectorObject}.visibility', 0)
    #
    # poleVectorConstraint = cmds.poleVectorConstraint(poleVectorObject, ikHandle)[0]
    # containedNodes.append(poleVectorConstraint)
    #
    # # Create locators for measuring distance
    # rootLocator = cmds.spaceLocator(name = f'{rootJoint}_rootPosLocator')[0]
    # rootLocator_pointConstraint = cmds.pointConstraint(rootJoint, rootLocator, maintainOffset = False, name = f'{rootLocator}_pointConstraint')[0]
    #
    # endLocator = cmds.spaceLocator(name = f'{endJoint}_endPosLocator')[0]
    # cmds.xform(endLocator, worldSpace = True, absolute = True,
    #            translation = cmds.xform(ikHandle, query = True, worldSpace = True, translation = True))
    # ikHandle_pointConstraint = cmds.pointConstraint(endLocator, ikHandle, maintainOffset = False, name = f'{ikHandle}_pointConstraint')[0]
    #
    # containedNodes.extend([rootLocator, endLocator, rootLocator_pointConstraint, ikHandle_pointConstraint])
    #
    # cmds.setAttr(f'{rootLocator}.visibility', 0)
    # cmds.setAttr(f'{endLocator}.visibility', 0)
    #
    # # Setup distance measurement between locators
    # rootLocatorWithoutNamespace = stripAllNamespaces(rootLocator)[1]
    # endLocatorWithoutNamespace = stripAllNamespaces(endLocator)[1]
    # moduleNamespace = stripAllNamespaces(rootJoint)[0]
    #
    # distNode = cmds.createNode('distanceBetween', name = f'{moduleNamespace}:distBetween_{rootLocatorWithoutNamespace}_{endLocatorWithoutNamespace}')
    #
    # containedNodes.append(distNode)
    #
    # cmds.connectAttr(f'{rootLocator}Shape.worldPosition[0]', f'{distNode}.point1')
    # cmds.connectAttr(f'{endLocator}Shape.worldPosition[0]', f'{distNode}.point2')
    # scaleAttr = f'{distNode}.distance'
    #
    # # Divide distance by original length to get scale factor
    # scaleFactor = cmds.createNode('multiplyDivide', name = f'{ikHandle}_scaleFactor')
    # containedNodes.append(scaleFactor)
    #
    # cmds.setAttr(f'{scaleFactor}.operation', 2)  # divide
    # cmds.connectAttr(scaleAttr, f'{scaleFactor}.input1X')
    # cmds.setAttr(f'{scaleFactor}.input2X', totalOriginalLength)
    #
    # translationDriver = f'{scaleFactor}.outputX'
    #
    # # Multiply original translateX by scale factor
    # for joint in childJoints:
    #     multNode = cmds.createNode('multiplyDivide', name = f'{joint}_scaleMultiply')
    #     containedNodes.append(multNode)
    #
    #     cmds.setAttr(f'{multNode}.input1X', cmds.getAttr(f'{joint}.translateX'))
    #     cmds.connectAttr(translationDriver, f'{multNode}.input2X')
    #     cmds.connectAttr(f'{multNode}.outputX', f'{joint}.translateX')
    #
    # # Optionally add all created nodes to the given container
    # if container:
    #     addNodeToContainer(container, containedNodes, includeHierarchyBelow = True)
    #
    # return {
    #     'ikHandle': ikHandle,
    #     'ikEffector': ikEffector,
    #     'rootLocator': rootLocator,
    #     'endLocator': endLocator,
    #     'poleVectorObject': poleVectorObject,
    #     'ikHandlePointConstraint': ikHandle_pointConstraint,
    #     'rootLocatorPointConstraint': rootLocator_pointConstraint
    # }


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
    Adds specified nodes to a Maya container.

    Args:
        container (str): The name of the container node to add nodes to.
        nodesIn (list or str): A single node name or a list of node names to add.
        includeHierarchyBelow (bool): If True, includes the entire hierarchy below the specified nodes.
        includeShapes (bool): If True, includes shape nodes associated with the specified nodes.
        includeShaders (bool): If True, includes shader nodes connected to the specified nodes.
        force (bool): If True, forces the addition even if some nodes are already in the container.
    """

    # Ensure nodesIn is a list for consistent processing
    nodes = nodesIn if isinstance(nodesIn, list) else [nodesIn]

    def flatten(inputList):
        """Flattens a nested list to a single list of strings (non-recursive)."""
        result = []
        for item in inputList:
            if isinstance(item, list):
                result.extend(item)
            else:
                result.append(item)
        return result

    if isinstance(nodesIn, str):
        nodes = [nodesIn]
    elif isinstance(nodesIn, list):
        nodes = flatten(nodesIn)
    else:
        raise TypeError("nodesIn must be a string or a list of strings.")

    conversionNodes = []

    for node in nodes:
        node_conversionNodes = cmds.listConnections(node, source = True, destination = True)
        node_conversionNodes = cmds.ls(node_conversionNodes, type = 'unitConversion')

        conversionNodes.extend(node_conversionNodes)

    nodes.extend(conversionNodes)

    cmds.container(container,
                   edit = True,
                   addNode = nodes,
                   includeHierarchyBelow = includeHierarchyBelow,
                   includeShapes = includeShapes,
                   includeShaders = includeShaders,
                   force = force)

def createContainer(name, nodesIn = None, includeHierarchyBelow = True, includeShaders = True, includeTransform = True, includeShapes = True, force = True):
    """
    Creates a new Maya container node and optionally adds specified nodes to it.
    Also renames the associated hyperLayout node for clarity.

    Args:
        name (str): The desired name for the new container node.
        nodesIn (list or str, optional): A single node name or a list of node names to add initially.
                                         Defaults to None (empty container).
        includeHierarchyBelow (bool): If True, includes the entire hierarchy below the specified nodes.
        includeShaders (bool): If True, includes shader nodes connected to the specified nodes.
        includeTransform (bool): If True, includes transform nodes.
        includeShapes (bool): If True, includes shape nodes.
        force (bool): If True, forces the creation/addition.

    Returns:
        str: The name of the newly created container node.
    """
    # Ensure nodesIn is a list for consistent processing
    nodes = nodesIn if isinstance(nodesIn, list) else [nodesIn] if nodesIn else []

    # Create the container and add initial nodes
    container = cmds.container(name = name,
                               addNode = nodes,
                               includeHierarchyBelow = includeHierarchyBelow,
                               includeShaders = includeShaders,
                               includeTransform = includeTransform,
                               includeShapes = includeShapes,
                               force = force)

    # Find and rename the associated hyperLayout node for better organization
    hyperLayout = cmds.listConnections(container, type = 'hyperLayout')
    if hyperLayout: # Check if hyperLayout exists (it usually does)
        cmds.rename(hyperLayout[0], f'{name}_hyperLayout') # hyperLayout returns a list

    return container

def assignMaterial(obj, color = (1, 0, 0), diffuse = 0.2):
    """
    Creates a Lambert material with specified color and diffuse properties,
    assigns it to the given Maya object, and returns the material and its materialInfo node.
    If a material with the generated name already exists, it will be reused.

    Args:
        obj (str): The name of the object (e.g., a transform node) to assign the material to.
        color (tuple): A tuple (R, G, B) representing the diffuse color (values from 0 to 1).
                       Defaults to red (1, 0, 0).
        diffuse (float): The diffuse intensity of the material (value from 0 to 1).
                         Defaults to 0.2.

    Returns:
        list: A list containing [materialNode (str), materialInfoNode (str)].
    """
    # Generate a material name based on the object name
    # If obj is namespaced, the material will also be namespaced, which is fine for modularity.
    materialName = f'{obj}_m'

    # Create material if it doesn't exist, otherwise reuse existing
    if not cmds.objExists(materialName):
        material = cmds.shadingNode("lambert", asShader = True, name = materialName)
    else:
        material = materialName # Use the existing material

    # Set color and diffuse attributes
    cmds.setAttr(f"{material}.color", *color, type = "double3")
    cmds.setAttr(f"{material}.diffuse", diffuse)

    # Create a shading group for the material
    shadingGroup = cmds.sets(renderable = True, noSurfaceShader = True, empty = True, name = f"{material}SG")
    # Connect the material's outColor to the shading group's surfaceShader
    cmds.connectAttr(f"{material}.outColor", f"{shadingGroup}.surfaceShader", force = True)

    # Assign the material to the specified object
    cmds.sets(obj, edit = True, forceElement = shadingGroup)

    # Find and rename the associated materialInfo node for clarity
    materialInfo = cmds.listConnections(material, type = "materialInfo")
    materialInfoNode = materialInfo[0] if materialInfo else None # Get the first materialInfo node
    if materialInfoNode:
        materialInfoNode = cmds.rename(materialInfoNode, f'{obj}_mInfo')

    return [material, materialInfoNode]


def createTranslationControl(name):
    """
    Creates a standard translation control (a red sphere) with an assigned material
    and places it within its own container. This function assumes it is called
    within the desired Maya namespace.

    Args:
        name (str): The base name for the control and its container.
                    This name will be used to form unique names like
                    '{name}_translation_control' and '{name}_translation_container'.

    Returns:
        list: A list containing [container (str), control (str)].
    """
    # CRITICAL FIX: Removed cmds.namespace(setNamespace = ':')
    # This function should operate within the current active namespace set by the caller (e.g., Blueprint.install).
    # Changing the namespace here would break the intended naming structure.

    # Create the control geometry (a sphere)
    # The name will be formed using the 'name' argument, which should already include the namespace
    # if called from a namespaced context (e.g., 'moduleNamespace:jointName').
    control = cmds.sphere(name = f'{name}_translation_control', ax = (0, 1, 0), ch = False)[0]

    # Assign a red material to the control
    material, materialInfo = assignMaterial(control, color = (1, 0, 0))

    # Create a container for the control and its associated nodes (material, materialInfo)
    # The container name will also be formed using the 'name' argument.
    container = createContainer(name = f'{name}_translation_container',
                                nodesIn = [control, material, materialInfo],
                                includeHierarchyBelow = True,
                                includeShaders = True,
                                includeTransform = True,
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

    constrainedGrp = cmds.group(empty = True, name = f'{connector}_parentConstrainedGrp')
    cmds.parent(connector, constrainedGrp, absolute = True)

    # Create container and add nodes
    container = createContainer(name = f'{name}_orientation_container', nodesIn = [connector, constrainedGrp, y_material, y_materialInfo, z_material, z_materialInfo], includeHierarchyBelow = True,
                                includeShaders = True, includeTransform = True, includeShapes = True)

    return [container, connector, constrainedGrp]

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

    constrainedGrp = cmds.group(empty = True, name = f'{connector}_parentConstrainedGrp')
    cmds.parent(connector, constrainedGrp, absolute = True)

    # Create container and add nodes
    container = createContainer(name = f'{name}_hierarchy_container', nodesIn = [connector, material, materialInfo, constrainedGrp], includeHierarchyBelow = True, includeShaders = True, includeTransform = True,
                                includeShapes = True)

    return [container, connector, constrainedGrp]

def createHookConnector(name):
    cylinder = cmds.cylinder(name = f'{name}_cylinder', radius = 0.2, heightRatio = 5, ch = False)[0]

    cmds.move(0.5, 0, 0, f'{cylinder}.cv[0:3][0:7]', relative = True)

    material, materialInfo = assignMaterial(cylinder, color = (0.5, 0.8, 0.8), diffuse = 0.2)

    connector = cmds.rename(cylinder, f'{name}_hook_connector', ignoreShape = True)

    constrainedGrp = cmds.group(empty = True, name = f'{connector}_parentConstrainedGrp')
    cmds.parent(connector, constrainedGrp, absolute = True)

    # Create container and add nodes
    container = createContainer(name = f'{name}_hook_container', nodesIn = [connector, constrainedGrp, material, materialInfo], includeHierarchyBelow = True, includeShaders = True, includeTransform = True,
                                includeShapes = True)

    return [container, connector, constrainedGrp]


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

    combined = cmds.polyUnite(control, cubeX, cubeY, cubeZ, ch = False, mergeUVSets = True)
    control = cmds.rename(combined, name)
    # cmds.parent(cubeXShape, cubeYShape, cubeZShape, control, shape = True, relative = True, noConnections = True)
    # cmds.delete(cubeX, cubeY, cubeZ)

    # for shape in cmds.listRelatives(name, shapes = True, fullPath = True):
    #     cmds.setAttr(f'{shape}.overrideEnabled', 1)
    #     cmds.setAttr(f'{shape}.overrideShading', 0)

    shapes = cmds.listRelatives(control, shapes = True, fullPath = True) or []
    for shape in shapes:
        # Clean up unused groupId connections
        connections = cmds.listConnections(shape, type = "groupId") or []
        for conn in connections:
            try:
                cmds.delete(conn)
            except:
                pass

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