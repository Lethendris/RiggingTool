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
        mainLayout.setSpacing(10)

        nameLayout = QtWidgets.QHBoxLayout()
        nameLayout.setSpacing(4)
        positionLayout = QtWidgets.QHBoxLayout()
        positionLayout.setSpacing(4)
        buttonLayout = QtWidgets.QHBoxLayout()
        buttonLayout.setSpacing(4)

        self.groupNameLabel = QtWidgets.QLabel('Group Name:')
        self.groupNameLabel.setMinimumWidth(80)

        self.groupLineEdit = QtWidgets.QLineEdit()
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

