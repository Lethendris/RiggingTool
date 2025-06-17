import os

import maya.cmds as cmds

MODULE_NAME = "ModuleA"
MODULE_DESCRIPTION = "Module A Description"
MODULE_ICON = "path/to/icon.png"  # Optional

import System.utils as utils
import importlib

importlib.reload(utils)


class ModuleA:
    def __init__(self, userSpecifiedName):
        """
        Initialize the ModuleA instance with a given user-specified name.

        Args:
            userSpecifiedName (str): Custom name to uniquely identify this module instance.
        """

        self.moduleName = MODULE_NAME  # Constant module base name (should be defined externally).
        self.userSpecifiedName = userSpecifiedName
        self.moduleNameSpace = f'{self.moduleName}__{self.userSpecifiedName}'
        self.containerName = f'{self.moduleNameSpace}:module_container'

        # Default joint information: names and world-space positions.
        self.jointInfo = [['root_joint', [0.0, 0.0, 0.0]], ['end_joint', [4.0, 0.0, 0.0]]]

    def install(self):
        """
        Set up the module in the Maya scene by creating joints, control groups,
        containers, and applying stretchy IK functionality.
        """

        # Ensure we’re in the root namespace and create a unique one for this module.
        cmds.namespace(setNamespace = ':')
        cmds.namespace(addNamespace = self.moduleNameSpace)

        # Create groups to organize joints and visual representation.
        self.jointsGrp = cmds.group(empty = True, name = f'{self.moduleNameSpace}:joints_grp')
        self.hierarchyConnectorsGrp = cmds.group(empty = True, name = f'{self.moduleNameSpace}:hierarchyConnectors_grp')
        self.orientationConnectorsGrp = cmds.group(empty = True, name = f'{self.moduleNameSpace}:orientationConnectors_grp')
        self.moduleGrp = cmds.group(self.jointsGrp, self.hierarchyConnectorsGrp, self.orientationConnectorsGrp, name = f'{self.moduleNameSpace}:module_grp')

        # Create a container and include the hierarchy.
        cmds.container(name = self.containerName, addNode = [self.moduleGrp], includeHierarchyBelow = True)

        cmds.select(clear = True)

        # Create joints as defined in self.jointInfo.

        joints = []

        for index, (jointName, jointPos) in enumerate(self.jointInfo):
            parentName = ''

            if index > 0:
                parentName = f'{self.moduleNameSpace}:{self.jointInfo[index - 1][0]}'
                cmds.select(parentName, replace = True)

            jointName_full = cmds.joint(name = f'{self.moduleNameSpace}:{jointName}', position = jointPos)
            joints.append(jointName_full)

            # Hide joint from view
            # cmds.setAttr(f'{jointName_full}.visibility', 0)

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
        controlGrpFile = os.path.join(os.environ["RIGGING_TOOL_ROOT"], 'ControlObjects/Blueprint/controlGroup_control.ma')
        cmds.file(controlGrpFile, i = True)

        self.moduleTransform = cmds.rename('controlGroup_control', f'{self.moduleNameSpace}:module_transform')

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

        return [container, connector, constrainedGrp]