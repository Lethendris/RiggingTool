import maya.cmds as cmds

MODULE_NAME = "ModuleA"
MODULE_DESCRIPTION = "Module A Description"
MODULE_ICON = "path/to/icon.png"  # Optional

class ModuleA:

    def __init__(self, userSpecifiedName):
        self.moduleName = MODULE_NAME
        self.userSpecifiedName = userSpecifiedName

        self.moduleNameSpace = f'{self.moduleName}__{self.userSpecifiedName}'

        self.moduleSet = f'{self.moduleNameSpace}:module_set'

        self.jointInfo = [['root_joint', [0.0, 0.0, 0.0]], ['end_joint', [4.0, 0.0, 0.0]], ['end_joint2', [8.0, 0.0, 0.0]]]

    def install(self):
        cmds.namespace(setNamespace = ':')
        cmds.namespace(add = self.moduleNameSpace)

        self.jointsGrp = cmds.group(em = True, name = f'{self.moduleNameSpace}:joints_grp')
        self.moduleGrp = cmds.group(self.jointsGrp, name = f'{self.moduleNameSpace}:module_grp')


        cmds.select(clear = True)

        index = 0
        joints = []

        for j in self.jointInfo:
            jointName = j[0]
            jointPos = j[1]
            parentJnt = ''

            if index > 0:
                parentJnt = f'{self.moduleNameSpace}:{self.jointInfo[index - 1][0]}'
                cmds.select(parentJnt, replace = True)


            jointName_full = cmds.joint(n = f'{self.moduleNameSpace}:{jointName}', p = jointPos)
            joints.append(jointName_full)

            if index > 0:
                cmds.joint(parentJnt, edit = True, orientJoint = 'xyz', secondaryAxisOrient = 'yup')

            index += 1

        cmds.parent(joints[0], self.jointsGrp, absolute = True)

        for j in joints:
            print(j)

        cmds.sets(self.moduleGrp, self.jointsGrp, joints, name = self.moduleSet)


