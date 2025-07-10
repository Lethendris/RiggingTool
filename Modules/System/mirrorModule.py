import maya.cmds as cmds
from PySide6 import QtWidgets, QtCore
from shiboken6 import wrapInstance
import System.utils as utils
import maya.OpenMayaUI as omui
import os
import importlib
import time

importlib.reload(utils)

class MirrorProgressDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Mirroring Progress')
        self.setFixedSize(300, 100)
        self.setWindowModality(QtCore.Qt.ApplicationModal) # Blocks all other windows
        self.setWindowFlags(QtCore.Qt.Tool | QtCore.Qt.WindowTitleHint | QtCore.Qt.CustomizeWindowHint) # Minimal window

        mainLayout = QtWidgets.QVBoxLayout(self)
        self.progressLabel = QtWidgets.QLabel("Initializing...")
        self.progressBar = QtWidgets.QProgressBar()
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(100)

        mainLayout.addWidget(self.progressLabel)
        mainLayout.addWidget(self.progressBar)

    def updateProgress(self, value, message=""):
        self.progressBar.setValue(value)
        if message:
            self.progressLabel.setText(message)
        QtWidgets.QApplication.processEvents() # Process events to update UI

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

        self.moduleNames = [f"instance_{i}" for i in range(1, 15)]

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
        self.setWindowTitle('Mirror Module(s)')  # Changed from 'Mirror Module Settings'
        self.setFixedSize(350, 400)
        self.setWindowModality(QtCore.Qt.WindowModal)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.Tool)

        # --- Main Layout for the Dialog ---
        mainLayout = QtWidgets.QVBoxLayout(self)
        mainLayout.setContentsMargins(5, 5, 5, 5)
        mainLayout.setSpacing(8)

        # --- 1. Create the Scroll Area ---
        scrollArea = QtWidgets.QScrollArea()
        scrollArea.setWidgetResizable(True)  # Allows the inner widget to resize
        scrollArea.setFocusPolicy(QtCore.Qt.NoFocus)  # Prevents scroll area from stealing focus
        scrollArea.setStyleSheet("QScrollArea { border: 0px; }")  # Optional: remove border

        # --- 2. Create the Container Widget for ALL scrollable content ---
        scrollContentWidget = QtWidgets.QWidget()
        # This layout will hold all the sections that need to scroll
        self.scrollContentLayout = QtWidgets.QVBoxLayout(scrollContentWidget)
        self.scrollContentLayout.setContentsMargins(0, 0, 0, 0)  # No extra margins inside scroll area
        self.scrollContentLayout.setSpacing(8)
        self.scrollContentLayout.setAlignment(QtCore.Qt.AlignTop)  # Align content to top

        # --- Populate Scrollable Content ---

        # --- Mirror Plane GroupBox ---
        mirrorPlaneGroupBox = QtWidgets.QGroupBox('Plane')
        mirrorPlaneLayout = QtWidgets.QHBoxLayout()
        mirrorPlaneLayout.setAlignment(QtCore.Qt.AlignCenter)
        mirrorPlaneLayout.setSpacing(50)
        mirrorPlaneGroupBox.setLayout(mirrorPlaneLayout)

        # mirrorPlaneLayout.addWidget(QtWidgets.QLabel("Mirror Plane:")) # Label inside groupbox
        self.xyRadioButton = QtWidgets.QRadioButton("XY")
        self.yzRadioButton = QtWidgets.QRadioButton("YZ")
        self.xzRadioButton = QtWidgets.QRadioButton("XZ")
        self.xyRadioButton.setChecked(True)  # Default to YZ plane

        self.mirrorPlaneButtonGroup = QtWidgets.QButtonGroup(self)
        self.mirrorPlaneButtonGroup.addButton(self.xyRadioButton, 0)
        self.mirrorPlaneButtonGroup.addButton(self.yzRadioButton, 1)
        self.mirrorPlaneButtonGroup.addButton(self.xzRadioButton, 2)

        mirrorPlaneLayout.addWidget(self.xyRadioButton)
        mirrorPlaneLayout.addWidget(self.yzRadioButton)
        mirrorPlaneLayout.addWidget(self.xzRadioButton)
        self.scrollContentLayout.addWidget(mirrorPlaneGroupBox)  # Add to scrollable content

        # --- Mirrored Names GroupBox ---
        mirroredNamesGroupBox = QtWidgets.QGroupBox("Name(s)")
        mirroredNamesLayout = QtWidgets.QVBoxLayout()
        mirroredNamesGroupBox.setLayout(mirroredNamesLayout)

        namesGridLayout = QtWidgets.QGridLayout()
        namesGridLayout.setColumnStretch(0, 0)  # Original name label
        namesGridLayout.setColumnStretch(1, 1)  # Line edit
        namesGridLayout.setSpacing(5)
        namesGridLayout.setAlignment(QtCore.Qt.AlignTop)

        self.mirrorNames = {}

        for i, module_name in enumerate(self.moduleNames):
            label = QtWidgets.QLabel(f"{module_name} >>")
            label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            lineEdit = QtWidgets.QLineEdit(f"{module_name}_mirror")
            self.mirrorNames[module_name] = lineEdit
            namesGridLayout.addWidget(label, i, 0)
            namesGridLayout.addWidget(lineEdit, i, 1)

        mirroredNamesLayout.addLayout(namesGridLayout)
        self.scrollContentLayout.addWidget(mirroredNamesGroupBox)  # Add to scrollable content

        # --- Dynamic Mirror Settings ---
        if self.sameMirrorSettingsForAll:
            # Pass the scrollContentLayout to the function
            self.generateMirrorFunctionControls(self.scrollContentLayout, None)
        else:
            for module_name in self.moduleNames:
                # Pass the scrollContentLayout and module name
                self.generateMirrorFunctionControls(self.scrollContentLayout, module_name)

        scrollArea.setWidget(scrollContentWidget)
        mainLayout.addWidget(scrollArea)

        # --- Bottom Buttons (fixed, outside scroll area) ---
        buttonLayout = QtWidgets.QHBoxLayout()
        self.mirrorButton = QtWidgets.QPushButton("Accept")
        self.closeButton = QtWidgets.QPushButton("Cancel")

        buttonLayout.addWidget(self.mirrorButton)
        buttonLayout.addWidget(self.closeButton)
        mainLayout.addLayout(buttonLayout)

        # --- Connections ---
        self.closeButton.clicked.connect(self.reject)
        self.mirrorButton.clicked.connect(self.accept)

    def accept(self):
        super().accept()
        self.moduleInfo = []

        self.mirrorPlane = self.mirrorPlaneButtonGroup.checkedButton().text()

        for i in range(len(self.modules)):
            originalModule = self.modules[i]
            originalModuleName = self.moduleNames[i]

            originalModulePrefix = originalModule.partition("__")[0]
            mirroredModuleUserSpecifiedName = self.mirrorNames[originalModuleName].text()
            mirroredModuleName = f'{originalModulePrefix}__{mirroredModuleUserSpecifiedName}'

            if utils.doesBlueprintUserSpecifiedNameExist(mirroredModuleUserSpecifiedName):
                QtWidgets.QMessageBox.question(self, "Name Conflict", f'Name {mirroredModuleUserSpecifiedName} already exists, aborting mirror.', QtWidgets.QMessageBox.StandardButton.Ok)
                return

            if self.sameMirrorSettingsForAll:
                translationSettingText = self.globalSettings['translationButtonGroup'].checkedButton().text()
                rotationSettingText = self.globalSettings['rotationButtonGroup'].checkedButton().text()

            else:
                translationSettingText = self.moduleSettings[originalModuleName]['translationButtonGroup'].checkedButton().text()
                rotationSettingText = self.moduleSettings[originalModuleName]['rotationButtonGroup'].checkedButton().text()

            self.moduleInfo.append([originalModule, mirroredModuleName, self.mirrorPlane, translationSettingText, rotationSettingText])

        self.mirrorModules()

    def mirrorModules(self):

        mirrorProgressDialog = MirrorProgressDialog(parent = self.parent)
        mirrorProgressDialog.show()

        mirrorModulesProgress = 0

        phase1_proportion = 15
        phase2_proportion = 70
        phase3_proportion = 15

        mirrorProgressDialog.updateProgress(5, "Collecting module data...")
        # time.sleep(0.1)  # Simulate a small delay


        blueprintsFolder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Blueprint')

        validModules = [module for module in utils.loadAllModulesFromDirectory(blueprintsFolder).keys()]
        validModuleNames = [module['name'] for module in utils.loadAllModulesFromDirectory(blueprintsFolder).values()]

        for module in self.moduleInfo:
            moduleName = module[0].partition('__')[0]

            if moduleName in validModuleNames:
                index = validModuleNames.index(moduleName)
                module.append(validModules[index])

        mirrorModulesProgress_increment = phase1_proportion / len(self.moduleInfo)

        for module in self.moduleInfo:

            userSpecifiedName = module[0].partition('__')[2]

            mod = importlib.import_module(f'Blueprint.{module[5]}')
            importlib.reload(mod)

            moduleClass = getattr(mod, mod.CLASS_NAME)
            moduleInstance = moduleClass(userSpecifiedName, None)

            hookObject = moduleInstance.findHookObject()
            newHookObject = None

            hookModule = utils.stripLeadingNamespace(hookObject)[0]

            hookFound = False

            for m in self.moduleInfo:

                if hookModule == m[0]:
                    hookFound = True

                    if m == module:
                        continue

                    hookObjectName = utils.stripLeadingNamespace(hookObject)[1]
                    newHookObject = f'{m[1]}:{hookObjectName}'

            if not hookFound:
                newHookObject = hookObject

            module.append(newHookObject)

            hookConstrained = moduleInstance.isRootConstrained()
            module.append(hookConstrained)

            mirrorModulesProgress += mirrorModulesProgress_increment
            progressMessage = f"Mirroring: {module[0]}"
            mirrorProgressDialog.updateProgress(mirrorModulesProgress, progressMessage)
            # time.sleep(0.1)

        mirrorModulesProgress_increment = phase2_proportion / len(self.moduleInfo)

        for module in self.moduleInfo:
            newUserSpecifiedName = module[1].partition('__')[2]
            mod = importlib.import_module(f'Blueprint.{module[5]}')
            importlib.reload(mod)

            moduleClass = getattr(mod, mod.CLASS_NAME)
            moduleInstance = moduleClass(newUserSpecifiedName, None)
            moduleInstance.mirror(module[0], module[2], module[3], module[4])

            mirrorModulesProgress += mirrorModulesProgress_increment

            progressMessage = f"Mirroring: {module[0]}"
            # mirrorProgressDialog.updateProgress(mirrorModulesProgress, progressMessage)
            # time.sleep(0.1)

        mirrorModulesProgress_increment = phase3_proportion / len(self.moduleInfo)

        for module in self.moduleInfo:
            newUserSpecifiedName = module[1].partition('__')[2]
            mod = importlib.import_module(f'Blueprint.{module[5]}')
            importlib.reload(mod)

            moduleClass = getattr(mod, mod.CLASS_NAME)
            moduleInstance = moduleClass(newUserSpecifiedName, None)

            moduleInstance.rehook(module[6])

            hookConstrained = module[7]
            if hookConstrained:
                moduleInstance.constrainRootToHook()

            mirrorModulesProgress += mirrorModulesProgress_increment
            mirrorProgressDialog.updateProgress(mirrorModulesProgress, progressMessage)

        # if self.group:
        #     cmds.lockNode('Group_container', lock = False, lockUnpublished = False)
        #
        #     groupParent = cmds.listRelatives(self.group, parent = True)
        #
        #     if groupParent:
        #         groupParent = groupParent[0]
        #
        #     self.processGroup(self.group, groupParent)
        #
        #     cmds.lockNode('Group_container', lock = True, lockUnpublished = True)
        #
        #     cmds.select(clear = True)

        mirrorProgressDialog.updateProgress(100, "Mirroring complete!")
        time.sleep(1)  # Give user time to read "complete"
        mirrorProgressDialog.close()

    def generateMirrorFunctionControls(self, parentLayout, moduleName):
        """
                Generates a QGroupBox with mirror function and orientation controls.
                Adds it to the given parent_layout.
                """
        textLabel = 'Settings'
        if moduleName:
            textLabel = f'{moduleName} Settings'

        mirrorSettingsGroupBox = QtWidgets.QGroupBox(textLabel)
        mirrorSettingsGridLayout = QtWidgets.QGridLayout()
        mirrorSettingsGroupBox.setLayout(mirrorSettingsGridLayout)

        # Row 0: Mirror Function
        mirrorSettingsGridLayout.addWidget(QtWidgets.QLabel("Mirror Rotation:"), 0, 0, QtCore.Qt.AlignRight)
        self.behaviorRadioButton = QtWidgets.QRadioButton("Behavior")
        self.orientationRadioButton = QtWidgets.QRadioButton("Orientation")
        self.behaviorRadioButton.setChecked(True)

        # QButtonGroup for Mirror Function (create unique names if per-module)
        self.rotationButtonGroup = QtWidgets.QButtonGroup(self)
        self.rotationButtonGroup.addButton(self.behaviorRadioButton, 0)
        self.rotationButtonGroup.addButton(self.orientationRadioButton, 1)

        mirrorSettingsGridLayout.addWidget(self.behaviorRadioButton, 0, 1)
        mirrorSettingsGridLayout.addWidget(self.orientationRadioButton, 0, 2)

        # Row 1: Orientation/World Space
        mirrorSettingsGridLayout.addWidget(QtWidgets.QLabel("Mirror Translation:"), 1, 0, QtCore.Qt.AlignRight)
        self.mirroredRadioButton = QtWidgets.QRadioButton("Mirrored")
        self.worldSpaceRadioButton = QtWidgets.QRadioButton("World Space")
        self.mirroredRadioButton.setChecked(True)

        # QButtonGroup for Orientation/World Space (create unique names if per-module)
        self.translationButtonGroup = QtWidgets.QButtonGroup(self)
        self.translationButtonGroup.addButton(self.mirroredRadioButton, 0)
        self.translationButtonGroup.addButton(self.worldSpaceRadioButton, 1)

        mirrorSettingsGridLayout.addWidget(self.mirroredRadioButton, 1, 1)
        mirrorSettingsGridLayout.addWidget(self.worldSpaceRadioButton, 1, 2)

        mirrorSettingsGridLayout.setColumnStretch(0, 0)
        mirrorSettingsGridLayout.setColumnStretch(1, 0)
        mirrorSettingsGridLayout.setColumnStretch(2, 1)

        # Add the generated GroupBox to the parent_layout
        parentLayout.addWidget(mirrorSettingsGroupBox)

        # Store references to these dynamically created widgets if you need to retrieve their values later
        if moduleName:
            if not hasattr(self, 'moduleSettings'):
                self.moduleSettings = {}
            self.moduleSettings[moduleName] = {
                'behaviorButton': self.behaviorRadioButton,
                'orientationButton': self.orientationRadioButton,
                'mirroredButton': self.mirroredRadioButton,
                'worldSpaceButton': self.worldSpaceRadioButton,
                'translationButtonGroup': self.translationButtonGroup,
                'rotationButtonGroup': self.rotationButtonGroup,
            }
        else:  # sameMirrorSettingsForAll
            self.globalSettings = {
                'behaviorButton': self.behaviorRadioButton,
                'orientationButton': self.orientationRadioButton,
                'mirroredButton': self.mirroredRadioButton,
                'worldSpaceButton': self.worldSpaceRadioButton,
                'translationButtonGroup': self.translationButtonGroup,
                'rotationButtonGroup': self.rotationButtonGroup
            }

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
        moduleInstance = moduleClass('null', None)

        # Check if the method exists before calling
        if hasattr(moduleInstance, 'canModuleBeMirrored'):
            return moduleInstance.canModuleBeMirrored()
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

    def processGroup(self, group, parent):
        import System.groupSelected as groupSelected
        importlib.reload(groupSelected)

        tempGroup = cmds.duplicate(group, parentOnly = True, inputConnections = True)[0]
        emptyGroup = cmds.group(empty = True)

        parent(tempGroup, emptyGroup, absolute = True)
        scaleAxis = 'scaleX'

        if self.mirrorPlane == 'XZ':
            scaleAxis = 'scaleY'

        elif self.mirrorPlane == 'XY':
            scaleAxis = 'scaleZ'

        cmds.setAttr(f'{emptyGroup}.{scaleAxis}', -1)





