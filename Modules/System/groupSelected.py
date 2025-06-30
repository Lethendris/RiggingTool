# System/groupSelected.py
import maya.cmds as cmds
from PySide6 import QtWidgets, QtCore, QtGui
import System.utils as utils
import importlib
importlib.reload(utils)

class GroupSelectedDialog(QtWidgets.QDialog):
    """
    A dialog for grouping selected module transforms or existing groups.
    """
    # Class variable to hold the single instance of the dialog
    _instance = None

    def __init__(self, parent = None):
        super().__init__(parent)
        self.setWindowTitle("Group Selected Modules")
        self.setObjectName("GroupSelectedDialog")
        self.setFixedSize(300, 150)

        self.objectsToGroup = []  # Initialize the list of objects to be grouped

        self.setupUI()

        self.findSelectionToGroup()
        self.createTemporaryGroupRepresentation()
        self.createAtLastSelected()

        cmds.select(self.tempGroupTransform)
        cmds.setToolTo('moveSuperContext')


    def setupUI(self):
        mainLayout = QtWidgets.QVBoxLayout(self)
        mainLayout.setSpacing(10)

        nameLayout = QtWidgets.QHBoxLayout()
        nameLayout.setSpacing(4)
        positionLayout = QtWidgets.QHBoxLayout()
        positionLayout.setSpacing(4)
        buttonLayout = QtWidgets.QHBoxLayout()
        buttonLayout.setSpacing(4)

        self.groupNameLabel = QtWidgets.QLabel('Group Name:')
        self.groupNameLabel.setMinimumWidth(80)

        self.groupLineEdit = QtWidgets.QLineEdit('group')
        self.groupLineEdit.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)

        self.positionLabel = QtWidgets.QLabel('Position At:')
        self.positionLabel.setMinimumWidth(80)

        self.lastSelectedButton = QtWidgets.QPushButton('Last Selected')
        self.lastSelectedButton.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.averagePositionButton = QtWidgets.QPushButton('Average Position')
        self.averagePositionButton.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)

        self.acceptButton = QtWidgets.QPushButton('Accept')
        self.cancelButton = QtWidgets.QPushButton('Cancel')

        nameLayout.addWidget(self.groupNameLabel)
        nameLayout.addWidget(self.groupLineEdit)

        positionLayout.addWidget(self.positionLabel)
        positionLayout.addWidget(self.lastSelectedButton)
        positionLayout.addWidget(self.averagePositionButton)

        buttonLayout.addWidget(self.acceptButton)
        buttonLayout.addWidget(self.cancelButton)

        mainLayout.addLayout(nameLayout)
        mainLayout.addLayout(positionLayout)
        mainLayout.addStretch()
        mainLayout.addLayout(buttonLayout)

        self.acceptButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)

        self.lastSelectedButton.clicked.connect(self.createAtLastSelected)
        self.averagePositionButton.clicked.connect(self.createAtAveragePosition)

    def reject(self):
        super().reject()

        cmds.delete(self.tempGroupTransform)

    def accept(self):


        groupName = self.groupLineEdit.text()
        if self.createGroup(groupName):
            super().accept()


    def createGroup(self, groupName):

        fullGroupName = f'Group__{groupName}'

        if cmds.objExists(fullGroupName):
            QtWidgets.QMessageBox.question(self, "Name Conflict", f"Group {groupName} already exists.",QtWidgets.QMessageBox.StandardButton.Ok | QtWidgets.QMessageBox.StandardButton.Cancel)
            return None

        groupTransform = cmds.rename(self.tempGroupTransform, fullGroupName)
        groupContainer = 'Group_container'

        if not cmds.objExists(groupContainer):
            utils.createContainer(name = groupContainer)

        containers = [groupContainer]

        for obj in self.objectsToGroup:
            if obj.startswith('Group__'):
                continue

            objNamespace = utils.stripLeadingNamespace(obj)[0]
            containers.append(f'{objNamespace}:module_container')

        for c in containers:
            cmds.lockNode(c, lock = False, lockUnpublished = False)

        if self.objectsToGroup:
            tempGroup = cmds.group(self.objectsToGroup, absolute = True)

            groupParent = cmds.listRelatives(tempGroup, parent = True)

            if groupParent:
                cmds.parent(groupTransform, groupParent[0], absolute = True)

            cmds.parent(self.objectsToGroup, groupTransform, absolute = True)

            cmds.delete(tempGroup)

        self.addGroupToContainer(groupTransform)

        for c in containers:
            cmds.lockNode(c, lock = True, lockUnpublished = True)

        cmds.setToolTo('moveSuperContext')
        cmds.select(groupTransform, replace = True)

        return groupTransform

    def addGroupToContainer(self, group):
        groupContainer = 'Group_container'
        utils.addNodeToContainer(container = groupContainer, nodesIn = [group])

        groupName = group.partition('Group__')[2]

        cmds.container(groupContainer, edit = True, publishAndBind = (f'{group}.translate', f'{groupName}_t'))
        cmds.container(groupContainer, edit = True, publishAndBind = (f'{group}.rotate', f'{groupName}_r'))
        cmds.container(groupContainer, edit = True, publishAndBind = (f'{group}.globalScale', f'{groupName}_globalScale'))

    def findSelectionToGroup(self):
        selectedObjects = cmds.ls(selection = True, transforms = True)

        self.objectsToGroup = []

        for obj in selectedObjects:
            if obj.endswith('module_transform') or obj.startswith('Group__'):
                self.objectsToGroup.append(obj)

    def createTemporaryGroupRepresentation(self):
        self.tempGroupTransform = utils.createModuleTransformControl('Group__tempGroupTransform__')

        cmds.connectAttr(f'{self.tempGroupTransform}.scaleY', f'{self.tempGroupTransform}.scaleX')
        cmds.connectAttr(f'{self.tempGroupTransform}.scaleY', f'{self.tempGroupTransform}.scaleZ')

        for attr in ['scaleX', 'scaleZ', 'visibility']:
            cmds.setAttr(f'{self.tempGroupTransform}.{attr}', lock = True, keyable = False)

        cmds.aliasAttr('globalScale', f'{self.tempGroupTransform}.scaleY')

    def createAtLastSelected(self):
        controlPos = cmds.xform(f'{self.objectsToGroup[len(self.objectsToGroup) - 1]}', query = True, worldSpace = True, translation = True)
        cmds.xform(self.tempGroupTransform, worldSpace = True, absolute = True, translation = controlPos)

    def createAtAveragePosition(self):
        controlPos = [0.0, 0.0, 0.0]

        for obj in self.objectsToGroup:
            objPos = cmds.xform(obj, query = True, worldSpace = True, translation = True)
            controlPos[0] += objPos[0]
            controlPos[1] += objPos[1]
            controlPos[2] += objPos[2]

        numberOfObjects = len(self.objectsToGroup)

        controlPos[0] /= numberOfObjects
        controlPos[1] /= numberOfObjects
        controlPos[2] /= numberOfObjects

        cmds.xform(self.tempGroupTransform, worldSpace = True, absolute = True, translation = controlPos)

    @classmethod
    def showUI(cls, parent = None):
        if cls._instance and cls._instance.isVisible():
            cls._instance.raise_()
            cls._instance.activateWindow()
            return

        if cls._instance:
            cls._instance.deleteLater()

        cls._instance = cls(parent = parent)

        if not cls._instance.objectsToGroup:
            return

        cls._instance.show()

