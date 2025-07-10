# System/groupSelected.py

import maya.cmds as cmds
from PySide6 import QtWidgets, QtCore
import System.utils as utils
import importlib

# Ensure the utils module is up-to-date
importlib.reload(utils)


class GroupSelectedDialog(QtWidgets.QDialog):
    """
    A dialog for grouping selected module transforms or existing groups.
    This class follows a singleton pattern to ensure only one instance is open at a time.
    """
    # Class variable to hold the single instance of the dialog
    _instance = None

    def __init__(self, parent = None):
        """
        Initializes the dialog UI widgets and sets up signal/slot connections.
        This method does NOT perform any Maya scene operations. It only builds the UI structure.
        """
        super().__init__(parent)
        self.setWindowTitle("Group Selected Modules")
        self.setObjectName("GroupSelectedDialog")
        self.setFixedSize(300, 150)

        # Initialize attributes that will be populated by scene-interaction logic later
        self.objectsToGroup = []
        self.tempGroupTransform = None

        # Call the UI setup method to create the widgets and layouts
        self.setupUI()

    def setupUI(self):
        """
        Creates and arranges all the UI widgets for the dialog.
        This method is called once from __init__ to build the UI structure.
        """
        mainLayout = QtWidgets.QVBoxLayout(self)
        mainLayout.setSpacing(10)

        # --- Layouts ---
        nameLayout = QtWidgets.QHBoxLayout()
        nameLayout.setSpacing(4)
        positionLayout = QtWidgets.QHBoxLayout()
        positionLayout.setSpacing(4)
        buttonLayout = QtWidgets.QHBoxLayout()
        buttonLayout.setSpacing(4)

        # --- Widgets ---
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

        # --- Assemble Layouts ---
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

        # --- Connect Signals to Slots ---
        self.acceptButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)
        self.lastSelectedButton.clicked.connect(self.createAtLastSelected)
        self.averagePositionButton.clicked.connect(self.createAtAveragePosition)

    def initializeSceneData(self):
        """
        Performs all Maya scene setup required before showing the dialog.
        This includes finding the selection and creating the temporary group representation.
        This method is called every time the dialog is shown.

        Returns:
            bool: True on success, False on failure (e.g., nothing valid selected).
        """
        if not self.findSelectionToGroup():
            return False

        self.createTemporaryGroupRepresentation()
        self.createAtLastSelected()

        cmds.select(self.tempGroupTransform)
        cmds.setToolTo('moveSuperContext')

        return True

    def reject(self):
        """
        Handles the cancel action. Deletes the temporary group and closes the dialog.
        """
        if self.tempGroupTransform and cmds.objExists(self.tempGroupTransform):
            cmds.delete(self.tempGroupTransform)
        super().reject()

    def accept(self):
        """
        Handles the accept action. Creates the final group and closes the dialog.
        """
        groupName = self.groupLineEdit.text()
        if self.createGroup(groupName):
            super().accept()

    def createGroup(self, groupName):
        """
        Creates the final group in the scene based on the temporary representation.
        """
        fullGroupName = f'Group__{groupName}'

        if cmds.objExists(fullGroupName):
            QtWidgets.QMessageBox.warning(self, "Name Conflict", f"Group '{groupName}' already exists.")
            return None

        groupTransform = cmds.rename(self.tempGroupTransform, fullGroupName)
        self.tempGroupTransform = None  # Clear the temp attribute after renaming

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
            if cmds.objExists(c):
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
            if cmds.objExists(c):
                cmds.lockNode(c, lock = True, lockUnpublished = True)

        cmds.setToolTo('moveSuperContext')
        cmds.select(groupTransform, replace = True)

        return groupTransform

    def addGroupToContainer(self, group):
        """
        Adds the newly created group and its attributes to the main group container.
        """
        groupContainer = 'Group_container'
        utils.addNodeToContainer(container = groupContainer, nodesIn = [group])

        groupName = group.partition('Group__')[2]

        cmds.container(groupContainer, edit = True, publishAndBind = (f'{group}.translate', f'{groupName}_t'))
        cmds.container(groupContainer, edit = True, publishAndBind = (f'{group}.rotate', f'{groupName}_r'))
        cmds.container(groupContainer, edit = True, publishAndBind = (f'{group}.globalScale', f'{groupName}_globalScale'))

    def findSelectionToGroup(self):
        """
        Finds valid module transforms or existing groups from the current selection.
        Returns True if valid objects are found, otherwise False.
        """
        selectedObjects = cmds.ls(selection = True, transforms = True)
        self.objectsToGroup = [obj for obj in selectedObjects if obj.endswith('module_transform') or obj.startswith('Group__')]
        return bool(self.objectsToGroup)

    def createTemporaryGroupRepresentation(self):
        """
        Creates a temporary visual representation for the group being created.
        """
        self.tempGroupTransform = utils.createModuleTransformControl('Group__tempGroupTransform__')

        cmds.connectAttr(f'{self.tempGroupTransform}.scaleY', f'{self.tempGroupTransform}.scaleX')
        cmds.connectAttr(f'{self.tempGroupTransform}.scaleY', f'{self.tempGroupTransform}.scaleZ')

        for attr in ['scaleX', 'scaleZ', 'visibility']:
            cmds.setAttr(f'{self.tempGroupTransform}.{attr}', lock = True, keyable = False)

        cmds.aliasAttr('globalScale', f'{self.tempGroupTransform}.scaleY')

    def createAtLastSelected(self):
        """
        Positions the temporary group at the location of the last selected object.
        """
        if not self.objectsToGroup: return
        last_selected = self.objectsToGroup[-1]
        controlPos = cmds.xform(last_selected, query = True, worldSpace = True, translation = True)
        cmds.xform(self.tempGroupTransform, worldSpace = True, absolute = True, translation = controlPos)

    def createAtAveragePosition(self):
        """
        Positions the temporary group at the average position of all selected objects.
        """
        if not self.objectsToGroup: return
        controlPos = [0.0, 0.0, 0.0]

        for obj in self.objectsToGroup:
            objPos = cmds.xform(obj, query = True, worldSpace = True, translation = True)
            controlPos[0] += objPos[0]
            controlPos[1] += objPos[1]
            controlPos[2] += objPos[2]

        numberOfObjects = len(self.objectsToGroup)
        if numberOfObjects > 0:
            controlPos[0] /= numberOfObjects
            controlPos[1] /= numberOfObjects
            controlPos[2] /= numberOfObjects

        cmds.xform(self.tempGroupTransform, worldSpace = True, absolute = True, translation = controlPos)

    def createGroupAtSpecified(self, name, targetGroup, parent):
        self.createTemporaryGroupRepresentation()

        parentConstraint = cmds.parentConstraint(targetGroup, self.tempGroupTransform ,maintainOffset = False)[0]
        cmds.delete(parentConstraint)

        scale = cmds.getAttr(f'{targetGroup}.globalScale')
        cmds.setAttr(f'{self.tempGroupTransform}.globalScale', scale)

        if parent:
            cmds.parent(self.tempGroupTransform, parent, absolute = True)

        newGroup = self.createGroup(name)

        return newGroup

    @classmethod
    def showUI(cls, parent = None):
        """
        The main entry point for showing the dialog.
        It handles instance creation, data initialization, and display.
        """
        if cls._instance and cls._instance.isVisible():
            cls._instance.raise_()
            cls._instance.activateWindow()
            return

        if cls._instance:
            cls._instance.deleteLater()

        cls._instance = cls(parent = parent)

        if not cls._instance.initializeSceneData():
            print("No valid objects selected to group.")
            cls._instance.deleteLater()
            cls._instance = None
            return

        cls._instance.show()


