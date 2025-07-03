import maya.cmds as cmds
from PySide6 import QtWidgets, QtCore
from shiboken6 import wrapInstance
import System.utils as utils
import maya.OpenMayaUI as omui
import os
import importlib
importlib.reload(utils)

class MirrorModule(QtWidgets.QDialog):
    def __init__(self, parent = None):  # Accept the parent UI instance

        super().__init__(parent)
        self.parent = parent  # Store the parent UI

        selection = cmds.ls(selection = True, transforms = True)

        if not selection:
            return

        firstSelected = selection[0]

        self.modules = []
        self.group = None

        if firstSelected.startswith('Group__'):
            self.group = firstSelected
            self.modules = self.findSubModules(firstSelected)
        else:
            moduleNamespaceInfo = utils.stripLeadingNamespace(firstSelected)
            if moduleNamespaceInfo:
                self.modules.append(moduleNamespaceInfo[0])

        tempModuleList = []

        for module in self.modules:
            if self.isModuleMirror(module):
                # Parent the message box to the main Maya window
                QtWidgets.QMessageBox.information(parent, "Mirror Module(s)", 'Cannot mirror a previously mirrored module, aborting mirror.')
                return
            if not self.canModuleBeMirrored(module):
                print(f'Module {module} is of a module type that can not be mirrored. Skipping module.')
            else:
                tempModuleList.append(module)

        self.modules = tempModuleList

        if self.modules:
            self.showUI()

    def showUI(self):
        self.moduleNames = []

        for module in self.modules:
            self.moduleNames.append(module.partition('__')[2])

        self.sameMirrorSettingsForAll = False

        if len(self.modules) > 1:
            msgBox = QtWidgets.QMessageBox(parent = self.parent)  # Parent the message box
            msgBox.setWindowTitle("Mirror Multiple Modules")
            msgBox.setText(f"{len(self.modules)} modules are selected. Do you want to mirror them all the same way or set each one individually?")
            msgBox.setIcon(QtWidgets.QMessageBox.Question)
            sameForAllBtn = msgBox.addButton("Same For All", QtWidgets.QMessageBox.AcceptRole)
            individuallyBtn = msgBox.addButton("Individually", QtWidgets.QMessageBox.ActionRole)
            cancelBtn = msgBox.addButton("Cancel", QtWidgets.QMessageBox.RejectRole)

            msgBox.exec()

            if msgBox.clickedButton() == cancelBtn:
                return
            elif msgBox.clickedButton() == sameForAllBtn:
                self.sameMirrorSettingsForAll = True

        self.setupMirrorUI()

        self.exec_()

    def setupMirrorUI(self):

        self.setWindowTitle('Mirror Module Settings')
        self.setMinimumSize(300, 400)
        self.setWindowModality(QtCore.Qt.WindowModal)
        # self.setWindowFlags(self.windowFlags() | QtCore.Qt.Tool)

        mainLayout = QtWidgets.QVBoxLayout(self)
        mainLayout.setContentsMargins(5,5,5,5)

        mirrorPlaneGroupBox = QtWidgets.QGroupBox("Mirror Plane:")
        mirrorPlaneLayout = QtWidgets.QHBoxLayout()
        mirrorPlaneGroupBox.setLayout(mirrorPlaneLayout)
        # Mirror plane buttons

        self.xyRadioButton  = QtWidgets.QRadioButton("XY")
        self.yzRadioButton  = QtWidgets.QRadioButton("YZ")
        self.xzRadioButton  = QtWidgets.QRadioButton("XZ")
        self.yzRadioButton.setChecked(True)

        mirrorPlaneLayout.addWidget(self.xyRadioButton)
        mirrorPlaneLayout.addWidget(self.yzRadioButton)
        mirrorPlaneLayout.addWidget(self.xzRadioButton)

        scrollArea = QtWidgets.QScrollArea()
        scrollArea.setWidgetResizable(True)  # Allows the inner widget to resize
        scrollArea.setFocusPolicy(QtCore.Qt.NoFocus)  # Prevents scroll area from stealing focus
        scrollArea.setStyleSheet("QScrollArea { border: 0px; }")

        scrollWidget = QtWidgets.QWidget()

        self.mirrorModulesLayout = QtWidgets.QVBoxLayout(scrollWidget)# Set layout on the widget

        mirroredNamesGroupBox = QtWidgets.QGroupBox("Mirrored Name(s):")

        # The GroupBox will have its own layout to hold the scroll area
        groupBoxLayout = QtWidgets.QHBoxLayout()
        groupBoxLayout.setContentsMargins(2,2,2,2)
        mirroredNamesGroupBox.setLayout(groupBoxLayout)

        for module_name in self.moduleNames:
            layout = QtWidgets.QHBoxLayout()
            layout.setSpacing(2)
            label = QtWidgets.QLabel(f"{module_name} >>")
            lineEdit = QtWidgets.QLineEdit(f"{module_name}_mirror")
            lineEdit.setFixedWidth(120)
            layout.addWidget(label)
            layout.addWidget(lineEdit)
            self.mirrorModulesLayout.addLayout(layout)

        scrollArea.setWidget(scrollWidget)
        # Add the scroll area to the GroupBox's layout
        groupBoxLayout.addWidget(scrollArea)
        # Add the GroupBox to the main dialog's layout        mainLayout.addWidget(mirroredNamesGroupBox)

        mainLayout.addWidget(mirrorPlaneGroupBox)
        mainLayout.addWidget(mirroredNamesGroupBox)

        # add to main layout
        mainLayout.addStretch()

    def canModuleBeMirrored(self, module):
        blueprintsFolder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Blueprint')

        validModules = [module for module in utils.loadAllModulesFromDirectory(blueprintsFolder).keys()]
        validModuleNames = [module['name'] for module in utils.loadAllModulesFromDirectory(blueprintsFolder).values()]

        moduleName = module.partition('__')[0]

        if not moduleName in validModuleNames:
            return False

        index = validModuleNames.index(moduleName)
        mod = importlib.import_module(f'Blueprint.{validModules[index]}')
        importlib.reload(mod)

        moduleClass = getattr(mod, mod.CLASS_NAME)
        moduleInst = moduleClass('null', None)

        # Check if the method exists before calling
        if hasattr(moduleInst, 'canModuleBeMirrored'):
            return moduleInst.canModuleBeMirrored()
        return False  # Default to False if method doesn't exist

    def isModuleMirror(self, module):
        moduleGrp = f'{module}:module_grp'
        if cmds.objExists(moduleGrp):
            return cmds.attributeQuery('mirrorLinks', node = moduleGrp, exists = True)
        return False

    def findSubModules(self, group):
        returnModules = []

        children = cmds.listRelatives(group, children = True, type = 'transform')

        if children:
            for child in children:
                if child.startswith('Group__'):
                    returnModules.extend(self.findSubModules(child))
                else:
                    namespaceInfo = utils.stripAllNamespaces(child)
                    if namespaceInfo and namespaceInfo[1] == 'module_transform':
                        module = namespaceInfo[0]
                        returnModules.append(module)

        return returnModules