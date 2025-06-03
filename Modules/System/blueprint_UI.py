"""
Blueprint Module UI for Maya
This module creates a UI for managing rigging modules with PySide2 in Maya.
It dynamically loads module information from Python files in a specified directory.
"""
import importlib.util
import os.path
import json

from PySide6 import QtCore, QtWidgets, QtGui
from shiboken6 import wrapInstance
import maya.OpenMayaUI as omui
import maya.cmds as cmds

# Global variable to store the UI instance
UI_INSTANCE = None

def mayaMainWindow():
    """Return the Maya main window widget as a Python object"""
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

def get_maya_colors():
    """Get standard Maya UI colors"""
    return {
        'background': QtGui.QColor(68, 68, 68),  # Maya's default dark gray
        'darker_background': QtGui.QColor(53, 53, 53),  # Darker gray for contrast
        'darkest_background': QtGui.QColor(45, 45, 45),  # Darkest gray for text fields
        'item_background': QtGui.QColor(58, 58, 58),  # Slightly darker gray for items
        'text': QtGui.QColor(200, 200, 200),  # Light gray for text
        'highlight': QtGui.QColor(80, 150, 180),  # Maya's blue highlight color
        'border': QtGui.QColor(35, 35, 35)  # Very dark gray for borders
    }

class IconWidget(QtWidgets.QFrame):
    """Widget for the clickable icon area"""

    clicked = QtCore.Signal()  # Signal emitted when icon is clicked

    def __init__(self, iconPath=None, parent=None):
        super().__init__(parent=parent)

        self.iconPath = iconPath if iconPath else ""
        self.maya_colors = get_maya_colors()

        self.setupUI()

    def setupUI(self):
        # Set frame style with border but no raised/sunken effect
        self.setFrameStyle(QtWidgets.QFrame.Panel | QtWidgets.QFrame.Plain)
        self.setLineWidth(1)
        self.setFixedSize(140, 140)

        # Set background color
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QtGui.QPalette.Window, self.maya_colors['darker_background'])
        self.setPalette(palette)

        # Icon layout
        iconLayout = QtWidgets.QVBoxLayout(self)
        iconLayout.setContentsMargins(5, 5, 5, 5)

        # Icon label
        if self.iconPath and os.path.exists(self.iconPath):
            self.iconLabel = QtWidgets.QLabel()
            pixmap = QtGui.QPixmap(self.iconPath)
            self.iconLabel.setPixmap(pixmap.scaled(
                120, 120,
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation
            ))
            self.iconLabel.setAlignment(QtCore.Qt.AlignCenter)
        else:
            self.iconLabel = QtWidgets.QLabel("Icon")
            self.iconLabel.setAlignment(QtCore.Qt.AlignCenter)
            self.iconLabel.setStyleSheet(f"color: {self.maya_colors['text'].name()};")

        iconLayout.addWidget(self.iconLabel)

        # Make the widget look interactive with cursor change
        self.setCursor(QtCore.Qt.PointingHandCursor)

    def mousePressEvent(self, event):
        """Handle mouse press event"""
        if event.button() == QtCore.Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

class ModuleWidget(QtWidgets.QFrame):
    """Widget representing a single module entry in the UI"""

    def __init__(self, moduleName, description, iconPath=None, moduleObject=None, parent=None):
        super().__init__(parent=parent)

        self.moduleName = moduleName
        self.description = description
        self.iconPath = iconPath if iconPath else ""
        self.moduleObject = moduleObject
        self.maya_colors = get_maya_colors()

        self.setupUI()

    def setupUI(self):
        # Set frame style with border but no raised/sunken effect
        self.setFrameStyle(QtWidgets.QFrame.Panel | QtWidgets.QFrame.Plain)
        self.setLineWidth(1)

        # Set background color
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QtGui.QPalette.Window, self.maya_colors['background'])
        self.setPalette(palette)

        # Main layout for the module widget
        self.mainLayout = QtWidgets.QHBoxLayout(self)
        self.mainLayout.setContentsMargins(10, 10, 10, 10)
        self.mainLayout.setSpacing(10)

        # Left side - Icon area (clickable)
        self.iconWidget = IconWidget(self.iconPath)
        self.iconWidget.clicked.connect(self.onIconClicked)
        self.mainLayout.addWidget(self.iconWidget)

        # Right side - Module info in vertical layout
        self.infoLayout = QtWidgets.QVBoxLayout()
        self.infoLayout.setContentsMargins(0, 0, 0, 0)
        self.infoLayout.setSpacing(5)

        # Module name label
        self.nameLabel = QtWidgets.QLabel(self.moduleName.upper())
        self.nameLabel.setAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setBold(True)
        self.nameLabel.setFont(font)
        self.nameLabel.setStyleSheet(f"color: {self.maya_colors['text'].name()};")
        self.infoLayout.addWidget(self.nameLabel)

        # Description text area (scrollable)
        self.descriptionTextEdit = QtWidgets.QTextEdit()
        self.descriptionTextEdit.setPlainText(self.description)
        self.descriptionTextEdit.setReadOnly(True)
        self.descriptionTextEdit.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.descriptionTextEdit.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.descriptionTextEdit.setStyleSheet(f"""
            QTextEdit {{
                background-color: {self.maya_colors['darkest_background'].name()};
                color: {self.maya_colors['text'].name()};
                border: 1px solid {self.maya_colors['border'].name()};
                padding: 5px;
            }}
            QScrollBar:vertical {{
                background-color: {self.maya_colors['darker_background'].name()};
                width: 14px;
                margin: 14px 0px 14px 0px;
            }}
            QScrollBar::handle:vertical {{
                background-color: #606060;
                min-height: 20px;
            }}
            QScrollBar::add-line:vertical {{
                background-color: {self.maya_colors['darker_background'].name()};
                height: 14px;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
            }}
            QScrollBar::sub-line:vertical {{
                background-color: {self.maya_colors['darker_background'].name()};
                height: 14px;
                subcontrol-position: top;
                subcontrol-origin: margin;
            }}
        """)
        self.infoLayout.addWidget(self.descriptionTextEdit)

        # Add info layout to main layout
        self.mainLayout.addLayout(self.infoLayout)
        self.mainLayout.setStretch(1, 1)  # Make the right side expand

    def onIconClicked(self):
        """Handle icon click event"""
        print(f"Module '{self.moduleName}' icon clicked")
        # If the module has a specific function to call, you could call it here
        if self.moduleObject and hasattr(self.moduleObject, 'module_function'):
            self.moduleObject.module_function()

