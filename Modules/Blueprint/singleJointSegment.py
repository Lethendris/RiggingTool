import System.blueprint as blueprintMod
import maya.cmds as cmds
import os
import importlib
importlib.reload(blueprintMod)

CLASS_NAME = "SingleJointSegment"
MODULE_DESCRIPTION = "Creates 2 joints with control for 1st joint's orientation and rotation order. Ideal use: Clavicle/Shoulder"
MODULE_ICON = os.path.join(os.environ['RIGGING_TOOL_ROOT'], 'Icons/_singleJointSeg.xpm')  # Optional

class SingleJointSegment(blueprintMod.Blueprint):
    def __init__(self, userSpecifiedName, hookObj):
        jointInfo = [['root_joint', [0.0, 0.0, 0.0]], ['end_joint', [4.0, 0.0, 0.0]]]

        super().__init__(CLASS_NAME, userSpecifiedName, jointInfo, hookObj)

    def install_custom(self, joints):
        pass

    def UI_custom(self):
        joints = self.getJoints()
        layout = self.createRotationOrderUIControl(joints[0])

        self.parentLayout.addLayout(layout)


    def lockPhase1(self):
        # Gather and return all required information from this module's control objects
        # joint positions = list of joint positions, from root down the hierarchy
        # joint orientations = list of orientations, or a list of axis information (orientJoint and secondaryAxisOrient for joint command)
        # these are passed in the following tuple : (orientations, None) or (None, axisInfo)
        # jointRotationOrders = list of joint rotation orders (integer values gathered with getAttr)
        # jointPreferredAngles = list of joint preferred angles, optional (can pass None)
        # hookObject = self.findHookObjectForLock()
        # rootTransform = a bool, either True or False. True = R, T, and S on root joint. False = R only.
        # moduleInfo = (jointPositions, jointOrientations, jointRotationOrders, jointPreferredAngles, hookObject, rootTransform)
        # return moduleInfo

        jointPositions = []
        jointOrientationValues = []
        jointRotationOrders = []

        joints = self.getJoints()

        for joint in joints:
            jointPositions.append(cmds.xform(joint, query = True, worldSpace = True, translation = True))


        cleanParent = f'{self.moduleNamespace}:joints_grp'

        orientationInfo = self.orientationControlledJoint_getOrientation(joints[0], cleanParent)
        cmds.delete(orientationInfo[1])
        jointOrientationValues.append(orientationInfo[0])
        jointOrientations = (jointOrientationValues, None)

        jointRotationOrders.append(cmds.getAttr(f'{joints[0]}.rotateOrder'))

        jointPreferredAngles = None
        hookObject = self.findHookObjectForLock()
        rootTransform = False

        moduleInfo = (jointPositions, jointOrientations, jointRotationOrders, jointPreferredAngles, hookObject, rootTransform)
        return moduleInfo

