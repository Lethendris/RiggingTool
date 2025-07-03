"""
Base Blueprint Module for Maya Rigging

This module defines the foundational `Blueprint` class, which serves as a base for creating
rigging modules in Maya. It provides core functionalities for managing module instances,
UI integration, and the installation process of module-specific components like joints
and controls. Derived classes are expected to override certain methods to implement
module-specific logic.
"""

import os
import maya.cmds as cmds
from PySide6 import QtCore, QtWidgets
import System.utils as utils
import importlib

importlib.reload(utils)  # Reload the utils module to ensure the latest version is used.


class Blueprint:
    """
    The base class for all rigging blueprint modules.

    This class provides the fundamental structure and methods for a rigging module,
    including initialization, UI integration, and the two-phase installation process
    (lockPhase1 and lockPhase2).

    Attributes:
        moduleName (str): The base name of the module (e.g., 'arm', 'leg').
        userSpecifiedName (str): A unique name given by the user for this instance of the module.
        jointInfo (list): A list of tuples, where each tuple contains (joint_name, joint_position).
        moduleNamespace (str): The unique namespace for this module instance in Maya (e.g., 'arm__instance_1').
        containerName (str): The name of the main container node for this module in Maya.
        hookObject (str): The name of the object in Maya to which this module should be hooked.

    """

    def __init__(self, moduleName, userSpecifiedName, jointInfo, hookObjectIn):

        """
        Initializes a new instance of the Blueprint module.

        Args:
            moduleName (str): The base name of the module.
            userSpecifiedName (str): A custom name to uniquely identify this module instance.
            jointInfo (list): A list of tuples, each containing (joint_name, joint_position).
            hookObjectIn (str): The name of a potential hook object from the Maya selection.
                                This is typically a translation control from another module.
        """

        self.moduleName = moduleName
        self.userSpecifiedName = userSpecifiedName
        self.jointInfo = jointInfo
        self.moduleNamespace = f'{self.moduleName}__{self.userSpecifiedName}'  # Construct the unique namespace for this module instance.
        self.containerName = f'{self.moduleNamespace}:module_container'  # Construct the name for the main container node.
        self.hookObject = None

        # Determine if the provided hookObjectIn is a valid translation control.
        if hookObjectIn is not None:
            # Check if the object name ends with '_translation_control' and has no suffix after it.
            before, split, after = hookObjectIn.rpartition('_translation_control')
            if split != '' and after == '':
                self.hookObject = hookObjectIn

        self.canBeMirrored = True

    # Methods intended for overriding by derived class
    def install_custom(self, joints):
        """
        Placeholder method for custom installation logic specific to derived classes.

        Derived classes should override this method to implement any unique setup
        or connections required after the base installation process.

        Args:
            joints (list): A list of the created joint names in Maya.
        """

    def UI(self, blueprint_UI_instance, parentLayout):
        """
        Initializes the UI for this module within the Blueprint UI.

        This method sets up references to the main Blueprint UI instance and the parent
        layout, then calls the `UI_custom` method for derived-class specific UI elements.

        Args:
            blueprint_UI_instance (Blueprint_UI): The main Blueprint UI instance.
            parentLayout (QtWidgets.QLayout): The layout to which module-specific UI elements should be added.
        """

        self.blueprint_UI_instance = blueprint_UI_instance
        self.parentLayout = parentLayout
        self.UI_custom()

    def UI_custom(self):
        """
        Placeholder method for custom UI creation logic specific to derived classes.

        Derived classes should override this method to add their own unique UI controls
        and widgets to the `parentLayout` provided in the `UI` method.
        """

    def lockPhase1(self):
        """
        First phase of the locking process for a blueprint module.

        This method is intended to gather and return all necessary information
        from the module's control objects before they are deleted.

        Returns:
            tuple or None: A tuple containing:
                           (jointPositions, jointOrientations, jointRotationOrders,
                           jointPreferredAngles, hookObject, rootTransform)
                           Returns None if not implemented by the derived class.
        """

        return None

    def lockPhase2(self, moduleInfo):
        """
        Second phase of the locking process for a blueprint module.

        This method takes the gathered `moduleInfo` from `lockPhase1` and uses it
        to create the final, production-ready joints and their associated utility nodes.

        Args:
            moduleInfo (tuple): A tuple containing all necessary joint and module information
                                 as returned by `lockPhase1`.
        """

        jointPositions = moduleInfo[0]
        numJoints = len(jointPositions)

        jointOrientations = moduleInfo[1]
        orientWithAxis = False
        pureOrientations = False

        if jointOrientations[0] is None:  # Determine if orientations are pure rotations or axis information.
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

        if jointPreferredAngles is not None:
            numPreferredAngles = len(jointPreferredAngles)

        hookObject = moduleInfo[4]

        rootTransform = moduleInfo[5]

        cmds.lockNode(self.containerName, lock = False, lockUnpublished = False)  # Delete blueprint controls and unlock the container.
        cmds.delete(self.containerName, hierarchy = 'below')

        cmds.namespace(setNamespace = ':')  # Set current namespace to root.

        jointRadius = 1

        if numJoints == 1:
            jointRadius = 1.5

        newJoints = []

        for i in range(numJoints):  # Create new joints based on the gathered information.
            newJoint = ''

            cmds.select(clear = True)

            if orientWithAxis:

                # Create joint with specified position and default rotation order.
                newJoint = cmds.joint(name = f'{self.moduleNamespaces}:blueprint_{self.jointInfo[i][0]}', position = jointPositions[i], rotationOrder = 'xyz', radius = jointRadius)

                if i != 0:
                    cmds.parent(newJoint, newJoints[i - 1], absolute = True)  # Parent the joint to the previous one in the hierarchy.
                    offsetIndex = i - 1

                    if offsetIndex < numOrientations:
                        # Apply joint orientation and secondary axis orientation.
                        cmds.joint(newJoints[offsetIndex], edit = True, orientJoint = jointOrientations[offsetIndex][0], secondaryAxisOrient = jointOrientations[offsetIndex][1])

                        # Freeze transformations to apply the orientation.
                        cmds.makeIdentity(newJoint, rotate = True, apply = True)

            else:
                if i != 0:
                    cmds.select(newJoints[i - 1])

                jointOrientation = [0.0, 0.0, 0.0]

                if i < numOrientations:
                    jointOrientation = [jointOrientations[i][0], jointOrientations[i][1], jointOrientations[i][2]]

                # Create joint with specified position and orientation.
                newJoint = cmds.joint(name = f'{self.moduleNamespace}:blueprint_{self.jointInfo[i][0]}', position = jointPositions[i], orientation = jointOrientation, rotationOrder = 'xyz', radius = jointRadius)

            newJoints.append(newJoint)

            if i < numRotationOrders:  # Apply rotation order if available.
                cmds.setAttr(f'{newJoint}.rotateOrder', int(jointRotationOrders[i]))

            if i < numPreferredAngles:  # Apply preferred angles if available.
                cmds.setAttr(f'{newJoint}.preferredAngleX', jointPreferredAngles[i][0])
                cmds.setAttr(f'{newJoint}.preferredAngleY', jointPreferredAngles[i][1])
                cmds.setAttr(f'{newJoint}.preferredAngleZ', jointPreferredAngles[i][2])

            cmds.setAttr(f'{newJoint}.segmentScaleCompensate', 0)  # Disable segment scale compensate for all new joints.

        blueprintGrp = cmds.group(empty = True, name = f'{self.moduleNamespace}:blueprint_joints_grp')  # Group the newly created blueprint joints.
        cmds.parent(newJoints[0], blueprintGrp, absolute = True)

        creationPoseGrpNodes = cmds.duplicate(blueprintGrp, name = f'{self.moduleNamespace}:creationPose_joints_grp', renameChildren = True)  # Duplicate the blueprint group to create a creation pose group.
        creationPoseGrp = creationPoseGrpNodes[0]

        creationPoseGrpNodes.pop(0)

        for index, node in enumerate(creationPoseGrpNodes):  # Rename and hide the duplicated joints.
            renamedNode = cmds.rename(node, f'{self.moduleNamespace}:creationPose_{self.jointInfo[index][0]}')
            cmds.setAttr(f'{renamedNode}.visibility', 0)

        cmds.addAttr(blueprintGrp, attributeType = 'bool', defaultValue = 0, longName = 'controlModulesInstalled', keyable = False)  # Add a custom attribute to the blueprint group for installed modules.

        hookGrp = cmds.group(empty = True, name = f'{self.moduleNamespace}:HOOK_IN')
        for obj in [blueprintGrp, creationPoseGrp]:
            cmds.parent(obj, hookGrp, absolute = True)

        settingsLocator = cmds.spaceLocator(name = f'{self.moduleNamespace}:SETTINGS')[0]
        cmds.setAttr(f'{settingsLocator}.visibility', 0)

        cmds.addAttr(settingsLocator, attributeType = 'enum', longName = 'activeModule', enumName = 'None:', keyable = False)  # Add attributes to the settings locator for active module and creation pose weight.
        cmds.addAttr(settingsLocator, attributeType = 'float', longName = 'creationPoseWeight', defaultValue = 1, keyable = False)

        utilityNodes = []

        for index, joint in enumerate(newJoints):  # Create utility nodes for joint rotations and translations.
            if index < (numJoints - 1) or numJoints == 1:
                # Create plusMinusAverage node for joint rotations.
                addNode = cmds.createNode('plusMinusAverage', name = f'{joint}_addRotations')
                cmds.connectAttr(f'{addNode}.output3D', f'{joint}.rotate', force = True)
                utilityNodes.append(addNode)

                # Create multiplyDivide node for dummy rotations.
                dummyRotationsMultiply = cmds.createNode('multiplyDivide', name = f'{joint}_dummyRotationsMultiply')
                cmds.connectAttr(f'{dummyRotationsMultiply}.output', f'{addNode}.input3D[0]', force = True)
                utilityNodes.append(dummyRotationsMultiply)

            if index > 0:

                # For child joints, handle translateX.
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
                # For the root joint, handle translation and scale if rootTransform is True.
                if rootTransform:

                    # Translation
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

        # Create a container for the blueprint nodes.
        blueprintContainer = utils.createContainer(name = f'{self.moduleNamespace}:blueprint_container', nodesIn = blueprintNodes, includeHierarchyBelow = True, includeShaders = True, includeTransform = True, includeShapes = True)

        moduleGrp = cmds.group(empty = True, name = f'{self.moduleNamespace}:module_grp')  # Create a main group for the module.
        for obj in [hookGrp, settingsLocator]:
            cmds.parent(obj, moduleGrp, absolute = True)

        # Create the main module container and add relevant nodes.
        moduleContainer = utils.createContainer(name = f'{self.moduleNamespace}:module_container', nodesIn = [moduleGrp, settingsLocator, hookGrp, blueprintContainer], includeHierarchyBelow = True, includeShaders = True, includeTransform = True, includeShapes = True)

        cmds.container(moduleContainer, edit = True, publishAndBind = (f'{settingsLocator}.activeModule', 'activeModule'))  # Publish attributes from the settings locator to the module container.
        cmds.container(moduleContainer, edit = True, publishAndBind = (f'{settingsLocator}.creationPoseWeight', 'creationPoseWeight'))

        cmds.select(moduleGrp)
        cmds.addAttr(attributeType = 'float', longName = 'hierarchicalScale')
        cmds.connectAttr(f'{hookGrp}.scaleY', f'{moduleGrp}.hierarchicalScale')

    def lockPhase3(self, hookObject):
        if hookObject:
            hookObjectModuleNode = utils.stripLeadingNamespace(hookObject)
            hookObjectModule = hookObjectModuleNode[0]
            hookObjectJoint = hookObjectModuleNode[1].split('_translation_control')[0]

            hookObject = f'{hookObjectModule}:blueprint_{hookObjectJoint}'

            parentConstraint = cmds.parentConstraint(hookObject, f'{self.moduleNamespace}:HOOK_IN', maintainOffset = True, name = f'{self.moduleNamespace}:hook_parentConstraint')[0]
            scaleConstraint = cmds.scaleConstraint(hookObject, f'{self.moduleNamespace}:HOOK_IN', maintainOffset = True, name = f'{self.moduleNamespace}:hook_scaleConstraint')[0]

            utils.addNodeToContainer(self.containerName, [parentConstraint, scaleConstraint])

        cmds.lockNode(self.containerName, lock = True, lockUnpublished = True)

    # BASE CLASS METHODS
    def install(self):
        """
        Installs the blueprint module in the Maya scene.

        This method creates the necessary groups, joints, controls, and sets up
        connections for the module. It also calls `install_custom` for derived-class
        specific installation logic.
        """

        # Create groups to organize joints and visual representation.
        self.jointsGrp = cmds.group(empty = True, name = f'{self.moduleNamespace}:joints_grp')
        self.hierarchyConnectorsGrp = cmds.group(empty = True, name = f'{self.moduleNamespace}:hierarchyConnectors_grp')
        self.orientationConnectorsGrp = cmds.group(empty = True, name = f'{self.moduleNamespace}:orientationConnectors_grp')
        self.moduleGrp = cmds.group(self.jointsGrp, self.hierarchyConnectorsGrp, self.orientationConnectorsGrp, name = f'{self.moduleNamespace}:module_grp')

        utils.createContainer(name = self.containerName, nodesIn = [self.moduleGrp], includeHierarchyBelow = True)  # Create a container and include the hierarchy.

        cmds.select(clear = True)

        joints = []  # Create joints as defined in self.jointInfo.
        for index, (jointName, jointPos) in enumerate(self.jointInfo):
            parentName = ''

            if index > 0:
                parentName = f'{self.moduleNamespace}:{self.jointInfo[index - 1][0]}'
                cmds.select(parentName, replace = True)

            jointName_full = cmds.joint(name = f'{self.moduleNamespace}:{jointName}', position = jointPos)
            joints.append(jointName_full)

            cmds.setAttr(f'{jointName_full}.visibility', 0)  # Hide joint from view.

            utils.addNodeToContainer(self.containerName, jointName_full)  # Add joint to the module container.

            cmds.container(self.containerName, edit = True, publishAndBind = (f'{jointName_full}.rotate', f'{jointName}_R'))  # Publish joint rotate and rotateOrder attributes to the container.
            cmds.container(self.containerName, edit = True, publishAndBind = (f'{jointName_full}.rotateOrder', f'{jointName}_rotateOrder'))

            if index > 0:  # Orient the joint properly if it's not the first one.
                cmds.joint(parentName, edit = True, orientJoint = 'xyz', secondaryAxisOrient = 'yup')

        cmds.parent(joints[0], self.jointsGrp, absolute = True)  # Parent the root joint to the joints group.

        self.initializeModuleTransform(self.jointInfo[0][1])  # Initialize the module's main transform.

        translationControls = []  # Create translation controls at each joint.

        for joint in joints:
            translationControls.append(self.createTranslationControlAtJoint(joint))

        rootJoint_pointConstraint = cmds.pointConstraint(translationControls[0], joints[0], maintainOffset = False, name = f'{joints[0]}_pointConstraint')  # Constrain the root joint to its translation control.

        utils.addNodeToContainer(self.containerName, rootJoint_pointConstraint)

        self.initializeHook(translationControls[0])  # Initialize the hook object if one was provided.

        for index in range(len(joints) - 1):  # Create stretchy segments between each joint pair.
            self.setupStretchyJointSegment(connectorType = 'orientation', parentJoint = joints[index], childJoint = joints[index + 1])

        self.install_custom(joints)  # Call custom installation logic from derived classes.

        cmds.lockNode(self.containerName, lock = True, lockUnpublished = True)  # Lock the container to prevent accidental edits.

    def createTranslationControlAtJoint(self, joint):
        """
        Creates a translation control object at the specified joint's position.

        Args:
            joint (str): The name of the joint to attach a control to.

        Returns:
            str: The name of the created translation control object.
        """
        container, control = utils.createTranslationControl(name = joint)  # Create the translation control using a utility function.

        utils.addNodeToContainer(self.containerName, container)  # Add the control's container to the module's main container.

        cmds.parent(control, self.moduleTransform, absolute = True)  # Parent the control under the module's main transform.

        jointPos = cmds.xform(joint, query = True, worldSpace = True, translation = True)  # Move the control to match the joint's world position.
        cmds.xform(control, worldSpace = True, absolute = True, translation = jointPos)

        niceName = utils.stripLeadingNamespace(joint)[1]  # Publish the translation attribute of the control to its container.
        attrName = f'{niceName}_T'
        cmds.container(container, edit = True, publishAndBind = (f'{control}.translate', attrName))

        cmds.container(self.containerName, edit = True, publishAndBind = (f'{container}.{attrName}', attrName))  # Publish the control's container to the module's main container.

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

    def initializeModuleTransform(self, position):
        """
        Creates and initializes the main transform for the module.

        This transform serves as the root for all module components and allows
        for easy manipulation of the entire module.

        Args:
            position (list): A list of three floats [x, y, z] representing the initial
                             world space position of the module transform.
        """

        self.moduleTransform = utils.createModuleTransformControl(name = f'{self.moduleNamespace}:module_transform')  # Create an empty group to serve as the module's main transform.

        cmds.xform(self.moduleTransform, worldSpace = True, absolute = True, translation = position)  # Set its world space position.

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

        elif connectorType == 'hook':
            container, connector = utils.createHookConnector(name)
            parentGrp = None

        constrainedGrp = cmds.group(empty = True, name = f'{connector}_parentConstraint_grp')
        cmds.parent(connector, constrainedGrp, absolute = True)
        parentConstraint = cmds.parentConstraint(parentJoint, constrainedGrp, maintainOffset = False)[0]

        # Connect translateX to scaleX to drive stretch.
        cmds.connectAttr(f'{childJoint}.translateX', f'{constrainedGrp}.scaleX')

        scaleConstraint = cmds.scaleConstraint(self.moduleTransform, constrainedGrp, skip = ['x'], maintainOffset = False)[0]

        if parentGrp:
            cmds.parent(constrainedGrp, parentGrp, relative = True)

        # Add to containers.
        utils.addNodeToContainer(container, [constrainedGrp, parentConstraint, scaleConstraint], includeHierarchyBelow = True)
        utils.addNodeToContainer(self.containerName, container)

        # Parent the visual representation group under the hierarchy group.
        if connectorType == 'orientation':
            niceName = utils.stripLeadingNamespace(parentJoint)[1]
            attrName = f'{niceName}_orientation'
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

    def createRotationOrderUIControl(self, joint):
        layout = QtWidgets.QHBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignLeft)

        # Check if the joint exists before creating any UI elements
        if not cmds.objExists(joint):
            return layout  # Return an empty layout if the joint doesn't exist

        jointName = utils.stripAllNamespaces(joint)[1]

        label = QtWidgets.QLabel(jointName)
        label.setFixedWidth(80)  # Optional: Give label a fixed width for alignment
        combobox = QtWidgets.QComboBox()

        combobox.addItems(['xyz', 'yzx', 'zxy', 'xzy', 'yxz', 'zyx'])
        combobox.setFixedWidth(100)  # Optional: Give combobox a fixed width

        layout.addWidget(label)
        layout.addWidget(combobox)

        # 1. Initialize the combobox to the joint's current rotateOrder
        currentRotateOrder = cmds.getAttr(f'{joint}.rotateOrder')  # Get the current rotateOrder (integer value) from the joint
        combobox.setCurrentIndex(currentRotateOrder)  # Set the combobox's current index to match the joint's rotateOrder

        # 2. Connect the combobox's signal to a function that updates the joint's rotateOrder
        def update_joint_rotate_order(index):
            """
            This function will be called when the combobox's selected index changes.
            'index' is the new selected index (0-5) from the combobox.
            """
            # Set the joint's rotateOrder attribute in Maya
            # Always check if the joint still exists before attempting to set the attribute
            if cmds.objExists(joint):
                cmds.setAttr(f'{joint}.rotateOrder', index)
                print(f"Updated {joint}'s rotateOrder to: {combobox.currentText()} (index: {index})")
            else:
                print(f"Error: Cannot update rotateOrder for '{joint}'. Joint no longer exists.")

        # Connect the currentIndexChanged signal to our update function
        # This ensures that whenever the user selects a new item, the update_joint_rotate_order function is called.
        combobox.currentIndexChanged.connect(update_joint_rotate_order)

        # Return the layout. The combobox and its connection will persist because
        # the layout is added to a parent widget/layout in UI_custom.
        return layout

    def delete(self):

        cmds.lockNode(self.containerName, lock = False, lockUnpublished = False)

        blueprintsFolder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Blueprint')

        validModules = [module for module in utils.loadAllModulesFromDirectory(blueprintsFolder).keys()]
        validModuleNames = [module['name'] for module in utils.loadAllModulesFromDirectory(blueprintsFolder).values()]

        hookedModules = set()

        for jointInfo in self.jointInfo:
            joint = jointInfo[0]
            translationControl = self.getTranslationControl(f'{self.moduleNamespace}:{joint}')

            connections = cmds.listConnections(translationControl)

            for connection in connections:
                moduleInstance = utils.stripLeadingNamespace(connection)

                if moduleInstance:
                    moduleName, split, userSpecifiedName = moduleInstance[0].partition('__')
                    if moduleInstance[0] != self.moduleNamespace and moduleName in validModuleNames:
                        index = validModuleNames.index(moduleName)
                        hookedModules.add((validModules[index], userSpecifiedName))

        for module in hookedModules:
            mod = importlib.import_module(f'Blueprint.{module[0]}')
            moduleClass = getattr(mod, mod.CLASS_NAME)
            moduleInstance = moduleClass(module[1], None)
            moduleInstance.rehook(None)

        moduleTransform = f'{self.moduleNamespace}:module_transform'
        moduleTransformParent = cmds.listRelatives(moduleTransform, parent = True)

        cmds.delete(self.containerName)

        cmds.namespace(setNamespace = ':')
        cmds.namespace(removeNamespace = self.moduleNamespace)

        if moduleTransformParent != None:
            parentGroup = moduleTransformParent[0]

            children = cmds.listRelatives(parentGroup, children = True)
            children = cmds.ls(children, transforms = True)

            if len(children) == 0:
                cmds.select(parentGroup, replace = True)
                import System.groupSelected as groupSelected
                importlib.reload(groupSelected)

                groupSelected.UngroupSelected()

    def renameModuleInstance(self, newName):

        if newName == self.userSpecifiedName:
            return

        if utils.doesBlueprintUserSpecifiedNameExist(newName):
            QtWidgets.QMessageBox.information(None, "Name Conflict", f"Name {newName} already exists.\nAborting Rename.")
            return False

        else:
            newNamespace = f'{self.moduleName}__{newName}'
            cmds.lockNode(self.containerName, lock = False, lockUnpublished = False)
            cmds.namespace(setNamespace = ':')
            cmds.namespace(addNamespace = newNamespace)
            cmds.namespace(setNamespace = ':')

            cmds.namespace(moveNamespace = [self.moduleNamespace, newNamespace])
            cmds.namespace(removeNamespace = self.moduleNamespace)

            self.moduleNamespace = newNamespace
            self.containerName = f'{newNamespace}:module_container'
            cmds.lockNode(self.containerName, lock = True, lockUnpublished = True)

            return True

    def initializeHook(self, rootTranslationControl):
        unhookedLocator = cmds.spaceLocator(name = f'{self.moduleNamespace}:unhookedTarget')[0]
        cmds.pointConstraint(rootTranslationControl, unhookedLocator, offset = (0, 0.001, 0), name = f'{unhookedLocator}_pointConstraint')

        cmds.setAttr(f'{unhookedLocator}.visibility', 0)

        if self.hookObject is None:
            self.hookObject = unhookedLocator

        rootPos = cmds.xform(rootTranslationControl, query = True, worldSpace = True, translation = True)
        targetPos = cmds.xform(self.hookObject, query = True, worldSpace = True, translation = True)

        cmds.select(clear = True)

        rootJointWithoutNamespace = 'hook_root_joint'
        rootJoint = cmds.joint(name = f'{self.moduleNamespace}:{rootJointWithoutNamespace}', position = rootPos)
        cmds.setAttr(f'{rootJoint}.visibility', 0)

        targetJointWithoutNamespace = 'hook_target_joint'
        targetJoint = cmds.joint(name = f'{self.moduleNamespace}:{targetJointWithoutNamespace}', position = targetPos)
        cmds.setAttr(f'{targetJoint}.visibility', 0)

        cmds.joint(rootJoint, edit = True, orientJoint = 'xyz', secondaryAxisOrient = 'yup')

        hookGrp = cmds.group(rootJoint, unhookedLocator, name = f'{self.moduleNamespace}:hook_grp', parent = self.moduleGrp)
        hookContainer = utils.createContainer(name = f'{self.moduleNamespace}:hook_container', nodesIn = hookGrp, includeHierarchyBelow = True, includeShaders = True, includeTransform = True, includeShapes = True)

        utils.addNodeToContainer(self.containerName, hookContainer)

        for joint in [rootJoint, targetJoint]:
            jointName = utils.stripAllNamespaces(joint)[1]
            cmds.container(hookContainer, edit = True, publishAndBind = (f'{joint}.rotate', f'{jointName}_R'))

        ikNodes = utils.basicStretchyIK(rootJoint = rootJoint, endJoint = targetJoint, container = hookContainer, lockMinimumLength = False)
        ikHandle = ikNodes['ikHandle']
        rootLocator = ikNodes['rootLocator']
        endLocator = ikNodes['endLocator']
        poleVectorLocator = ikNodes['poleVectorObject']

        rootPointConstraint = cmds.pointConstraint(f'{rootTranslationControl}', rootJoint, maintainOffset = False, name = f'{rootJoint}_pointConstraint')[0]
        targetPointConstraint = cmds.pointConstraint(self.hookObject, endLocator, maintainOffset = False, name = f'{self.moduleNamespace}:hook_pointConstraint')[0]

        utils.addNodeToContainer(hookContainer, [rootPointConstraint, targetPointConstraint])

        for node in [ikHandle, rootLocator, endLocator, poleVectorLocator]:
            cmds.parent(node, hookGrp, absolute = True)
            cmds.setAttr(f'{node}.visibility', 0)

        container, connector, constrainedGrp = self.createConnector(connectorType = 'hook', name = rootJoint, parentJoint = rootJoint, childJoint = targetJoint)
        cmds.parent(constrainedGrp, hookGrp, absolute = True)

        cmds.container(self.containerName, edit = True, removeNode = container)
        utils.addNodeToContainer(hookContainer, container)

    def rehook(self, newHookObject):
        oldHookObject = self.findHookObject()

        self.hookObject = f'{self.moduleNamespace}:unhookedTarget'

        if newHookObject is not None:
            if newHookObject.find('_translation_control') != -1:
                splitString = newHookObject.split('_translation_control')
                if splitString[1] == '':
                    if utils.stripAllNamespaces(newHookObject)[0] != self.moduleNamespace:
                        self.hookObject = newHookObject

        if self.hookObject == oldHookObject:
            return

        self.unconstrainRootFromHook()

        cmds.lockNode(self.containerName, lock = False, lockUnpublished = False)

        hookConstraint = f'{self.moduleNamespace}:hook_pointConstraint'
        cmds.connectAttr(f'{self.hookObject}.parentMatrix[0]', f'{hookConstraint}.target[0].targetParentMatrix', force = True)
        cmds.connectAttr(f'{self.hookObject}.translate', f'{hookConstraint}.target[0].targetTranslate', force = True)
        cmds.connectAttr(f'{self.hookObject}.rotatePivot', f'{hookConstraint}.target[0].targetRotatePivot', force = True)
        cmds.connectAttr(f'{self.hookObject}.rotatePivotTranslate', f'{hookConstraint}.target[0].targetRotateTranslate', force = True)

        cmds.lockNode(self.containerName, lock = True, lockUnpublished = True)

    def findHookObject(self):
        hookConstraint = f'{self.moduleNamespace}:hook_pointConstraint'
        sourceAttr = cmds.connectionInfo(f'{hookConstraint}.target[0].targetParentMatrix', sourceFromDestination = True)
        sourceNode = str(sourceAttr).rpartition('.')[0]

        return sourceNode

    def findHookObjectForLock(self):
        hookObject = self.findHookObject()

        if hookObject == f'{self.moduleNamespace}:unhookedTarget':
            hookObject = None
        else:
            self.rehook(None)

        return hookObject

    def snapRootToHook(self):
        rootControl = self.getTranslationControl(f'{self.moduleNamespace}:{self.jointInfo[0][0]}')
        hookObject = self.findHookObject()

        if hookObject == f'{self.moduleNamespace}:unhookedTarget':
            return

        hookObjectPos = cmds.xform(hookObject, query = True, worldSpace = True, translation = True)
        cmds.xform(rootControl, worldSpace = True, absolute = True, translation = hookObjectPos)

    def constrainRootToHook(self):
        rootControl = self.getTranslationControl(f'{self.moduleNamespace}:{self.jointInfo[0][0]}')
        hookObject = self.findHookObject()

        if hookObject == f'{self.moduleNamespace}:unhookedTarget':
            return

        cmds.lockNode(self.containerName, lock = False, lockUnpublished = False)

        cmds.pointConstraint(hookObject, rootControl, maintainOffset = False, name = f'{rootControl}_hookConstraint')
        cmds.setAttr(f'{rootControl}.translate', lock = True)
        cmds.setAttr(f'{rootControl}.visibility', lock = False)
        cmds.setAttr(f'{rootControl}.visibility', 0)
        cmds.setAttr(f'{rootControl}.visibility', lock = True)

        cmds.select(clear = True)

        cmds.lockNode(self.containerName, lock = True, lockUnpublished = True)

    def unconstrainRootFromHook(self):
        cmds.lockNode(self.containerName, lock = False, lockUnpublished = False)

        rootControl = self.getTranslationControl(f'{self.moduleNamespace}:{self.jointInfo[0][0]}')
        rootControl_hookConstraint = f'{rootControl}_hookConstraint'

        if cmds.objExists(rootControl_hookConstraint):
            cmds.delete(rootControl_hookConstraint)
            cmds.setAttr(f'{rootControl}.translate', lock = False)
            cmds.setAttr(f'{rootControl}.visibility', lock = False)
            cmds.setAttr(f'{rootControl}.visibility', 1)
            cmds.setAttr(f'{rootControl}.visibility', lock = True)

            cmds.select(rootControl, replace = True)
            cmds.setToolTo('moveSuperContext')


        cmds.lockNode(self.containerName, lock = True, lockUnpublished = True)

    def isRootConstrained(self):
        rootControl = self.getTranslationControl(f'{self.moduleNamespace}:{self.jointInfo[0][0]}')
        rootControl_hookConstraint = f'{rootControl}_hookConstraint'

        return cmds.objExists(rootControl_hookConstraint)

    def canModuleBeMirrored(self):
        return self.canBeMirrored