class Blueprint_UI(QtWidgets.QDialog):
    """Main UI dialog for the Blueprint Module system"""

    def __init__(self, modulesDir=None, parent=None):
        if parent is None:
            try:
                parent = mayaMainWindow()
            except:
                pass

        super().__init__(parent=parent)

        self.setWindowTitle('Blueprint Module UI')
        self.setMinimumSize(600, 700)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        # Store the modules directory
        self.modulesDir = modulesDir

        # Dictionary to store loaded modules
        self.loadedModules = {}

        # Get Maya colors
        self.maya_colors = get_maya_colors()

        # Path for storing UI state
        self.state_file = os.path.join(os.path.expanduser("~"), ".blueprint_ui_state.json")

        self.setupUI()

        # Load modules if directory is provided
        if self.modulesDir:
            self.loadModulesFromFileDirectory()

        # Load saved UI state
        self.loadUIState()

        # Connect close event to save state
        self.finished.connect(self.saveUIState)

    def setupUI(self):
        # Set the dialog's background color to match Maya's UI
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QtGui.QPalette.Window, self.maya_colors['background'])
        self.setPalette(palette)

        # Main layout
        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.mainLayout.setContentsMargins(5, 5, 5, 5)
        self.mainLayout.setSpacing(0)

        # Tab widget
        self.tabWidget = QtWidgets.QTabWidget()
        self.tabWidget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {self.maya_colors['border'].name()};
                background-color: {self.maya_colors['background'].name()};
            }}
            QTabBar::tab {{
                background-color: {self.maya_colors['darker_background'].name()};
                color: {self.maya_colors['text'].name()};
                padding: 5px 10px;
                border: 1px solid {self.maya_colors['border'].name()};
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }}
            QTabBar::tab:selected {{
                background-color: {self.maya_colors['background'].name()};
            }}
            QTabBar::tab:hover {{
                background-color: {self.maya_colors['highlight'].name()};
            }}
        """)

        # Modules tab
        self.modulesTab = QtWidgets.QWidget()
        self.modulesTabLayout = QtWidgets.QVBoxLayout(self.modulesTab)
        self.modulesTabLayout.setContentsMargins(10, 10, 10, 10)
        self.modulesTabLayout.setSpacing(10)

        # Scroll area for modules
        self.scrollArea = QtWidgets.QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setFrameStyle(QtWidgets.QFrame.Panel | QtWidgets.QFrame.Plain)
        self.scrollArea.setStyleSheet(f"""
            QScrollArea {{
                border: 1px solid {self.maya_colors['border'].name()};
                background-color: {self.maya_colors['background'].name()};
            }}
            QScrollBar:vertical {{
                background-color: {self.maya_colors['darker_background'].name()};
                width: 14px;
                margin: 14px 0px 14px 0px;
            }}
            QScrollBar::handle:vertical {{
                background-color: #606060;
                min-height: 20px;
            }}
            QScrollBar::add-line:vertical {{
                background-color: {self.maya_colors['darker_background'].name()};
                height: 14px;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
            }}
            QScrollBar::sub-line:vertical {{
                background-color: {self.maya_colors['darker_background'].name()};
                height: 14px;
                subcontrol-position: top;
                subcontrol-origin: margin;
            }}
        """)

        # Container widget for scroll area
        self.scrollWidget = QtWidgets.QWidget()
        self.scrollWidget.setStyleSheet(f"background-color: {self.maya_colors['background'].name()};")
        self.scrollLayout = QtWidgets.QVBoxLayout(self.scrollWidget)
        self.scrollLayout.setContentsMargins(10, 10, 10, 10)
        self.scrollLayout.setSpacing(15)
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

        # Add the modules tab to the tab widget
        self.tabWidget.addTab(self.modulesTab, 'Modules')

        # Add the tab widget to the main layout
        self.mainLayout.addWidget(self.tabWidget)

    def loadModulesFromFileDirectory(self):
        """Load all Python modules from the specified directory"""
        if not self.modulesDir or not os.path.isdir(self.modulesDir):
            print(f'Error: Invalid modules directory: {self.modulesDir}')
            return

        # Clear existing modules
        self.clearModules()

        # Find all Python files in the directory
        for fileName in os.listdir(self.modulesDir):
            if fileName.endswith('.py') and not fileName.startswith('__'):
                modulePath = os.path.join(self.modulesDir, fileName)
                moduleName = os.path.splitext(fileName)[0]

                try:
                    # Import the module dynamically
                    moduleSpec = importlib.util.spec_from_file_location(moduleName, modulePath)
                    module = importlib.util.module_from_spec(moduleSpec)
                    moduleSpec.loader.exec_module(module)

                    # Extract module metadata
                    name = getattr(module, 'MODULE_NAME', moduleName)
                    description = getattr(module, 'MODULE_DESCRIPTION', 'No description available')
                    iconPath = getattr(module, 'MODULE_ICON', '')

                    # Add module to UI
                    self.addModule(name, description, iconPath, module)

                    # Store the loaded module
                    self.loadedModules[moduleName] = module

                except Exception as e:
                    print(f'Error loading module {moduleName}: {str(e)}')

    def addModule(self, name, description, iconPath='', moduleObject=None):
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

    def saveUIState(self):
        """Save UI state to a file"""
        try:
            state = {
                'geometry': self.saveGeometry().toBase64().data().decode(),
                'modulesDir': self.modulesDir if self.modulesDir else '',
                'moduleDescriptions': {}
            }

            # Save description text for each module
            for i in range(self.scrollLayout.count() - 1):  # Exclude spacer
                widget = self.scrollLayout.itemAt(i).widget()
                if isinstance(widget, ModuleWidget):
                    module_name = widget.moduleName
                    description = widget.descriptionTextEdit.toPlainText()
                    state['moduleDescriptions'][module_name] = description

            with open(self.state_file, 'w') as f:
                json.dump(state, f)

        except Exception as e:
            print(f"Error saving UI state: {str(e)}")

    def loadUIState(self):
        """Load UI state from a file"""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    state = json.load(f)

                # Restore window geometry
                if 'geometry' in state:
                    self.restoreGeometry(QtCore.QByteArray.fromBase64(state['geometry'].encode()))

                # Restore module descriptions
                if 'moduleDescriptions' in state:
                    for i in range(self.scrollLayout.count() - 1):  # Exclude spacer
                        widget = self.scrollLayout.itemAt(i).widget()
                        if isinstance(widget, ModuleWidget):
                            module_name = widget.moduleName
                            if module_name in state['moduleDescriptions']:
                                widget.descriptionTextEdit.setPlainText(state['moduleDescriptions'][module_name])

        except Exception as e:
            print(f"Error loading UI state: {str(e)}")

def showUI(modulesDir=None):
    """Show the Blueprint Module UI

    Args:
        modulesDir (str, optional): Directory containing module Python files.

    Returns:
        Blueprint_UI: The UI instance.
    """
    global UI_INSTANCE

    # If UI already exists, just show it
    if UI_INSTANCE is not None and UI_INSTANCE.isVisible():
        UI_INSTANCE.activateWindow()
        UI_INSTANCE.raise_()
        return UI_INSTANCE

    # If UI exists but is hidden, show it again
    if UI_INSTANCE is not None:
        # Update modules directory if provided
        if modulesDir and UI_INSTANCE.modulesDir != modulesDir:
            UI_INSTANCE.modulesDir = modulesDir
            UI_INSTANCE.loadModulesFromFileDirectory()

        UI_INSTANCE.show()
        return UI_INSTANCE

    # Create new UI
    UI_INSTANCE = Blueprint_UI(modulesDir)
    UI_INSTANCE.show()
    return UI_INSTANCE

# Example module files for testing
"""
# Example module_a.py:
MODULE_NAME = "Module A"
MODULE_DESCRIPTION = "This is a test description for Module A. It can contain detailed information about the module's functionality and usage instructions. The text area is scrollable to accommodate longer descriptions."
MODULE_ICON = ""  # Path to icon image

def module_function():
    print("Module A function called")

# Example module_b.py:
MODULE_NAME = "Module B"
MODULE_DESCRIPTION = "This is the description for Module B. It demonstrates how the module information is displayed in the UI with proper alignment and styling."
MODULE_ICON = ""  # Path to icon image

def module_function():
    print("Module B function called")
"""
