# System/groupSelected.py
import maya.cmds as cmds
from PySide6 import QtWidgets, QtCore, QtGui


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

        # --- IMPORTANT: Set the window modality here ---
        # QtCore.Qt.WindowModal: Blocks input to the parent window.
        # This is generally preferred for dialogs within a host application like Maya.
        self.setWindowModality(QtCore.Qt.WindowModal)

        # --- REMOVE THIS LINE: It makes the window stay on top of ALL applications ---
        # self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)

        self.objectsToGroup = []  # Initialize the list of objects to be grouped

        self.setupUI()

    def setupUI(self):
        mainLayout = QtWidgets.QVBoxLayout(self)

        nameLayout = QtWidgets.QHBoxLayout()
        positionLayout = QtWidgets.QHBoxLayout()
        buttonLayout = QtWidgets.QHBoxLayout()

        self.groupNameLabel = QtWidgets.QLabel('Group Name:')
        self.groupTextEdit = QtWidgets.QTextEdit()

        self.positionLabel = QtWidgets.QLabel('Position At')
        self.positionLabel.setAlignment(QtCore.Qt.AlignCenter)

        self.lastSelectedButton = QtWidgets.QPushButton('Last Selected')
        self.averagePositionButton = QtWidgets.QPushButton('Average Position')

        nameLayout.addWidget(self.groupNameLabel)
        nameLayout.addWidget(self.groupTextEdit)
        positionLayout.addWidget(self.positionLabel)
        buttonLayout.addWidget(self.lastSelectedButton)
        buttonLayout.addWidget(self.averagePositionButton)

        mainLayout.addLayout(nameLayout)
        mainLayout.addLayout(positionLayout)
        mainLayout.addLayout(buttonLayout)




        # # Group Name Input
        # groupNameLayout = QtWidgets.QHBoxLayout()
        # groupNameLabel = QtWidgets.QLabel("Group Name:")
        # self.groupNameLineEdit = QtWidgets.QLineEdit("NewGroup")  # Default name
        # groupNameLayout.addWidget(groupNameLabel)
        # groupNameLayout.addWidget(self.groupNameLineEdit)
        # mainLayout.addLayout(groupNameLayout)
        #
        # # List of Objects to Group
        # objectsLabel = QtWidgets.QLabel("Objects to Group:")
        # mainLayout.addWidget(objectsLabel)
        # self.objectsListWidget = QtWidgets.QListWidget()
        # self.objectsListWidget.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)  # Not selectable
        # self.objectsListWidget.setMinimumHeight(100)
        # mainLayout.addWidget(self.objectsListWidget)
        #
        # # Buttons
        # buttonLayout = QtWidgets.QHBoxLayout()
        # self.groupButton = QtWidgets.QPushButton("Group")
        # self.cancelButton = QtWidgets.QPushButton("Cancel")
        # buttonLayout.addStretch()  # Push buttons to the right
        # buttonLayout.addWidget(self.groupButton)
        # buttonLayout.addWidget(self.cancelButton)
        # mainLayout.addLayout(buttonLayout)

        # Connections

    @classmethod
    def showUI(cls, parent = None):
        if cls._instance and cls._instance.isVisible():
            cls._instance.raise_()
            cls._instance.activateWindow()
            cls._instance.findSelectionToGroup()
            return

        if cls._instance:
            cls._instance.deleteLater()

        cls._instance = cls(parent = parent)
        cls._instance.exec_()

