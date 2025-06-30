"""
Base Blueprint Module for Maya Rigging

This module defines the foundational `Blueprint` class, which serves as a base for creating
rigging modules in Maya. It provides core functionalities for managing module instances,
UI integration, and the installation process of module-specific components like joints
and controls. Derived classes are expected to override certain methods to implement
module-specific logic.
"""

import importlib.util
import os.path
import sys

from PySide6 import QtCore, QtWidgets, QtGui
from shiboken6 import wrapInstance
import maya.OpenMayaUI as omui
import maya.cmds as cmds
from functools import partial

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
                color: #e0e0e0;
                border: 2px solid #555;
                border-radius: 4px;
                padding: 6px;
                font-family: Consolas, monospace;
                font-size: 12px;
            }
        """)

    def keyPressEvent(self, event):
        event.accept()


class MyPushButton(QtWidgets.QPushButton):

    def __init__(self, *a, **kw):
        super(MyPushButton, self).__init__(*a, **kw)

        pix_normal = QtGui.QPixmap("my_image.jpg")
        pix_over = pix_normal.copy()
        painter = QtGui.QPainter(pix_over)
        painter.fillRect(pix_over.rect(), QtGui.QBrush(QtGui.QColor(0, 0, 0, 128)))
        painter.end()

        self._icon_normal = QtGui.QIcon(pix_normal)
        self._icon_over = QtGui.QIcon(pix_over)
        self.setIcon(self._icon_normal)

    def enterEvent(self, event):
        self.setIcon(self._icon_over)
        return super(MyPushButton, self).enterEvent(event)

    def leaveEvent(self, event):
        self.setIcon(self._icon_normal)
        return super(MyPushButton, self).leaveEvent(event)


class RoundedIconButton(QtWidgets.QPushButton):
    def __init__(self, imagePath, radius = 8, *args, **kwargs):
        """
        A QPushButton with rounded corners and hover/press color variants.

        Args:
            imagePath (str): Path to base icon image.
            radius (int): Corner radius.
        """
        super().__init__(*args, **kwargs)
        self.radius = radius

        self.setIconSize(QtCore.QSize(64, 64))
        self.setFixedSize(64, 64)
        self.setFlat(True)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setMouseTracking(True)

        # Load icons
        self._icon_normal = QtGui.QIcon(imagePath)
        self._icon_hover = self._createOverlayIcon(imagePath, QtGui.QColor(0, 0, 0, 100))
        self._icon_pressed = self._createOverlayIcon(imagePath, QtGui.QColor(0, 0, 0, 200))

        # Internal state
        self._hovered = False
        self._pressed = False

        self.setIcon(self._icon_normal)

    def _createOverlayIcon(self, imagePath, overlayColor):
        """Creates an icon with a translucent color overlay."""
        pixmap = QtGui.QPixmap(imagePath)
        painter = QtGui.QPainter(pixmap)
        painter.fillRect(pixmap.rect(), overlayColor)
        painter.end()
        return QtGui.QIcon(pixmap)

    def enterEvent(self, event):
        self._hovered = True
        self._updateIcon()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self._pressed = False
        self._updateIcon()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        self._pressed = True
        self._updateIcon()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self._pressed = False
        self._updateIcon()
        super().mouseReleaseEvent(event)

    def _updateIcon(self):
        if self._pressed:
            self.setIcon(self._icon_pressed)
        elif self._hovered:
            self.setIcon(self._icon_hover)
        else:
            self.setIcon(self._icon_normal)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        # Clip to rounded rect
        rect = QtCore.QRectF(self.rect())
        path = QtGui.QPainterPath()
        path.addRoundedRect(rect, self.radius, self.radius)
        painter.setClipPath(path)

        # Optional: background
        # painter.fillPath(path, QtGui.QColor("#f5f5f5"))

        # Draw standard button background
        option = QtWidgets.QStyleOptionButton()
        self.initStyleOption(option)
        self.style().drawControl(QtWidgets.QStyle.CE_PushButtonBevel, option, painter, self)

        # Draw icon manually to ensure it's centered with clipping
        icon = self.icon()
        if not icon.isNull():
            iconSize = self.iconSize()
            x = (self.width() - iconSize.width()) // 2
            y = (self.height() - iconSize.height()) // 2
            icon.paint(painter, x, y, iconSize.width(), iconSize.height())

        # Optional text
        if self.text():
            painter.setPen(self.palette().color(QtGui.QPalette.ButtonText))
            painter.drawText(self.rect(), QtCore.Qt.AlignCenter, self.text())

        painter.end()


class ModuleWidget(QtWidgets.QWidget):
    install = QtCore.Signal(str, object)

    def __init__(self, moduleName, description, iconPath = None, moduleObject = None, parent = None):
        super().__init__(parent = parent)

        self.moduleName = moduleName
        self.description = description
        self.iconPath = iconPath if iconPath else ""
        self.moduleObject = moduleObject

        # MAIN LAYOUT
        self.mainLayout = QtWidgets.QHBoxLayout(self)
        self.mainLayout.setContentsMargins(5, 0, 5, 0)
        self.mainLayout.setSpacing(5)
        self.setFixedHeight(90)

        # WIDGETS
        self.imageButton = RoundedIconButton(self.iconPath)  # image button
        self.imageButton.setFixedSize(64, 64)
        self.imageButton.setIconSize(QtCore.QSize(64, 64))

        if self.iconPath and os.path.exists(self.iconPath):  # set icon for button if available
            icon = QtGui.QIcon(self.iconPath)
            self.imageButton.setIcon(icon)
        else:

            self.imageButton.setText("Icon")  # default icon

        self.nameLabel = QtWidgets.QLabel(self.moduleName)  # module name label

        self.descriptionField = NonInteractivePlainTextEdit(self.description)  # Description text field
        self.descriptionField.setFixedHeight(64)

        # CREATE LAYOUTS
        self.moduleField = QtWidgets.QVBoxLayout()  # module description layout
        self.moduleField.setContentsMargins(5, 0, 0, 0)

        # ADD WIDGETS
        self.mainLayout.addWidget(self.imageButton, alignment = QtCore.Qt.AlignBottom)
        self.moduleField.addWidget(self.nameLabel, alignment = QtCore.Qt.AlignCenter)
        self.moduleField.addWidget(self.descriptionField)

        # CONNECT WIDGETS
        self.imageButton.clicked.connect(self.moduleImageButtonClicked)

        # ADD TO MAIN LAYOUT
        self.mainLayout.addLayout(self.moduleField)

    QtCore.Signal(str, object)

    def moduleImageButtonClicked(self):
        self.install.emit(self.moduleName, self.moduleObject)


class Blueprint_UI(QtWidgets.QDialog):
    ui_instance = None

    def __init__(self, modulesDir = None, parent = None):
        self.jobNum = None

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
        self.setFixedSize(400, 800)

        # SETUP UI
        self.setupUI()

        self.modifySelected()

        # LOAD MODULES

        if self.modulesDir:
            self.loadedModules = utils.loadAllModulesFromDirectory(self.modulesDir)  # Load modules if directory is provided

            self.addModuleToUI()

    def installModule(self, moduleName, moduleObject):

        baseName = 'instance_'

        cmds.namespace(setNamespace = ":")
        rawNamespaces = cmds.namespaceInfo(listOnlyNamespaces = True)

        # Strip prefix before '__' if present
        strippedNamespaces = [ns.partition('__')[2] if '__' in ns else ns for ns in rawNamespaces]

        newSuffix = utils.findHighestTrailingNumber(strippedNamespaces, baseName) + 1

        userSpecifiedName = f'{baseName}{newSuffix}'

        hookObj = self.findHookObjectFromSelection()

        if moduleObject and hasattr(moduleObject, moduleName):
            moduleClass = getattr(moduleObject, moduleName)
            moduleInstance = moduleClass(userSpecifiedName, hookObj)
            moduleInstance.install()

            moduleTransform = f'{moduleName}__{userSpecifiedName}:module_transform'
            cmds.select(moduleTransform)
            cmds.setToolTo('moveSuperContext')

    def findHookObjectFromSelection(self):
        selectedObjects = cmds.ls(selection = True, transforms = True)

        numberOfSelectedObjects = len(selectedObjects)

        hookObj = None

        if numberOfSelectedObjects != 0:
            hookObj = selectedObjects[numberOfSelectedObjects - 1]  # pick last selected as hookObj

        return hookObj

    def rehookModuleSetup(self):

        selectedNodes = cmds.ls(selection = True, transforms = True)

        if len(selectedNodes) == 2:
            newHook = self.findHookObjectFromSelection()
            self.moduleInstance.rehook(newHook)

        else:
            self.deleteScriptJob()

            currentSelection = cmds.ls(selection = True)
            cmds.headsUpMessage('Please select the joint you want to re-hook to. Clear selection to un-hook')

            cmds.scriptJob(event = ('SelectionChanged', partial(self.rehookModule_callback, currentSelection)), runOnce = True)

    def rehookModule_callback(self, currentSelection):

        newHook = self.findHookObjectFromSelection()
        self.moduleInstance.rehook(newHook)

        if len(currentSelection) > 0:
            cmds.select(currentSelection, replace = True)

        else:
            cmds.select(clear = True)

        self.createScriptJob()

    def showEvent(self, event):
        super().showEvent(event)
        self.createScriptJob()

    def closeEvent(self, event):
        super().closeEvent(event)
        self.deleteScriptJob()

    def createScriptJob(self):
        self.jobNum = cmds.scriptJob(event = ['SelectionChanged', self.modifySelected], runOnce = True)

    def deleteScriptJob(self):
        cmds.scriptJob(kill = self.jobNum, force = True)

    def modifySelected(self):

        selectedNodes = cmds.ls(selection = True)

        if len(selectedNodes) <= 1:
            self.moduleInstance = None
            selectedModuleNamespace = None
            currentModuleFile = None

            self.buttons['Ungroup'].setEnabled(False)

            if len(selectedNodes) == 1:
                lastSelected = selectedNodes[0]

                if lastSelected.startswith('Group__'):
                    self.buttons['Ungroup'].setEnabled(True)

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
            constrainCommand = self.constrainRookToHook
            constrainLabel = 'Constrain Root > Hook'

            if selectedModuleNamespace is not None:
                controlEnable = True
                userSpecifiedName = selectedModuleNamespace.partition('__')[2]

                mod = importlib.import_module(f'Blueprint.{currentModuleFile}')
                importlib.reload(mod)

                moduleClass = getattr(mod, mod.CLASS_NAME)
                self.moduleInstance = moduleClass(userSpecifiedName, None)

                if self.moduleInstance.isRootConstrained():
                    constrainCommand = self.unconstrainRookFromHook
                    constrainLabel = 'Unconstrain Root'

            self.buttons['Mirror Module'].setEnabled(controlEnable)
            self.buttons['Rehook'].setEnabled(controlEnable)
            # self.buttons['Group Selected'].setEnabled(controlEnable)
            self.buttons['Snap Root > Hook'].setEnabled(controlEnable)
            self.buttons['Constrain Root > Hook'].setEnabled(controlEnable)
            self.buttons['Constrain Root > Hook'].setText(constrainLabel)

            self.buttons['Constrain Root > Hook'].clicked.connect(constrainCommand)

            self.buttons['Delete'].setEnabled(controlEnable)
            self.moduleInstanceLineEdit.setEnabled(controlEnable)
            self.moduleInstanceLineEdit.setText(userSpecifiedName)

            self.createModuleSpecificControls()

        self.createScriptJob()

    def createModuleSpecificControls(self):

        self._clearLayout(self.moduleControlScrollLayout)

        if self.moduleInstance is not None:
            self.moduleInstance.UI(self, self.moduleControlScrollLayout)

    def deleteModule(self):
        self.moduleInstance.delete()
        cmds.select(clear = True)

    def _clearLayout(self, layout):
        """Helper to clear all widgets and layouts from a given layout."""
        if layout is None:
            return
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()
            elif item.layout():  # Handle nested layouts
                self._clearLayout(item.layout())
                item.layout().deleteLater()

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
            border-radius: 4px;
            padding: 5px;
        }

        QTabBar::tab {
            background: #2c3e50;
            color: #e0e0e0;
            border: 1px solid #444;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            padding: 2px 16px;
            margin-right: 2px;
            font: bold 12px;
        }

        QTabBar::tab:selected {
            background: #008593;
            border-top-left-radius: 4px;    /* more rounded corner */
            border-top-right-radius: 4px;
        }

        QTabBar::tab:hover {
            background: #00727e;
        }
        """)

        self.modulesTab = QtWidgets.QWidget()
        self.tabWidget.addTab(self.modulesTab, 'Modules')

        self.scrollArea = QtWidgets.QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setFrameShape(QtWidgets.QFrame.Box)
        self.scrollArea.setFixedHeight(300)

        self.scrollWidget = QtWidgets.QWidget()

        self.moduleControlScrollArea = QtWidgets.QScrollArea()
        self.moduleControlScrollArea.setWidgetResizable(True)
        self.moduleControlScrollArea.setFrameShape(QtWidgets.QFrame.Box)

        self.moduleControlScrollWidget = QtWidgets.QWidget()

        self.moduleInstanceNameLabel = QtWidgets.QLabel('Module Instance:')
        self.moduleInstanceLineEdit = QtWidgets.QLineEdit()

        self.symmetryCheckbox = QtWidgets.QCheckBox('Symmetry Move')

        buttonFont = QtGui.QFont('Consolas')
        buttonFont.setBold(True)
        buttonFont.setPointSizeF(12)  # floating point improves text rendering
        buttonFont.setStyleStrategy(QtGui.QFont.PreferAntialias)

        self.lockButton = QtWidgets.QPushButton('LOCK')
        self.lockButton.setStyleSheet("""
        QPushButton {
            background-color: #235592;
            color: #e0e0e0;
            border-radius: 4px;
            border: 1px solid #190000;
            padding: 4px 8px;


        }
        QPushButton:hover {
            background-color: #1e4778;
        }
        QPushButton:pressed {
            background-color: #18385f;
        }
        QPushButton:disabled {
            background-color: #555555;
            color: #aaaaaa;
            border: 1px solid #333333;
        }
        """)

        self.lockButton.setFont(buttonFont)

        self.publishButton = QtWidgets.QPushButton('PUBLISH')
        self.publishButton.setStyleSheet("""
        QPushButton {
            background-color: #38761d;
            color: #e0e0e0;
            border-radius: 4px;
            border: 1px solid #190000;
            padding: 4px 8px;


        }
        QPushButton:hover {
            background-color: #2a5815;
        }
        QPushButton:pressed {
            background-color: #1f4110;
        }
        QPushButton:disabled {
            background-color: #555555;
            color: #aaaaaa;
            border: 1px solid #333333;
        }
        """)

        self.publishButton.setFont(buttonFont)
        self.publishButton.setFixedHeight(50)

        # CREATE LAYOUTS
        self.modulesTabLayout = QtWidgets.QVBoxLayout(self.modulesTab)
        self.modulesTabLayout.setContentsMargins(0, 0, 0, 0)
        self.modulesTabLayout.setSpacing(5)
        self.modulesTabLayout.setAlignment(QtCore.Qt.AlignTop)

        self.scrollLayout = QtWidgets.QVBoxLayout(self.scrollWidget)
        self.scrollLayout.setContentsMargins(5, 5, 5, 5)
        self.scrollLayout.setSpacing(5)
        self.scrollLayout.setAlignment(QtCore.Qt.AlignTop)

        self.moduleControlScrollLayout = QtWidgets.QVBoxLayout(self.moduleControlScrollWidget)
        self.moduleControlScrollLayout.setContentsMargins(5, 5, 5, 5)
        self.moduleControlScrollLayout.setSpacing(5)
        self.moduleControlScrollLayout.setAlignment(QtCore.Qt.AlignTop)

        self.moduleInstanceNameLayout = QtWidgets.QHBoxLayout()
        self.moduleInstanceNameLayout.setContentsMargins(5, 0, 0, 0)

        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setSpacing(8)
        self.gridLayout.setContentsMargins(8, 8, 8, 8)

        self.bottomButtonLayout = QtWidgets.QVBoxLayout()

        # ADD WIDGETS
        self.scrollArea.setWidget(self.scrollWidget)
        self.moduleControlScrollArea.setWidget(self.moduleControlScrollWidget)

        self.modulesTabLayout.addWidget(self.scrollArea)

        self.moduleInstanceNameLayout.addWidget(self.moduleInstanceNameLabel)
        self.moduleInstanceNameLayout.addWidget(self.moduleInstanceLineEdit)

        self.gridLayout.addWidget(self.symmetryCheckbox, 2, 2)

        self.bottomButtonLayout.setAlignment(QtCore.Qt.AlignBottom)
        self.bottomButtonLayout.addWidget(self.createHLine())

        self.bottomButtonLayout.addWidget(self.lockButton)
        self.bottomButtonLayout.addWidget(self.createHLine())
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

        styleSheet = """
        QPushButton {
            background-color: #008593;
            color: #e0e0e0;
            border-radius: 4px;
            border: 1px solid #003338;
            padding: 4px 8px;


        }
        QPushButton:hover {
            background-color: #00727e;
        }
        QPushButton:pressed {
            background-color: #00434a;
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
            btn.setStyleSheet(styleSheet)  # apply rounded corners style
            self.gridLayout.addWidget(btn, row, col)
            self.buttons[text] = btn

        self.buttons['Delete'].setStyleSheet("""
        QPushButton {
            background-color: #720000;
            color: #e0e0e0;
            border-radius: 4px;
            border: 1px solid #190000;
            padding: 4px 8px;


        }
        QPushButton:hover {
            background-color: #510000;
        }
        QPushButton:pressed {
            background-color: #310000;
        }
        QPushButton:disabled {
            background-color: #555555;
            color: #aaaaaa;
            border: 1px solid #333333;
        }
        """)

        # self.buttons['Snap Root > Hook'].setEnabled(False)
        # self.buttons['Mirror Module'].setEnabled(False)
        # self.buttons['Rehook'].setEnabled(False)
        # self.buttons['Ungroup'].setEnabled(False)
        # self.buttons['Group Selected'].setEnabled(True)
        # self.buttons['Constrain Root > Hook'].setEnabled(False)
        # self.buttons['Delete'].setEnabled(False)

        # ADD TO MAIN LAYOUT
        self.modulesTabLayout.addWidget(self.createHLine())
        self.modulesTabLayout.addLayout(self.moduleInstanceNameLayout)
        self.modulesTabLayout.addWidget(self.createHLine())
        self.modulesTabLayout.addLayout(self.gridLayout)

        self.modulesTabLayout.addWidget(self.createHLine())
        self.modulesTabLayout.addWidget(self.moduleControlScrollArea)
        self.modulesTabLayout.addLayout(self.bottomButtonLayout)

        # CONNECT WIDGETS
        self.lockButton.clicked.connect(self.lockClicked)
        self.buttons['Delete'].clicked.connect(self.deleteModule)
        self.moduleInstanceLineEdit.editingFinished.connect(self.renameModule)
        self.buttons['Rehook'].clicked.connect(self.rehookModuleSetup)
        self.buttons['Snap Root > Hook'].clicked.connect(self.snapRootToHook)
        self.buttons['Constrain Root > Hook'].clicked.connect(self.constrainRookToHook)
        self.buttons['Group Selected'].clicked.connect(self.groupSelected)
        self.buttons['Ungroup'].clicked.connect(self.ungroupSelected)

    def snapRootToHook(self):
        self.moduleInstance.snapRootToHook()

    def constrainRookToHook(self):
        self.moduleInstance.constrainRootToHook()

        self.buttons['Constrain Root > Hook'].setText('Unconstrain Root')

        try:
            self.buttons['Constrain Root > Hook'].clicked.disconnect()
        except:
            pass

        self.buttons['Constrain Root > Hook'].clicked.connect(self.unconstrainRookFromHook)

    def unconstrainRookFromHook(self):
        self.moduleInstance.unconstrainRootFromHook()

        self.buttons['Constrain Root > Hook'].setText('Constraint Root > Hook')

        try:
            self.buttons['Constrain Root > Hook'].clicked.disconnect()
        except:
            pass

        self.buttons['Constrain Root > Hook'].clicked.connect(self.constrainRookToHook)

    def lockClicked(self):
        reply = QtWidgets.QMessageBox.question(self, "Lock Blueprints?",
                                               "Locking the character will convert current blueprint modules to joints.This action cannot be undone. Modifications to the blueprint system cannot be made after this point.\nDo you want to continue?",
                                               QtWidgets.QMessageBox.StandardButton.Ok | QtWidgets.QMessageBox.StandardButton.Cancel)
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
                moduleInst = moduleClass(module[1], None)
                moduleInfo = moduleInst.lockPhase1()

                moduleInstances.append((moduleInst, moduleInfo))

            for module in moduleInstances:
                module[0].lockPhase2(module[1])

            for module in moduleInstances:
                hookObject = module[1][4]
                module[0].lockPhase3(hookObject)

    def groupSelected(self):
        import System.groupSelected as groupSelected
        importlib.reload(groupSelected)
        groupSelected.GroupSelectedDialog.showUI(self)

    def ungroupSelected(self):
        import System.groupSelected as groupSelected
        importlib.reload(groupSelected)
        groupSelected.UngroupSelected()

    def addModuleToUI(self):
        """
        Adds all loaded modules to the UI by creating a ModuleWidget for each
        and inserting it before the spacer item in the scroll layout.
        """

        insertIndex = self.scrollLayout.count() - 1  # index before spacer

        for moduleName, module_info in self.loadedModules.items():
            description = module_info.get("description", "No description available.")
            iconPath = module_info.get("icon", None)
            moduleObject = module_info.get("module", None)
            className = module_info.get("name", moduleName)  # Get the actual class name

            module_widget = ModuleWidget(className, description, iconPath, moduleObject)
            self.scrollLayout.addWidget(module_widget)
            module_widget.install.connect(self.installModule)

    @classmethod
    def showUI(cls, modulesDir = None):
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

    def renameModule(self):
        newName = self.moduleInstanceLineEdit.text()

        self.moduleInstance.renameModuleInstance(newName)

        previousSelection = cmds.ls(selection = True)

        if len(previousSelection) > 0:
            cmds.select(previousSelection, replace = True)

        else:
            cmds.select(clear = True)


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
