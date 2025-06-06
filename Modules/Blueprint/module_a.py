import os

import maya.cmds as cmds

MODULE_NAME = "ModuleA"
MODULE_DESCRIPTION = "Module A Description"
MODULE_ICON = "path/to/icon.png"  # Optional


class ModuleA:
    def __init__(self, userSpecifiedName):
        """Initialize the module with a user-specified name."""
        self.moduleName = MODULE_NAME
        self.userSpecifiedName = userSpecifiedName
        self.moduleNameSpace = f'{self.moduleName}__{self.userSpecifiedName}'
        self.moduleSet = f'{self.moduleNameSpace}:module_set'

        self.jointInfo = [
            ['root_joint', [0.0, 0.0, 0.0]],
            ['end_joint', [4.0, 0.0, 0.0]],
            ['end_joint2', [8.0, 0.0, 0.0]]
        ]

    def install(self):
        """Create the joint hierarchy and set up the module in the scene."""
        cmds.namespace(setNamespace=':')
        cmds.namespace(add=self.moduleNameSpace)

        self.moduleSet = cmds.sets(name = self.moduleSet)

        self.jointsGrp = cmds.group(em=True, name=f'{self.moduleNameSpace}:joints_grp')
        self.moduleGrp = cmds.group(self.jointsGrp, name=f'{self.moduleNameSpace}:module_grp')

        cmds.select(clear=True)

        joints = []
        for index, (jointName, jointPos) in enumerate(self.jointInfo):
            fullJointName = f'{self.moduleNameSpace}:{jointName}'

            if index > 0:
                parentName = f'{self.moduleNameSpace}:{self.jointInfo[index - 1][0]}'
                cmds.select(parentName, replace=True)

            joint = cmds.joint(n=fullJointName, p=jointPos)
            joints.append(joint)

            if index > 0:
                cmds.joint(parentName, edit=True, orientJoint='xyz', secondaryAxisOrient='yup')

        # Parent the root joint under the joints group
        cmds.parent(joints[0], self.jointsGrp, absolute=True)

        translationControls = []
        for joint in joints:
            translationControls.append(self.createTranslationControlAtJoint(joint))

        # Create a set containing all relevant module nodes
        cmds.sets(self.moduleGrp, self.jointsGrp, *joints, addElement=self.moduleSet)


    def createTranslationControlAtJoint(self, joint):
        translationControlFile = f'{os.environ["RIGGING_TOOL_ROOT"]}/ControlObjects/Blueprint/translation_control.fbx'
        nodes = cmds.file(translationControlFile, i = True, type="FBX", returnNewNodes = True)
        for node in nodes:
            cmds.sets(node, addElement = self.moduleSet)

        translationControl = cmds.rename('translation_control', f'{joint}_translation_control')




