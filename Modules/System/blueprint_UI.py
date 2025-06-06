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

        self.setStyleSheet('''
        QPlainTextEdit 
        {
        border: none;
        }
        ''')

    def keyPressEvent(self, event):
        event.accept()




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
        self.imageButton = QtWidgets.QPushButton()
        self.imageButton.setFixedSize(64, 64)
        self.imageButton.setIconSize(QtCore.QSize(64, 64))


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
        self.mainLayout.setStretch(1, 1)  # Make the right side expand

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
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

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

        # modules tab
        self.modulesTab = QtWidgets.QWidget()
        self.modulesTabLayout = QtWidgets.QVBoxLayout(self.modulesTab)
        self.modulesTabLayout.setContentsMargins(0, 0, 0, 0)
        self.modulesTabLayout.setSpacing(5)


        # scroll area
        self.scrollArea = QtWidgets.QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setFrameShape(QtWidgets.QFrame.Box)

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
