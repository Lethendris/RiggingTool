"""
Blueprint Module UI for Maya
This module creates a UI for managing rigging modules with PySide2 in Maya.
It dynamically loads module information from Python files in a specified directory.
"""
import importlib.util
import os.path
import sys

from PySide6 import QtCore, QtWidgets, QtGui
from shiboken6 import wrapInstance
import maya.OpenMayaUI as omui
import maya.cmds as cmds

from . import utils
importlib.reload(utils)

projectRoot = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if projectRoot not in sys.path:
    sys.path.append(projectRoot)

def mayaMainWindow():
    """Return the Maya main window widget as a Python object"""
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

class NonInteractivePlainTextEdit(QtWidgets.QPlainTextEdit):
    def __init__(self, text = '', parent = None):
        super().__init__(text, parent)

        self.setReadOnly(True)
        self.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.setCursor(QtCore.Qt.ArrowCursor)
        self.viewport().setCursor(QtCore.Qt.ArrowCursor)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: #242424;
                color: #ffffff;
                border: 2px solid #555;
                border-radius: 8px;
                padding: 6px;
                font-family: Consolas, monospace;
                font-size: 12px;
            }
        """)

    def keyPressEvent(self, event):
        event.accept()

class RoundedIconButton(QtWidgets.QPushButton):
    def __init__(self, *args, radius=8, **kwargs):
        super().__init__(*args, **kwargs)
        self.radius = radius
        self.setIconSize(QtCore.QSize(64, 64))
        self.setMinimumSize(64, 64)
        self.setMaximumSize(64, 64)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        # Clip to rounded rect
        path = QtGui.QPainterPath()
        rect = QtCore.QRectF(self.rect())
        path.addRoundedRect(rect, self.radius, self.radius)
        painter.setClipPath(path)

        # Draw button background
        option = QtWidgets.QStyleOptionButton()
        self.initStyleOption(option)
        self.style().drawControl(QtWidgets.QStyle.CE_PushButtonBevel, option, painter, self)

        # Draw icon centered
        icon = self.icon()
        if not icon.isNull():
            iconSize = self.iconSize()
            rect = self.rect()
            x = (rect.width() - iconSize.width()) // 2
            y = (rect.height() - iconSize.height()) // 2
            icon.paint(painter, x, y, iconSize.width(), iconSize.height())

        # Draw button text if any
        if self.text():
            textRect = self.rect()
            painter.setPen(self.palette().color(QtGui.QPalette.ButtonText))
            painter.drawText(textRect, QtCore.Qt.AlignCenter, self.text())

        painter.end()


class ModuleWidget(QtWidgets.QWidget):
    def __init__(self, moduleName, description, iconPath = None, moduleObject = None, parent = None):
        super().__init__(parent = parent)

        self.moduleName = moduleName
        self.description = description
        self.iconPath = iconPath if iconPath else ""
        self.moduleObject = moduleObject

        self.setupUI()


    def setupUI(self):

        # MAIN LAYOUT
        self.mainLayout = QtWidgets.QHBoxLayout(self)
        self.mainLayout.setContentsMargins(5, 0, 5, 0)
        self.mainLayout.setSpacing(5)
        self.setFixedHeight(90)

        # WIDGETS
        self.imageButton = RoundedIconButton() # image button
        self.imageButton.setFixedSize(64, 64)
        self.imageButton.setIconSize(QtCore.QSize(64, 64))
        self.imageButton.setStyleSheet("""
            QPushButton {
                border: 2px solid #555;
                border-radius: 8px;
                background-color: #3498db;
                color: white;
                padding: 6px;
                background-image: url("path/to/icon.png");
                background-repeat: no-repeat;
                background-position: center;
                background-origin: content;
            }
            QPushButton:hover {
                background-color: #2980b9;
                border-color: #1abc9c;
            }
        """)

        if self.iconPath and os.path.exists(self.iconPath): # set icon for button if available
            icon = QtGui.QIcon(self.iconPath)
            self.imageButton.setIcon(icon)
        else:

            self.imageButton.setText('Icon') # default icon


        self.nameLabel = QtWidgets.QLabel(self.moduleName) # module name label

        self.descriptionField = NonInteractivePlainTextEdit(self.description) # Description text field
        self.descriptionField.setFixedHeight(64)

        # CREATE LAYOUTS
        self.moduleField = QtWidgets.QVBoxLayout() # module description layout
        self.moduleField.setContentsMargins(5, 0, 0, 0)


        # ADD WIDGETS
        self.mainLayout.addWidget(self.imageButton, alignment = QtCore.Qt.AlignBottom)
        self.moduleField.addWidget(self.nameLabel, alignment = QtCore.Qt.AlignCenter)
        self.moduleField.addWidget(self.descriptionField)

        # CONNECT WIDGETS
        self.imageButton.clicked.connect(self.moduleImageButtonClicked)

        # ADD TO MAIN LAYOUT
        self.mainLayout.addLayout(self.moduleField)


    def moduleImageButtonClicked(self):
        self.installModule()

    def installModule(self):
        baseName = 'instance_'

        cmds.namespace(setNamespace = ':')
        rawNamespaces = cmds.namespaceInfo(listOnlyNamespaces = True)

        # Strip prefix before '__' if present
        strippedNamespaces = [ns.partition('__')[2] if '__' in ns else ns for ns in rawNamespaces]

        newSuffix = utils.findHighestTrailingNumber(strippedNamespaces, baseName) + 1

        userSpecifiedName = f'{baseName}{newSuffix}'


        if self.moduleObject and hasattr(self.moduleObject, self.moduleName):
            moduleClass = getattr(self.moduleObject, self.moduleName)
            moduleInstance = moduleClass(userSpecifiedName)
            moduleInstance.install()

            moduleTransform = f'{self.moduleName}__{userSpecifiedName}:module_transform'
            cmds.select(moduleTransform)
            cmds.setToolTo('moveSuperContext')

class Blueprint_UI(QtWidgets.QDialog):

    ui_instance = None

    def __init__(self, modulesDir = None, parent = None):

        self.moduleInstance = None

        if parent is None:
            try:
                parent = mayaMainWindow()
            except:
                pass

        self.modulesDir = modulesDir

        super().__init__(parent = parent)

        # MAIN WINDOW FLAGS
        self.setWindowTitle('Blueprint Module UI')
        self.setObjectName("Blueprint Module UI")
        self.setFixedSize(400,600)

        # SETUP UI
        self.setupUI()

        # LOAD MODULES

        if self.modulesDir:

            self.loadedModules = utils.loadAllModulesFromDirectory(self.modulesDir)  # Load modules if directory is provided

            self.addModuleToUI()

    def showEvent(self, event):
        super().showEvent(event)

        # Ensure a script job exists and is active when the UI is shown.
        # If self.jobNum is None or the job no longer exists in Maya, create a new one.
        if getattr(self, 'jobNum', None) is None or not cmds.scriptJob(exists=self.jobNum):
            self.createScriptJob()

    def createScriptJob(self):
        """Create a scriptJob that listens for selection changes"""
        if getattr(self, 'jobNum', None) is not None and cmds.scriptJob(exists = self.jobNum):
            cmds.scriptJob(kill = self.jobNum, force = True)

        self.jobNum = cmds.scriptJob(event = ['SelectionChanged', self.modifySelected], parent = self.objectName())

    def closeEvent(self, event):

        if getattr(self, 'jobNum', None) is not None and cmds.scriptJob(exists = self.jobNum):
            cmds.scriptJob(kill = self.jobNum, force = True)
            self.jobNum = None

        super().closeEvent(event)

    def modifySelected(self):

        selectedNodes = cmds.ls(selection = True)

        if len(selectedNodes) <= 1:
            self.moduleInstance = None
            selectedModuleNamespace = None
            currentModuleFile = None

            if len(selectedNodes) == 1:
                lastSelected = selectedNodes[0]

                namespaceAndNode = utils.stripLeadingNamespace(lastSelected)
                if namespaceAndNode is not None:
                    namespace = namespaceAndNode[0]

                    validModules = [module for module in utils.loadAllModulesFromDirectory(self.modulesDir).keys()]
                    validModuleNames = [module['name'] for module in utils.loadAllModulesFromDirectory(self.modulesDir).values()]

                    for index, moduleName in enumerate(validModuleNames):
                        moduleNameIncSuffix = f'{moduleName}__'
                        if namespace.find(moduleNameIncSuffix) == 0:
                            currentModuleFile = validModules[index]
                            selectedModuleNamespace = namespace
                            break

            controlEnable = False
            userSpecifiedName = ''

            if selectedModuleNamespace is not None:
                controlEnable = True
                userSpecifiedName = selectedModuleNamespace.partition('__')[2]

                mod = importlib.import_module(f'Blueprint.{currentModuleFile}')
                importlib.reload(mod)

                moduleClass = getattr(mod, mod.CLASS_NAME)
                self.moduleInstance = moduleClass(userSpecifiedName = userSpecifiedName)

            self.buttons['Mirror Module'].setEnabled(False)
            self.buttons['Rehook'].setEnabled(False)
            self.buttons['Constrain Root > Hook'].setEnabled(False)
            self.buttons['Delete'].setEnabled(False)

            self.moduleInstanceLineEdit.setText(userSpecifiedName)








    def createHLine(self):
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        line.setLineWidth(1)
        line.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        return line

    def setupUI(self):

        # MAIN LAYOUT
        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(5)

        # CREATE WIDGETS
        self.tabWidget = QtWidgets.QTabWidget()
        self.tabWidget.setStyleSheet("""
        QTabWidget::pane {
            border: 2px solid #555;
            border-radius: 8px;
            padding: 5px;
        }

        QTabBar::tab {
            background: #2c3e50;
            color: white;
            border: 1px solid #444;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            padding: 5px 16px;
            margin-right: 2px;
            font: bold 12px;
        }

        QTabBar::tab:selected {
            background: #3daee9;
            border-top-left-radius: 8px;    /* more rounded corner */
            border-top-right-radius: 8px;
        }

        QTabBar::tab:hover {
            background: #a4a4a4;
        }
        """)

        self.modulesTab = QtWidgets.QWidget()
        self.tabWidget.addTab(self.modulesTab, 'Modules')

        self.scrollArea = QtWidgets.QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setFrameShape(QtWidgets.QFrame.Box)
        self.scrollArea.setFixedHeight(300)

        self.scrollWidget = QtWidgets.QWidget()

        self.moduleInstanceNameLabel = QtWidgets.QLabel('Module Instance:')
        self.moduleInstanceLineEdit = QtWidgets.QLineEdit()

        self.symmetryCheckbox = QtWidgets.QCheckBox('Symmetry Move')

        buttonFont = QtGui.QFont()
        buttonFont.setPointSize(12)
        buttonFont.setBold(True)

        self.lockButton = QtWidgets.QPushButton('LOCK')
        self.lockButton.setStyleSheet("""
                                QPushButton {
                                    background-color: #216091;  /* solid blue */
                                    color: white;
                                    border-radius: 5px;
                                    padding: 4px 8px;

                                }
                                QPushButton:hover {
                                    background-color: #063A62;  /* darker blue on hover */
                                }
                                QPushButton:pressed {
                                    background-color: #032947;  /* even darker when pressed */
                                }
                                """)
        self.lockButton.setFont(buttonFont)
        self.lockButton.setFixedSize(64, 64)

        self.publishButton = QtWidgets.QPushButton('PUBLISH')
        self.publishButton.setStyleSheet("""
                        QPushButton {
                            background-color: #68B159;  /* solid blue */
                            color: white;
                            border-radius: 5px;
                            padding: 4px 8px;


                        }
                        QPushButton:hover {
                            background-color: #216A12;  /* darker blue on hover */
                        }
                        QPushButton:pressed {
                            background-color: #0C4700;  /* even darker when pressed */
                        }
                        """)
        self.publishButton.setFont(buttonFont)
        self.publishButton.setFixedHeight(64)

        # CREATE LAYOUTS
        self.modulesTabLayout = QtWidgets.QVBoxLayout(self.modulesTab)
        self.modulesTabLayout.setContentsMargins(0, 0, 0, 0)
        self.modulesTabLayout.setSpacing(5)

        self.scrollLayout = QtWidgets.QVBoxLayout(self.scrollWidget)
        self.scrollLayout.setContentsMargins(5, 5, 5, 5)
        self.scrollLayout.setSpacing(5)
        self.scrollLayout.setAlignment(QtCore.Qt.AlignTop)

        self.moduleInstanceNameLayout = QtWidgets.QHBoxLayout()

        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setSpacing(8)
        self.gridLayout.setContentsMargins(8, 8, 8, 8)

        self.bottomButtonLayout = QtWidgets.QHBoxLayout()

        # ADD WIDGETS
        self.scrollArea.setWidget(self.scrollWidget)

        self.modulesTabLayout.addWidget(self.scrollArea)

        self.moduleInstanceNameLayout.addWidget(self.moduleInstanceNameLabel)
        self.moduleInstanceNameLayout.addWidget(self.moduleInstanceLineEdit)

        self.gridLayout.addWidget(self.symmetryCheckbox, 2, 2)

        self.bottomButtonLayout.addWidget(self.lockButton)
        self.bottomButtonLayout.addWidget(self.publishButton)

        self.mainLayout.addWidget(self.tabWidget)

        # ADD BUTTONS TO GRID LAYOUT
        buttonDefs = [
            ('Rehook', 0, 0),
            ('Snap Root > Hook', 0, 1),
            ('Constrain Root > Hook', 0, 2),
            ('Group Selected', 1, 0),
            ('Ungroup', 1, 1),
            ('Mirror Module', 1, 2),
            ('Delete', 2, 1),
        ]

        roundedCornersStyle = """
        QPushButton {
            background-color: #3498db;  /* solid blue */
            color: white;
            border-radius: 5px;
            border: 1px solid #2980b9;
            padding: 4px 8px;


        }
        QPushButton:hover {
            background-color: #2980b9;  /* darker blue on hover */
        }
        QPushButton:pressed {
            background-color: #1c5980;  /* even darker when pressed */
        }
        QPushButton:disabled {
            background-color: #555555;
            color: #aaaaaa;
            border: 1px solid #333333;
        }
        """

        # Create buttons dynamically and add to layout
        self.buttons = {}
        for text, row, col in buttonDefs:
            btn = QtWidgets.QPushButton(text)
            btn.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
            btn.setFixedHeight(32)
            btn.setStyleSheet(roundedCornersStyle)  # apply rounded corners style
            self.gridLayout.addWidget(btn, row, col)
            self.buttons[text] = btn

        # ADD TO MAIN LAYOUT
        self.modulesTabLayout.addLayout(self.moduleInstanceNameLayout)
        self.modulesTabLayout.addWidget(self.createHLine())
        self.modulesTabLayout.addLayout(self.gridLayout)
        self.modulesTabLayout.addWidget(self.createHLine())
        self.modulesTabLayout.addLayout(self.bottomButtonLayout)

        # CONNECT WIDGETS
        self.lockButton.clicked.connect(self.lockClicked)

    def lockClicked(self):
        reply = QtWidgets.QMessageBox.question(self, "Lock Blueprints?", "Locking the character will convert current blueprint modules to joints.This action cannot be undone. Modifications to the blueprint system cannot be made after this point.\nDo you want to continue?", QtWidgets.QMessageBox.StandardButton.Ok | QtWidgets.QMessageBox.StandardButton.Cancel)

        if reply == QtWidgets.QMessageBox.StandardButton.Cancel:
            return
        else:
            moduleInfo = []

            cmds.namespace(setNamespace = ':')
            namespaces = cmds.namespaceInfo(listOnlyNamespaces = True)

            validModules = [module for module in utils.loadAllModulesFromDirectory(self.modulesDir).keys()]
            validModuleNames = [module['name'] for module in utils.loadAllModulesFromDirectory(self.modulesDir).values()]

            for n in namespaces:
                splitString = n.partition('__')

                if splitString[1] != '':
                    module = splitString[0]
                    userSpecifiedName = splitString[2]

                    if module in validModuleNames:
                        index = validModuleNames.index(module)
                        moduleInfo.append([validModules[index], userSpecifiedName])

            if len(moduleInfo) == 0:
                QtWidgets.QMessageBox.information(None, "Lock Blueprints?", "There is no blueprint module instance in the current scene.\nAborting Lock.")

            moduleInstances = []

            for module in moduleInfo:
                mod = importlib.import_module(f'Blueprint.{module[0]}')
                importlib.reload(mod)

                moduleClass = getattr(mod, mod.CLASS_NAME)
                moduleInst = moduleClass(userSpecifiedName = module[1])
                moduleInfo = moduleInst.lockPhase1()

                moduleInstances.append((moduleInst, moduleInfo))

            for module in moduleInstances:
                module[0].lockPhase2(module[1])



    def addModuleToUI(self):
        """
        Adds all loaded modules to the UI by creating a ModuleWidget for each
        and inserting it before the spacer item in the scroll layout.
        """

        insertIndex = self.scrollLayout.count() - 1  # index before spacer

        for moduleData in self.loadedModules.values():
            moduleWidget = ModuleWidget(
                moduleData['name'],
                moduleData['description'],
                moduleData['icon'],
                moduleData['module']
            )
            self.scrollLayout.insertWidget(insertIndex, moduleWidget)


    @classmethod
    def showUI(cls, modulesDir=None):
        """Show the Blueprint Module UI

        Args:
            modulesDir (str, optional): Directory containing module Python files.

        Returns:
            Blueprint_UI: The UI instance.
        """


        if not cls.ui_instance:
            cls.ui_instance = Blueprint_UI(modulesDir)

        if cls.ui_instance.isHidden():
            cls.ui_instance.show()

        else:
            cls.ui_instance.raise_()
            cls.ui_instance.activateWindow()



'''
import os
import sys
import maya.cmds as cmds


maya.cmds.file(new = True, f = True)

try:
    riggingToolRoot = os.environ['RIGGING_TOOL_ROOT']
    
except:
    print('RIGGING_TOOL_ROOT variable not correctly configured.')
    
else:
    path = f'{riggingToolRoot}/Modules'
    
    if not path in sys.path:
        sys.path.append(path)
    
    import System.blueprint_UI as blueprint_UI
    import importlib
    importlib.reload(blueprint_UI)
    
    # Call showUI as a function, not as a class method
    ui = blueprint_UI.Blueprint_UI.showUI(f'{path}/Blueprint')
'''
