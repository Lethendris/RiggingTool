import os

import maya.cmds as cmds

import System.utils as utils
import importlib
importlib.reload(utils)

class Blueprint:
    def __init__(self, moduleName, userSpecifiedName, jointInfo):
        print('base class constructor')

        """
        Initialize the ModuleA instance with a given user-specified name.

        Args:
            userSpecifiedName (str): Custom name to uniquely identify this module instance.
        """

        self.moduleName = moduleName # Constant module base name (should be defined externally).
        self.userSpecifiedName = userSpecifiedName
        self.jointInfo = jointInfo
        self.moduleNameSpace = f'{self.moduleName}__{self.userSpecifiedName}'
        self.containerName = f'{self.moduleNameSpace}:module_container'

    # Methods intended for overriding by derived class
    def install_custom(self, joints):
        print('install_custom() methods is not implemented by derived class.')


    # BASE CLASS METHODS
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
        self.hierarchyRepresentationGrp = cmds.group(empty = True, name = f'{self.moduleNameSpace}:hierarchyRepresentation_grp')
        self.orientationControlsGrp = cmds.group(empty = True, name = f'{self.moduleNameSpace}:orientationControls_grp')
        self.moduleGrp = cmds.group(self.jointsGrp, self.hierarchyRepresentationGrp, self.orientationControlsGrp, name = f'{self.moduleNameSpace}:module_grp')

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
            self.setupStretchyJointSegment(joints[index], joints[index + 1])

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

        translationControlFile = f'{os.environ["RIGGING_TOOL_ROOT"]}/ControlObjects/Blueprint/translation_control.ma'

        # Import the translation control file.
        cmds.file(translationControlFile, i = True)

        # Rename the imported container.
        container = cmds.rename('translation_control_container', f'{joint}_translation_control_container')
        utils.addNodeToContainer(self.containerName, container)

        # Rename nodes in the imported control for uniqueness.
        for node in cmds.container(container, query = True, nodeList = True):
            cmds.rename(node, f'{joint}_{node}', ignoreShape = True)

        control = f'{joint}_translation_control'

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

    def setupStretchyJointSegment(self, parentJoint, childJoint):
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

        self.createHierarchyRepresentation(parentJoint, childJoint)

    def createHierarchyRepresentation(self, parentJoint, childJoint):

        """
        Visual representation for joint hierarchy between two joints.

        Args:
            parentJoint (str): Start joint of the hierarchy link.
            childJoint (str): End joint of the hierarchy link.
        """

        nodes = self.createStretchyObject(objectRelativeFilePath = 'ControlObjects/Blueprint/hierarchy_representation.ma', objectContainerName = 'hierarchy_representation_container', objectName = 'hierarchy_representation', parentJoint = parentJoint, childJoint = childJoint)
        constrainedGrp = nodes[2]

        # Parent the visual representation group under the hierarchy group.
        cmds.parent(constrainedGrp, self.hierarchyRepresentationGrp, relative = True)



    def createStretchyObject(self, objectRelativeFilePath, objectContainerName, objectName, parentJoint, childJoint):
        """
        Create a stretchy object (e.g., visual line) between two joints.

        Args:
            objectRelativeFilePath (str): Relative path to the control file.
            objectContainerName (str): Base container name for the imported object.
            objectName (str): Name of the main control object.
            parentJoint (str): Joint to constrain the object to.
            childJoint (str): Joint whose translation drives the stretch.

        Returns:
            list: [container name, object name, constraint group name]
        """
        objectFile = os.path.join(os.environ['RIGGING_TOOL_ROOT'], objectRelativeFilePath)
        cmds.file(objectFile, i = True)

        # Rename container and nodes for uniqueness.
        objectContainer = cmds.rename(objectContainerName, f'{parentJoint}_{objectContainerName}')

        for node in cmds.container(objectContainer, query = True, nodeList = True):
            cmds.rename(node, f'{parentJoint}_{node}', ignoreShape = True)

        object = f'{parentJoint}_{objectName}'

        # Group and constrain object.
        constrainedGrp = cmds.group(empty = True, name = f'{object}_parentConstraint_grp')
        cmds.parent(object, constrainedGrp, absolute = True)

        parentConstraint = cmds.parentConstraint(parentJoint, constrainedGrp, maintainOffset = False)[0]

        # Connect translateX to scaleX to drive stretch.
        cmds.connectAttr(f'{childJoint}.translateX', f'{constrainedGrp}.scaleX')

        scaleConstraint = cmds.scaleConstraint(self.moduleTransform, constrainedGrp, skip = ['x'], maintainOffset = False)[0]

        # Add to containers.
        utils.addNodeToContainer(objectContainer, [constrainedGrp, parentConstraint, scaleConstraint], includeHierarchyBelow = True)
        utils.addNodeToContainer(self.containerName, objectContainer)

        return [objectContainer, object, constrainedGrp]

    def initializeModuleTransform(self, rootPos):
        print(os.environ["RIGGING_TOOL_ROOT"])
        controlGrpFile = os.path.join(os.environ["RIGGING_TOOL_ROOT"], 'ControlObjects/Blueprint/controlGroup_control.ma')
        print(controlGrpFile)
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

    def deleteHierarchyRepresentation(self, parentJoint):
        hieararchyContainer = f'{parentJoint}_hierarchy_representation_container'
        cmds.delete(hieararchyContainer)


    def createOrientationControl(self, parentJoint, childJoint):

        self.deleteHierarchyRepresentation(parentJoint)

        nodes = self.createStretchyObject(objectRelativeFilePath = 'ControlObjects/Blueprint/orientation_control.ma', objectContainerName = 'orientation_control_container', objectName = 'orientation_control', parentJoint = parentJoint, childJoint = childJoint)
        orientationContainer = nodes[0]
        orientationControl = nodes[1]
        constrainedGrp = nodes[2]

        cmds.parent(constrainedGrp, self.orientationControlsGrp, relative = True)

        parentJointWithoutNamespace = utils.stripAllNamespaces(parentJoint)[1]
        attrName = f'{parentJointWithoutNamespace}_orientation'
        cmds.container(orientationContainer, edit = True, publishAndBind = (f'{orientationControl}.rotateX', attrName))
        cmds.container(self.containerName, edit = True, publishAndBind = (f'{orientationContainer}.{attrName}', attrName))

        return orientationControl