class UngroupSelected:
    def __init__(self):
        selectedObjects = cmds.ls(selection = True, transforms = True)

        filteredGroups = [obj for obj in selectedObjects if obj.startswith('Group__')]

        if not filteredGroups:
            return

        groupContainer = 'Group_container'

        modules = []
        for group in filteredGroups:
            modules.extend(self.findChildModules(group))

        moduleContainers = [groupContainer]

        for module in modules:
            moduleContainer = f'{module}:module_container'
            moduleContainers.append(moduleContainer)

        for container in moduleContainers:
            cmds.lockNode(container, lock = False, lockUnpublished = False)

        for group in filteredGroups:
            numChildren = len(cmds.listRelatives(group, children = True))
            if numChildren > 1:
                cmds.ungroup(group, absolute = True)

            for attr in ['t', 'r', 'globalScale']:
                cmds.container(groupContainer, edit = True, unbindAndUnpublish = f'{group}.{attr}')

            parentGroup = cmds.listRelatives(group, parent = True)

            cmds.delete(group)
            cmds.delete(groupContainer)

            if parentGroup:
                parentGroup = parentGroup[0]
                children = cmds.listRelatives(parentGroup, children = True)
                children = cmds.ls(children, transforms = True)

                if len(children) == 0:
                    cmds.select(parentGroup, replace = True)
                    UngroupSelected()

        for container in moduleContainers:
            if cmds.objExists(container):
                cmds.lockNode(container, lock = True, lockUnpublished = True)

    def findChildModules(self, group):
        modules = []
        children = cmds.listRelatives(group, children = True)

        if children:
            for child in children:
                moduleNamespaceInfo = utils.stripLeadingNamespace(child)
                if moduleNamespaceInfo:
                    modules.append(moduleNamespaceInfo[0])

                elif 'Group__' in child:
                    modules.extend(self.findChildModules(child))

        return modules


