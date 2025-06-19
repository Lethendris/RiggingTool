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
        # create layout
        self.mainLayout = QtWidgets.QHBoxLayout(self)
        self.mainLayout.setContentsMargins(5, 0, 5, 0)
        self.mainLayout.setSpacing(5)

        # create widgets
        # image button
        self.imageButton = RoundedIconButton()
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


        # set icon for button if available
        if self.iconPath and os.path.exists(self.iconPath):
            icon = QtGui.QIcon(self.iconPath)
            self.imageButton.setIcon(icon)
        else:
            # default icon
            self.imageButton.setText('Icon')

        # module name label
        self.nameLabel = QtWidgets.QLabel(self.moduleName)

        # module description field
        self.moduleField = QtWidgets.QVBoxLayout()
        self.moduleField.setContentsMargins(5, 0, 0, 0)

        # Description text field
        self.descriptionField = NonInteractivePlainTextEdit(self.description)
        self.descriptionField.setFixedHeight(64)

        # add widgets
        self.mainLayout.addWidget(self.imageButton, alignment = QtCore.Qt.AlignBottom)
        self.moduleField.addWidget(self.nameLabel, alignment = QtCore.Qt.AlignCenter)
        self.moduleField.addWidget(self.descriptionField)

        self.mainLayout.addLayout(self.moduleField)

        # Set a fixed height for consistency
        self.setFixedHeight(90)

        # connect widgets
        # Connect button click event
        self.imageButton.clicked.connect(self.onIconClicked)

    def onIconClicked(self):
        self.installModule()

    def installModule(self):
        baseName = 'instance_'

        cmds.namespace(setNamespace = ':')
        namespaces = cmds.namespaceInfo(listOnlyNamespaces = True)


        for i in range(len(namespaces)):
            if namespaces[i].find('__') != -1:
                namespaces[i] = namespaces[i].partition('__')[2]

        newSuffix = utils.findHighestTrailingNumber(namespaces, baseName) + 1

        userSpecifiedName = f'{baseName}{str(newSuffix)}'


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
        if parent is None:
            try:
                parent = mayaMainWindow()
            except:
                pass

        super().__init__(parent = parent)

        self.setWindowTitle('Blueprint Module UI')
        # self.setMinimumSize(400, 200)
        self.setFixedSize(400,600)

        # store modules directory
        self.modulesDir = modulesDir

        # loaded modules
        self.loadedModules = {}

        self.setupUI()

        # Load modules if directory is provided
        if self.modulesDir:
            self.loadModulesFromFileDirectory()

    def setupUI(self):

        # main layout
        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(5)

        # tab widget
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
            padding: 8px 16px;
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

        # modules tab
        self.modulesTab = QtWidgets.QWidget()


        self.modulesTabLayout = QtWidgets.QVBoxLayout(self.modulesTab)
        self.modulesTabLayout.setContentsMargins(0, 0, 0, 0)
        self.modulesTabLayout.setSpacing(5)


        # scroll area
        self.scrollArea = QtWidgets.QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setFrameShape(QtWidgets.QFrame.Box)
        self.scrollArea.setFixedHeight(300)

        self.scrollWidget = QtWidgets.QWidget()
        self.scrollLayout = QtWidgets.QVBoxLayout(self.scrollWidget)
        self.scrollLayout.setContentsMargins(5, 5, 5, 5)

        self.scrollLayout.setSpacing(5)
        self.scrollLayout.setAlignment(QtCore.Qt.AlignTop)

        # Add spacer at the bottom to push widgets to the top
        spacer = QtWidgets.QSpacerItem(
            20, 40,
            QtWidgets.QSizePolicy.Minimum,
            QtWidgets.QSizePolicy.Expanding
        )
        self.scrollLayout.addItem(spacer)

        # Set the scroll widget as the scroll area's widget
        self.scrollArea.setWidget(self.scrollWidget)
        self.modulesTabLayout.addWidget(self.scrollArea)

        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        line.setLineWidth(1)
        self.modulesTabLayout.addWidget(line)

        self.moduleInstanceNameLayout = QtWidgets.QHBoxLayout()
        self.moduleInstanceNameLabel = QtWidgets.QLabel('Module Instance:')
        self.moduleInstanceLineEdit = QtWidgets.QLineEdit()
        self.moduleInstanceNameLayout.addWidget(self.moduleInstanceNameLabel)
        self.moduleInstanceNameLayout.addWidget(self.moduleInstanceLineEdit)

        self.modulesTabLayout.addLayout(self.moduleInstanceNameLayout)
        self.modulesTabLayout.addWidget(line)

        # self.gridWidget = QtWidgets.QWidget()
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setSpacing(8)
        self.gridLayout.setContentsMargins(8, 8, 8, 8)

        # Define buttons with text and position (row, column)
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

        self.symmetryCheckbox = QtWidgets.QCheckBox('Symmetry Move')


        self.gridLayout.addWidget(self.symmetryCheckbox, 2, 2)


        # Add the grid layout to the parent layout
        self.modulesTabLayout.addLayout(self.gridLayout)

        self.modulesTabLayout.addWidget(line)

        buttonFont = QtGui.QFont()
        buttonFont.setPointSize(11)
        buttonFont.setBold(True)

        self.lockButton = QtWidgets.QPushButton('Lock')
        self.lockButton.setStyleSheet(roundedCornersStyle)
        self.publishButton = QtWidgets.QPushButton('PUBLISH')
        self.publishButton.setFont(buttonFont)

        self.publishButton.setStyleSheet(roundedCornersStyle)
        self.publishButton.setFixedHeight(50)


        self.modulesTabLayout.addWidget(self.lockButton)
        self.modulesTabLayout.addWidget(self.publishButton)
        # self.modulesTabLayout.addStretch()

        # buttonFont = QtGui.QFont()
        # buttonFont.setPointSize(11)
        # buttonFont.setBold(True)

        # self.rehook_btn = QtWidgets.QPushButton('Rehook')
        # self.rehook_btn.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        # self.rehook_btn.setFont(buttonFont)
        #
        # self.snapToHook_btn = QtWidgets.QPushButton('Snap to\nHook')
        # self.snapToHook_btn.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        # self.snapToHook_btn.setFont(buttonFont)
        #
        # self.constrainRootToHook_btn = QtWidgets.QPushButton('Constrain\nRoot to Hook')
        # self.constrainRootToHook_btn.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        # self.constrainRootToHook_btn.setFont(buttonFont)
        #
        # self.group_btn = QtWidgets.QPushButton('Group')
        # self.group_btn.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        # self.group_btn.setFont(buttonFont)
        #
        # self.ungroup_btn = QtWidgets.QPushButton('Ungroup')
        # self.ungroup_btn.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        # self.ungroup_btn.setFont(buttonFont)
        #
        # self.mirror_btn = QtWidgets.QPushButton('Mirror')
        # self.mirror_btn.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        # self.mirror_btn.setFont(buttonFont)
        #
        # self.delete_btn = QtWidgets.QPushButton('Delete')
        # self.delete_btn.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        # self.delete_btn.setFont(buttonFont)
        #
        #
        # self.gridLayout.addWidget(self.rehook_btn, 0, 0)
        # self.gridLayout.addWidget(self.snapToHook_btn, 0, 1)
        # self.gridLayout.addWidget(self.constrainRootToHook_btn, 0, 2)
        # self.gridLayout.addWidget(self.group_btn, 1, 0)
        # self.gridLayout.addWidget(self.ungroup_btn, 1, 1)
        # self.gridLayout.addWidget(self.mirror_btn, 1, 2)
        # self.gridLayout.addWidget(self.delete_btn, 2, 1)
        #
        # # Make the grid occupy vertical space
        # self.gridWidget.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        #
        #
        # self.modulesTabLayout.addWidget(self.gridWidget, stretch = 1)
        #
        # self.lockButton = QtWidgets.QPushButton("LOCK")
        # self.lockButton.setFixedHeight(30)
        # self.lockButton.setFont(buttonFont)
        # self.publishButton = QtWidgets.QPushButton("PUBLISH")
        # self.publishButton.setFixedHeight(40)
        # self.publishButton.setFont(buttonFont)
        #
        #
        # self.modulesTabLayout.addWidget(self.lockButton)
        # self.modulesTabLayout.addWidget(self.publishButton)

        self.tabWidget.addTab(self.modulesTab, 'Modules')

        self.mainLayout.addWidget(self.tabWidget)

        # Set the dialog's background color to match Maya's UI
        self.setAutoFillBackground(True)
        palette = self.palette()
        self.setPalette(palette)

    def loadModulesFromFileDirectory(self):
        """Load all Python modules from the specified directory"""
        if not self.modulesDir or not os.path.isdir(self.modulesDir):
            print(f'Error: Invalid modules directory: {self.modulesDir}')
            return

        # clear modules
        self.clearModules()

        # Find all Python files in the directory
        for fileName in os.listdir(self.modulesDir):
            if fileName.endswith('.py') and not fileName.startswith('__'):
                modulePath = os.path.join(self.modulesDir, fileName)
                moduleName = os.path.splitext(fileName)[0]

                try:
                    # import module dynamically
                    moduleSpec = importlib.util.spec_from_file_location(moduleName, modulePath)
                    module = importlib.util.module_from_spec(moduleSpec)
                    moduleSpec.loader.exec_module(module)

                    # extract module metadata
                    name = getattr(module, 'MODULE_NAME', moduleName)
                    description = getattr(module, 'MODULE_DESCRIPTION', 'No description available')
                    iconPath = getattr(module, 'MODULE_ICON', '')

                    # add module to UI
                    self.addModule(name, description, iconPath, module)

                    self.loadedModules[moduleName] = module

                except Exception as e:
                    print(f'Error loading module {moduleName}: {str(e)}')

    def addModule(self, name, description, iconPath = '', moduleObject = None):
        """Add a new module to the UI"""
        moduleWidget = ModuleWidget(name, description, iconPath, moduleObject)

        # Insert before the spacer (which is the last item)
        self.scrollLayout.insertWidget(self.scrollLayout.count() - 1, moduleWidget)

        return moduleWidget

    def clearModules(self):
        """Clear all modules from the UI"""
        # Remove all widgets except the spacer at the end
        while self.scrollLayout.count() > 1:
            item = self.scrollLayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Clear the loaded modules dictionary
        self.loadedModules.clear()

    @classmethod
    def showUI(cls, modulesDir=None):
        """Show the Blueprint Module UI

        Args:
            modulesDir (str, optional): Directory containing module Python files.

        Returns:
            Blueprint_UI: The UI instance.
        """

        """
        if not cls.ui_instance:
            cls.ui_instance = Blueprint_UI(modulesDir)

        if cls.ui_instance.isHidden():
            cls.ui_instance.show()

        else:
            cls.ui_instance.raise_()
            cls.ui_instance.activateWindow()
        """


        # close existing UI if it exists
        for widget in QtWidgets.QApplication.allWidgets():
            if isinstance(widget, Blueprint_UI):
                widget.close()
                widget.deleteLater()

        # create and show new UI
        UI = Blueprint_UI(modulesDir)
        UI.show()
        return UI


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
