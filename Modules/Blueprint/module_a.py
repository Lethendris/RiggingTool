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
        """Initialize the module with a user-specified name."""
        self.moduleName = MODULE_NAME
        self.userSpecifiedName = userSpecifiedName
        self.moduleNameSpace = f'{self.moduleName}__{self.userSpecifiedName}'
        self.containerName = f'{self.moduleNameSpace}:module_container'

        self.jointInfo = [
            ['root_joint', [0.0, 0.0, 0.0]],
            ['end_joint', [4.0, 0.0, 0.0]],
            ['end_joint2', [8.0, 0.0, 0.0]]
        ]

    def install(self):

        cmds.namespace(setNamespace = ':')
        cmds.namespace(addNamespace = self.moduleNameSpace)

        self.jointsGrp = cmds.group(empty = True, name = f'{self.moduleNameSpace}:joints_grp')
        self.moduleGrp = cmds.group(self.jointsGrp, name = f'{self.moduleNameSpace}:module_grp')

        cmds.container(name = self.containerName, addNode = [self.moduleGrp], includeHierarchyBelow = True)
        cmds.select(clear = True)

        joints = []
        for index, (jointName, jointPos) in enumerate(self.jointInfo):
            parentName = ''

            if index > 0:
                parentName = f'{self.moduleNameSpace}:{self.jointInfo[index - 1][0]}'
                cmds.select(parentName, replace = True)

            jointName_full = cmds.joint(name = f'{self.moduleNameSpace}:{jointName}', position = jointPos)
            joints.append(jointName_full)

            cmds.container(self.containerName, edit = True, addNode = [jointName_full])

            cmds.container(self.containerName, edit = True, publishAndBind = (f'{jointName_full}.rotate', f'{jointName}_R'))
            cmds.container(self.containerName, edit = True, publishAndBind = (f'{jointName_full}.rotateOrder', f'{jointName}_rotateOrder'))

            if index > 0:
                cmds.joint(parentName, edit = True, orientJoint = 'xyz', secondaryAxisOrient = 'yup')

        cmds.parent(joints[0], self.jointsGrp, absolute = True)


        translationControls = []
        for joint in joints:
            translationControls.append(self.createTranslationControlAtJoint(joint))

        rootJoint_pointConstraint = cmds.pointConstraint(translationControls[0], joints[0], maintainOffset = False, name = f'{joints[0]}_pointConstraint')
        cmds.container(self.containerName, edit = True, addNode = rootJoint_pointConstraint)


        # setup stretchy joint segments
        for index in range(len(joints) - 1):
            self.setupStretchyJointSegment(joints[index], joints[index + 1])


        cmds.lockNode(self.containerName, lock = True, lockUnpublished = True)


    def createTranslationControlAtJoint(self, joint):

        translationControlFile = f'{os.environ["RIGGING_TOOL_ROOT"]}/ControlObjects/Blueprint/translation_control.ma'

        cmds.file(translationControlFile, i = True)
        try:
            cmds.delete('sceneConfigurationScriptNode')
        except:
            pass

        container = cmds.rename('translation_control_container', f'{joint}_translation_control_container')
        cmds.container(self.containerName, edit = True, addNode = [container])


        for node in cmds.container(container, query = True, nodeList = True):
            cmds.rename(node, f'{joint}_{node}', ignoreShape = True)

        control = f'{joint}_translation_control'

        jointPos = cmds.xform(joint, query = True, worldSpace = True, translation = True)
        cmds.xform(control, worldSpace = True, absolute = True, translation = jointPos)

        niceName = utils.stripLeadingNamespace(joint)[1]
        attrName = f'{niceName}_T'

        cmds.container(container, edit = True, publishAndBind = (f'{control}.translate', attrName))
        cmds.container(self.containerName, edit = True, publishAndBind = (f'{container}.{attrName}', attrName))

        return control

    def getTranslationControl(self, jointName):
        return f'{jointName}_translation_control'

    def setupStretchyJointSegment(self, parentJoint, childJoint):
        parentTranslationControl = self.getTranslationControl(parentJoint)
        childTranslationControl = self.getTranslationControl(childJoint)

        poleVectorLocator = cmds.spaceLocator(name = f'{parentTranslationControl}_poleVectorLocator')[0]
        poleVectorLocatorGrp = cmds.group(poleVectorLocator, name = f'{poleVectorLocator}_parentConstraintGrp')

        cmds.parent(poleVectorLocatorGrp, self.moduleGrp, absolute = True)
        parentConstraint = cmds.parentConstraint(parentTranslationControl, poleVectorLocatorGrp, maintainOffset = False)[0]

        cmds.setAttr(f'{poleVectorLocator}.visibility', 0)
        cmds.setAttr(f'{poleVectorLocator}.ty', -0.5)

        ikNodes = utils.basicStretchyIK(rootJoint = parentJoint, endJoint = childJoint, container = self.containerName, lockMinimumLength = False, poleVectorObject = poleVectorLocator,
                        scaleCorrectionAttribute = None)

        ikHandle = ikNodes['ikHandle']
        rootLocator = ikNodes['rootLocator']
        endLocator = ikNodes['endLocator']

        childPointConstraint = cmds.pointConstraint(childTranslationControl, endLocator, maintainOffset = False, name = f'{endLocator}_pointConstraint')[0]

        cmds.container(self.containerName, edit = True, addNode = [poleVectorLocatorGrp, parentConstraint, childPointConstraint], includeHierarchyBelow = True)

        for node in [ikHandle, rootLocator, endLocator]:
            cmds.parent(node, self.jointsGrp, absolute = True)
            cmds.setAttr(f'{node}.visibility', 0)


