import System.blueprint as blueprintMod
import maya.cmds as cmds
import os
import importlib
importlib.reload(blueprintMod)

MODULE_NAME = "SingleJointSegment"
MODULE_DESCRIPTION = "Creates 2 joints with control for 1st joint's orientation and rotation order. Ideal use: Clavicle/Shoulder"
MODULE_ICON = os.path.join(os.environ['RIGGING_TOOL_ROOT'], 'Icons/_singleJointSeg.xpm')  # Optional

class SingleJointSegment(blueprintMod.Blueprint):
    def __init__(self, userSpecifiedName):
        print('derived class constructor')
        jointInfo = [['root_joint', [0.0, 0.0, 0.0]], ['end_joint', [4.0, 0.0, 0.0]]]

        super().__init__(MODULE_NAME, userSpecifiedName, jointInfo)

    # def install_custom(self, joints):
    #     # NON default functionality
    #     # self.createOrientationControl(joints[0], joints[1])



