import os

import maya.cmds as cmds

import System.utils as utils
import importlib
importlib.reload(utils)

class Blueprint:
    def __init__(self, moduleName, userSpecifiedName, jointInfo):

        """
        Initialize the ModuleA instance with a given user-specified name.

        Args:
            userSpecifiedName (str): Custom name to uniquely identify this module instance.
        """

        self.moduleName = moduleName # Constant module base name (should be defined externally).
        self.userSpecifiedName = userSpecifiedName
        self.jointInfo = jointInfo
        self.moduleNamespace = f'{self.moduleName}__{self.userSpecifiedName}'
        self.containerName = f'{self.moduleNamespace}:module_container'

    # Methods intended for overriding by derived class
    def install_custom(self, joints):
        print('install_custom() methods is not implemented by derived class.')

    def lockPhase1(self):
        # Gather and return all required information from this module's control objects
        # joint positions = list of joint positions, from root down the hierarchy
        # joint orientations = list of orientations, or a list of axis information (orientJoint and secondaryAxisOrient for joint command)
        # these are passed in the following tuple : (orientations, None) or (None, axisInfo)
        # jointRotationOrders = list of joint rotation orders (integer values gathered with getAttr)
        # jointPreferredAngles = list of joint preferred angles, optional (can pass None)
        # hookObject = self.findHookObjectForLock()
        # rootTransform = a bool, either True or False. True = R, T, and S on root joint. False = R only.
        # moduleInfo = (jointPositions, jointOrientations, jointRotationOrders, jointPreferredAngles, hookObject, rootTransform
        # return moduleInfo
        return None

    def lockPhase2(self, moduleInfo):
        ([[0.0, 0.0, 0.0], [4.0, 0.0, 0.0]], ([(0.0, -0.0, 0.0)], None), [0], None, None, False)

        jointPositions = moduleInfo[0]
        numJoints = len(jointPositions)

        jointOrientations = moduleInfo[1]
        orientWithAxis = False
        pureOrientations = False

        if jointOrientations[0] == None:
            orientWithAxis = True
            jointOrientations = jointOrientations[1]

        else:
            pureOrientations = True
            jointOrientations = jointOrientations[0]

        numOrientations = len(jointOrientations)

        jointRotationOrders = moduleInfo[2]
        numRotationOrders = len(jointRotationOrders)

        jointPreferredAngles = moduleInfo[3]
        numPreferredAngles = 0

        if jointPreferredAngles != None:
            numPreferredAngles = len(jointPreferredAngles)

        # hook object = moduleInfo[4]

        rootTransform = moduleInfo[5]

        # Delete blueprint controls

        cmds.lockNode(self.containerName, lock = False, lockUnpublished = False)
        cmds.delete(self.containerName, hierarchy = 'below')

        cmds.namespace(setNamespace = ':')

        jointRadius = 1

        if numJoints == 1:
            jointRadius = 1.5

        newJoints = []

        for i in range(numJoints):
            newJoint = ''
            cmds.select(clear = True)

            if orientWithAxis:

                newJoint = cmds.joint(name = f'{self.moduleNamespace}:blueprint_{self.jointInfo[i][0]}', position = jointPositions[i], rotationOrder = 'xyz', radius = jointRadius)

                if i != 0:
                    cmds.parent(newJoint, newJoints[i-1], absolute = True)
                    offsetIndex = i - 1

                    if offsetIndex < numOrientations:
                        cmds.joint(newJoints[offsetIndex], edit = True, orientJoint = jointOrientations[offsetIndex][0], secondaryAxisOrient = jointOrientations[offsetIndex][1])

                        cmds.makeIdentity(newJoint, rotate = True, apply = True)

            else:
                if i != 0:
                    cmds.select(newJoints[i-1])

                jointOrientation = [0.0, 0.0, 0.0]

                if i < numOrientations:
                    jointOrientation = [jointOrientations[i][0], jointOrientations[i][1], jointOrientations[i][2]]

                newJoint = cmds.joint(name = f'{self.moduleNamespace}:blueprint_{self.jointInfo[i][0]}', position = jointPositions[i], orientation = jointOrientation, rotationOrder = 'xyz', radius = jointRadius)

            newJoints.append(newJoint)

            if i < numRotationOrders:
                cmds.setAttr(f'{newJoint}.rotateOrder', int(jointRotationOrders[i]))

            if i < numPreferredAngles:
                cmds.setAttr(f'{newJoint}.preferredAngleX', jointPreferredAngles[i][0])
                cmds.setAttr(f'{newJoint}.preferredAngleY', jointPreferredAngles[i][1])
                cmds.setAttr(f'{newJoint}.preferredAngleZ', jointPreferredAngles[i][2])


            cmds.setAttr(f'{newJoint}.segmentScaleCompensate', 0)

        blueprintGrp = cmds.group(empty = True, name = f'{self.moduleNamespace}:blueprint_joints_grp')
        cmds.parent(newJoints[0], blueprintGrp, absolute = True)

        creationPoseGrpNodes = cmds.duplicate(blueprintGrp, name = f'{self.moduleNamespace}:creationPose_joints_grp', renameChildren = True)
        creationPoseGrp = creationPoseGrpNodes[0]

        creationPoseGrpNodes.pop(0)

        for index, node in enumerate(creationPoseGrpNodes):
            renamedNode = cmds.rename(node, f'{self.moduleNamespace}:creationPose_{self.jointInfo[index][0]}')
            cmds.setAttr(f'{renamedNode}.visibility', 0)

        cmds.addAttr(blueprintGrp, attributeType = 'bool', defaultValue = 0, longName = 'controlModulesInstalled', keyable = False)

        settingsLocator = cmds.spaceLocator(name = f'{self.moduleNamespace}:SETTINGS')[0]
        cmds.setAttr(f'{settingsLocator}.visibility', 0)

        cmds.addAttr(settingsLocator, attributeType = 'enum', longName = 'activeModule', enumName = 'None:', keyable = False)
        cmds.addAttr(settingsLocator, attributeType = 'float', longName = 'creationPoseWeight', defaultValue = 1, keyable = False)
        
        utilityNodes = []

        for index, joint in enumerate(newJoints):
            if index < (numJoints - 1) or numJoints == 1:
                addNode = cmds.createNode('plusMinusAverage', name = f'{joint}_addRotations')
                cmds.connectAttr(f'{addNode}.output3D', f'{joint}.rotate', force = True)
                utilityNodes.append(addNode)

                dummyRotationsMultiply = cmds.createNode('multiplyDivide', name = f'{joint}_dummyRotationsMultiply')
                cmds.connectAttr(f'{dummyRotationsMultiply}.output', f'{addNode}.input3D[0]', force = True)
                utilityNodes.append(dummyRotationsMultiply)

            if index > 0:
                originalTx = cmds.getAttr(f'{joint}.tx')
                addTxNode = cmds.createNode('plusMinusAverage', name = f'{joint}_addTx')
                cmds.connectAttr(f'{addTxNode}.output1D', f'{joint}.translateX', force = True)
                utilityNodes.append(addTxNode)

                originalTxMultiply = cmds.createNode('multiplyDivide', name = f'{joint}_original_Tx')
                cmds.setAttr(f'{originalTxMultiply}.input1X', originalTx, lock = True)
                cmds.connectAttr(f'{settingsLocator}.creationPoseWeight', f'{originalTxMultiply}.input2X')
                cmds.connectAttr(f'{originalTxMultiply}.outputX', f'{addTxNode}.input1D[0]', force = True)
                utilityNodes.append(originalTxMultiply)

            else:
                if rootTransform:
                    originalTranslates = cmds.getAttr(f'{joint}.translate')[0]
                    addTranslateNode = cmds.createNode('plusMinusAverage', name = f'{joint}_addTranslate')
                    cmds.connectAttr(f'{addTranslateNode}.output3D', f'{joint}.translate', force = True)
                    utilityNodes.append(addTranslateNode)

                    originalTranslateMultiply = cmds.createNode('multiplyDivide', name = f'{joint}_original_translate')
                    cmds.setAttr(f'{originalTranslateMultiply}.input1', originalTranslates[0], originalTranslates[1], originalTranslates[2], type = 'double3')

                    for attr in ['X', 'Y', 'Z']:
                        cmds.connectAttr(f'{settingsLocator}.creationPoseWeight', f'{originalTranslateMultiply}.input2{attr}')

                    cmds.connectAttr(f'{originalTranslateMultiply}.output', f'{addTranslateNode}.input3D[0]', force = True)
                    utilityNodes.append(originalTranslateMultiply)

                    # Scale
                    originalScales = cmds.getAttr(f'{joint}.scale')[0]
                    addScaleNode = cmds.createNode('plusMinusAverage', name = f'{joint}_addScale')
                    cmds.connectAttr(f'{addScaleNode}.output3D', f'{joint}.scale', force = True)
                    utilityNodes.append(addScaleNode)

                    originalScaleMultiply = cmds.createNode('multiplyDivide', name = f'{joint}_original_scale')
                    cmds.setAttr(f'{originalScaleMultiply}.input1', originalScales[0], originalScales[1], originalScales[2], type = 'double3')

                    for attr in ['X', 'Y', 'Z']:
                        cmds.connectAttr(f'{settingsLocator}.creationPoseWeight', f'{originalScaleMultiply}.input2{attr}')

                    cmds.connectAttr(f'{originalScaleMultiply}.output', f'{addScaleNode}.input3D[0]', force = True)
                    utilityNodes.append(originalScaleMultiply)

        blueprintNodes = utilityNodes
        blueprintNodes.append(blueprintGrp)
        blueprintNodes.append(creationPoseGrp)

        blueprintContainer = utils.createContainer(name = f'{self.moduleNamespace}:blueprint_container', nodesIn = blueprintNodes, includeHierarchyBelow = True, includeShaders = True,
                                                   includeTransform = True, includeShapes = True)

        moduleGrp = cmds.group(empty = True, name = f'{self.moduleNamespace}:module_grp')
        cmds.parent(settingsLocator, moduleGrp, absolute = True)

        # TEMP
        for group in [blueprintGrp, creationPoseGrp]:
            cmds.parent(group, moduleGrp, absolute = True)
        # END TEMP

        moduleContainer = utils.createContainer(name = f'{self.moduleNamespace}:module_container', nodesIn = [moduleGrp, settingsLocator, blueprintContainer], includeHierarchyBelow = True,
                                                includeShaders = True, includeTransform = True, includeShapes = True)

        cmds.container(moduleContainer, edit = True, publishAndBind = (f'{settingsLocator}.activeModule', 'activeModule'))
        cmds.container(moduleContainer, edit = True, publishAndBind = (f'{settingsLocator}.creationPoseWeight', 'creationPoseWeight'))

        # TEMP
        cmds.lockNode(moduleContainer, lock = True, lockUnpublished = True)
        # END TEMP


    # BASE CLASS METHODS
    def install(self):

        """
        Set up the module in the Maya scene by creating joints, control groups,
        containers, and applying stretchy IK functionality.
        """

        # Ensure we’re in the root namespace and create a unique one for this module.
        # cmds.namespace(setNamespace = ':')
        # cmds.namespace(addNamespace = self.moduleNameSpace)

        # Create groups to organize joints and visual representation.
        self.jointsGrp = cmds.group(empty = True, name = f'{self.moduleNamespace}:joints_grp')
        self.hierarchyConnectorsGrp = cmds.group(empty = True, name = f'{self.moduleNamespace}:hierarchyConnectors_grp')
        self.orientationConnectorsGrp = cmds.group(empty = True, name = f'{self.moduleNamespace}:orientationConnectors_grp')
        self.moduleGrp = cmds.group(self.jointsGrp, self.hierarchyConnectorsGrp, self.orientationConnectorsGrp, name = f'{self.moduleNamespace}:module_grp')

        # Create a container and include the hierarchy.
        utils.createContainer(name = self.containerName, nodesIn = [self.moduleGrp], includeHierarchyBelow = True)

        cmds.select(clear = True)

        # Create joints as defined in self.jointInfo.

        joints = []

        for index, (jointName, jointPos) in enumerate(self.jointInfo):
            parentName = ''

            if index > 0:
                parentName = f'{self.moduleNamespace}:{self.jointInfo[index - 1][0]}'
                cmds.select(parentName, replace = True)

            jointName_full = cmds.joint(name = f'{self.moduleNamespace}:{jointName}', position = jointPos)
            joints.append(jointName_full)

            # Hide joint from view
            cmds.setAttr(f'{jointName_full}.visibility', 0)

            # Add joint to the module container.
            utils.addNodeToContainer(self.containerName, jointName_full)

            # Publish joint rotate and rotateOrder attributes.
            cmds.container(self.containerName, edit = True, publishAndBind = (f'{jointName_full}.rotate', f'{jointName}_R'))
            cmds.container(self.containerName, edit = True, publishAndBind = (f'{jointName_full}.rotateOrder', f'{jointName}_rotateOrder'))

            # Orient the joint properly if it's not the first one.
            if index > 0:
                cmds.joint(parentName, edit = True, orientJoint = 'xyz', secondaryAxisOrient = 'yup')

        # Parent the root joint to the joints group.
        cmds.parent(joints[0], self.jointsGrp, absolute = True)

        self.initializeModuleTransform(self.jointInfo[0][1])

        # Create translation controls at each joint.
        translationControls = []

        for joint in joints:
            translationControls.append(self.createTranslationControlAtJoint(joint))

        # Constrain root joint to its translation control.

        rootJoint_pointConstraint = cmds.pointConstraint(translationControls[0], joints[0], maintainOffset = False, name = f'{joints[0]}_pointConstraint')


        utils.addNodeToContainer(self.containerName, rootJoint_pointConstraint)


        # Create stretchy segments between each joint pair.
        for index in range(len(joints) - 1):
            self.setupStretchyJointSegment(connectorType = 'orientation', parentJoint = joints[index], childJoint = joints[index + 1])

        self.install_custom(joints)

        # Lock the container to prevent accidental edits.
        cmds.lockNode(self.containerName, lock = True, lockUnpublished = True)

    def createTranslationControlAtJoint(self, joint):
        """
        Creates a translation control object at the specified joint.

        Args:
            joint (str): Name of the joint to attach a control to.

        Returns:
            str: The name of the created control object.
        """

        container, control = utils.createTranslationControl(name = joint)

        utils.addNodeToContainer(self.containerName, container)

        cmds.parent(control, self.moduleTransform, absolute = True)

        # Move control to match the joint's position.
        jointPos = cmds.xform(joint, query = True, worldSpace = True, translation = True)
        cmds.xform(control, worldSpace = True, absolute = True, translation = jointPos)

        # Publish translation attribute to container.
        niceName = utils.stripLeadingNamespace(joint)[1]
        attrName = f'{niceName}_T'

        cmds.container(container, edit = True, publishAndBind = (f'{control}.translate', attrName))
        cmds.container(self.containerName, edit = True, publishAndBind = (f'{container}.{attrName}', attrName))

        return control


    def getTranslationControl(self, jointName):

        return f'{jointName}_translation_control'

    def getOrientationControl(self, jointName):

        return f'{jointName}_orientation_connector'

    def setupStretchyJointSegment(self, connectorType, parentJoint, childJoint):
        """
        Set up a stretchy IK segment between a parent and child joint.

        Args:
            parentJoint (str): Start joint.
            childJoint (str): End joint.
        """

        parentTranslationControl = self.getTranslationControl(parentJoint)
        childTranslationControl = self.getTranslationControl(childJoint)

        # Create a locator for the pole vector control and constrain it.
        poleVectorLocator = cmds.spaceLocator(name = f'{parentTranslationControl}_poleVectorLocator')[0]
        poleVectorLocatorGrp = cmds.group(poleVectorLocator, name = f'{poleVectorLocator}_parentConstraintGrp')

        cmds.parent(poleVectorLocatorGrp, self.moduleGrp, absolute = True)
        parentConstraint = cmds.parentConstraint(parentTranslationControl, poleVectorLocatorGrp, maintainOffset = False)[0]

        cmds.setAttr(f'{poleVectorLocator}.visibility', 0)
        cmds.setAttr(f'{poleVectorLocator}.ty', -0.5)
        self.createConnector(connectorType = connectorType, name = parentJoint, parentJoint = parentJoint, childJoint = childJoint)

        # Setup stretchy IK using utility function.
        ikNodes = utils.basicStretchyIK(rootJoint = parentJoint, endJoint = childJoint, container = self.containerName, lockMinimumLength = False, poleVectorObject = poleVectorLocator,
                        scaleCorrectionAttribute = None)

        ikHandle = ikNodes['ikHandle']
        rootLocator = ikNodes['rootLocator']
        endLocator = ikNodes['endLocator']

        # Constrain end locator to translation control.
        childPointConstraint = cmds.pointConstraint(childTranslationControl, endLocator, maintainOffset = False, name = f'{endLocator}_pointConstraint')[0]

        utils.addNodeToContainer(self.containerName, [poleVectorLocatorGrp, parentConstraint, childPointConstraint], includeHierarchyBelow = True)

        # Hide and parent IK nodes.
        for node in [ikHandle, rootLocator, endLocator]:
            cmds.parent(node, self.jointsGrp, absolute = True)
            cmds.setAttr(f'{node}.visibility', 0)

    def initializeModuleTransform(self, rootPos):
        self.moduleTransform = utils.createModuleTransformControl(name = f'{self.moduleNamespace}:module_transform')

        cmds.xform(self.moduleTransform, worldSpace = True, absolute = True, translation = rootPos)

        utils.addNodeToContainer(self.containerName, self.moduleTransform, includeHierarchyBelow = True)

        # Setup global scaling
        cmds.connectAttr(f'{self.moduleTransform}.scaleY', f'{self.moduleTransform}.scaleX')
        cmds.connectAttr(f'{self.moduleTransform}.scaleY', f'{self.moduleTransform}.scaleZ')

        cmds.aliasAttr('globalScale', f'{self.moduleTransform}.scaleY')

        cmds.container(self.containerName, edit = True, publishAndBind = (f'{self.moduleTransform}.translate', 'moduleTransform_T'))
        cmds.container(self.containerName, edit = True, publishAndBind = (f'{self.moduleTransform}.rotate', 'moduleTransform_R'))
        cmds.container(self.containerName, edit = True, publishAndBind = (f'{self.moduleTransform}.globalScale', 'moduleTransform_globalScale'))

    def createConnector(self, connectorType, name, parentJoint, childJoint):
        """
        Creates a visual connector between two joints, typically used to represent hierarchy links.

        This function creates a stretchy visual object between the parent and child joints
        using the specified connector type, then parents the resulting visual representation under the provided group.

        Args:
            connectorType (str): The type of visual connection to create (e.g., 'hierarchy', 'orientation').
            parentGrp (str): The transform node under which the connector should be parented.
            parentJoint (str): The name of the starting joint of the connection.
            childJoint (str): The name of the ending joint of the connection.

        Returns:
            list: A list containing:
                - container (str): The name of the container node for the created objects.
                - control (str): The name of the main control or geometry created.
                - constrainedGrp (str): The name of the group constrained between the two joints.
        """


        if connectorType == 'orientation':
            container, connector = utils.createOrientationConnector(name)
            parentGrp = self.orientationConnectorsGrp

        elif connectorType == 'hierarchy':
            container, connector = utils.createHierarchyConnector(name)
            parentGrp = self.hierarchyConnectorsGrp

        # container, control, constrainedGrp = self.createStretchyObject(connectorType, parentJoint, childJoint)
        constrainedGrp = cmds.group(empty = True, name = f'{connector}_parentConstraint_grp')
        cmds.parent(connector, constrainedGrp, absolute = True)
        parentConstraint = cmds.parentConstraint(parentJoint, constrainedGrp, maintainOffset = False)[0]

        # Connect translateX to scaleX to drive stretch.
        cmds.connectAttr(f'{childJoint}.translateX', f'{constrainedGrp}.scaleX')

        scaleConstraint = cmds.scaleConstraint(self.moduleTransform, constrainedGrp, skip = ['x'], maintainOffset = False)[0]

        cmds.parent(constrainedGrp, parentGrp, relative = True)

        # Add to containers.
        utils.addNodeToContainer(container, [constrainedGrp, parentConstraint, scaleConstraint], includeHierarchyBelow = True)
        utils.addNodeToContainer(self.containerName, container)

        # Parent the visual representation group under the hierarchy group.
        # cmds.parent(constrainedGrp, parentGrp, relative = True)
        if connectorType == 'orientation':
            niceName = utils.stripLeadingNamespace(parentJoint)[1]
            attrName = f'{niceName}_orientation'
            print(niceName)
            cmds.container(container, edit = True, publishAndBind = (f'{connector}.rotateX', attrName))
            cmds.container(self.containerName, edit = True, publishAndBind = (f'{container}.{attrName}', attrName))

        return [container, connector, constrainedGrp]

    def getJoints(self):
        jointBaseName = f'{self.moduleNamespace}:'
        joints = []

        for jointInfo in self.jointInfo:
            joints.append(f'{jointBaseName}{jointInfo[0]}')

        return joints

    def orientationControlledJoint_getOrientation(self, joint, cleanParent):
        newCleanParent = cmds.duplicate(joint, parentOnly = True)[0]

        if not cleanParent in cmds.listRelatives(newCleanParent, parent = True):
            cmds.parent(newCleanParent, cleanParent, absolute = True)

        cmds.makeIdentity(newCleanParent, apply = True, rotate = True, scale = False, translate = False)

        orientationControl = self.getOrientationControl(joint)
        cmds.setAttr(f'{newCleanParent}.rotateX', cmds.getAttr(f'{orientationControl}.rotateX'))

        cmds.makeIdentity(newCleanParent, apply = True, rotate = True, scale = False, translate = False)

        orientX = cmds.getAttr(f'{newCleanParent}.jointOrientX')
        orientY = cmds.getAttr(f'{newCleanParent}.jointOrientY')
        orientZ = cmds.getAttr(f'{newCleanParent}.jointOrientZ')

        orientationValues = (orientX, orientY, orientZ)

        return (orientationValues, newCleanParent)