class UngroupSelected:
    """
    A class to handle the ungrouping of selected Blueprint groups.
    Instantiating this class performs the ungroup operation immediately.
    """

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
            if cmds.objExists(moduleContainer):
                moduleContainers.append(moduleContainer)

        for container in moduleContainers:
            if cmds.objExists(container):
                cmds.lockNode(container, lock = False, lockUnpublished = False)

        for group in filteredGroups:
            children = cmds.listRelatives(group, children = True, fullPath = True) or []
            if children:
                cmds.ungroup(group, absolute = True)
            else:
                cmds.delete(group)

            groupName = group.partition('__')[2]
            for attr in ['t', 'r', 'globalScale']:
                attr_name = f'{groupName}_{attr}'
                if cmds.container(groupContainer, query = True, publishName = attr_name):
                    cmds.container(groupContainer, edit = True, unbindAndUnpublish = f'{group}.{attr}')

            parentGroup = cmds.listRelatives(group, parent = True)
            if parentGroup:
                parentGroup = parentGroup[0]
                children = cmds.listRelatives(parentGroup, children = True, type = 'transform') or []
                if not children:
                    cmds.select(parentGroup, replace = True)
                    UngroupSelected()  # Recursively ungroup empty parent

        if cmds.objExists(groupContainer) and not cmds.container(groupContainer, query = True, nodeList = True):
            cmds.delete(groupContainer)

        for container in moduleContainers:
            if cmds.objExists(container):
                cmds.lockNode(container, lock = True, lockUnpublished = True)

    def findChildModules(self, group):
        """
        Recursively finds all Blueprint module namespaces parented under a given group.
        """
        modules = []
        children = cmds.listRelatives(group, children = True, type = 'transform') or []
        for child in children:
            if child.startswith('Group__'):
                modules.extend(self.findChildModules(child))
            else:
                moduleNamespaceInfo = utils.stripLeadingNamespace(child)
                if moduleNamespaceInfo and moduleNamespaceInfo[1] == 'module_transform':
                    modules.append(moduleNamespaceInfo[0])
        return modules
