import sys, os

from pathlib import Path

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
import pandas as pd

from model import Spreadsheets
from view import QTeamsTableController, QTeamsDisplayTable, QTeamDetailsTable

class MainWindow(QMainWindow):

    # Constants
    WINDOW_TITLE = "Scouting 2025 Analysis"
    ASPECT_RATIO = (4, 3)
    SIZE_MULTIPLIER = 256

    DATA_PATH = None

    # Variables
    data: Spreadsheets

    # Components
    errorLabel: QLabel
    mainSplitter: QSplitter
    teamsTableController: QTeamsTableController
    teamsDisplayTable: QTeamsDisplayTable
    teamDetailsTable: QTeamDetailsTable

    def __init__(self):
        super().__init__()

        # Variables
        self.data = Spreadsheets(None)

        # Window settings
        self.setWindowTitle(self.WINDOW_TITLE)
        self.setMinimumWidth(self.ASPECT_RATIO[0] * self.SIZE_MULTIPLIER)
        self.setMinimumHeight(self.ASPECT_RATIO[1] * self.SIZE_MULTIPLIER)

        # Instantiate components
        self.errorWidget = QWidget()
        errorLayout = QVBoxLayout()
        errorLabel = QLabel("No data is loaded")
        self.errorButton = QPushButton("Select Folder")

        self.mainSplitter = QSplitter(Qt.Orientation.Vertical)
        
        topWidget = QWidget()
        topLayout = QHBoxLayout()

        self.teamsTableController = QTeamsTableController()
        self.teamsDisplayTable = QTeamsDisplayTable(self.data.getAllTeamDisplayStats())

        self.teamDetailsTable = QTeamDetailsTable()

        # Add components
        if self.data.isLoaded:
            self.setCentralWidget(self.mainSplitter)
        else:
            self.setCentralWidget(self.errorWidget)

        self.errorWidget.setLayout(errorLayout)
        errorLayout.addWidget(errorLabel)
        errorLayout.addWidget(self.errorButton)

        self.mainSplitter.addWidget(topWidget)
        topWidget.setLayout(topLayout)

        topLayout.addWidget(self.teamsTableController)
        topLayout.addWidget(self.teamsDisplayTable)

        self.mainSplitter.addWidget(self.teamDetailsTable)

        # Set component properties
        errorLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        errorLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.errorButton.setFixedWidth(128)

        # Add Signals
        self.errorButton.clicked.connect(self.__set_data_folder)

        self.teamsTableController.teamNumber.clicked.connect(
            lambda: self.teamsDisplayTable.setSort(QTeamsDisplayTable.Sort.TeamNumber)
        )
        self.teamsTableController.leaveFrq.clicked.connect(
            lambda: self.teamsDisplayTable.setSort(QTeamsDisplayTable.Sort.LeaveFrq)
        )
        self.teamsTableController.autonCycles.clicked.connect(
            lambda: self.teamsDisplayTable.setSort(QTeamsDisplayTable.Sort.AutonCycles)
        )
        self.teamsTableController.teleopCycles.clicked.connect(
            lambda: self.teamsDisplayTable.setSort(QTeamsDisplayTable.Sort.TeleopCycles)
        )
        self.teamsTableController.climbFrq.clicked.connect(
            lambda: self.teamsDisplayTable.setSort(QTeamsDisplayTable.Sort.ClimbFrq)
        )
        self.teamsTableController.disableFrq.clicked.connect(
            lambda: self.teamsDisplayTable.setSort(QTeamsDisplayTable.Sort.DisableFrq)
        )
        self.teamsTableController.reverseSort.clicked.connect(
            self.teamsDisplayTable.toggleReverse
        )

        self.teamsDisplayTable.itemSelectionChanged.connect(
            self.__set_details_table
        )

    def __set_data_folder(self) -> None:
        path = Path(QFileDialog.getExistingDirectory())
        self.data.loadData(path)
        if self.data.isLoaded:
            self.teamsDisplayTable.setData(self.data.getAllTeamDisplayStats())
            self.teamsDisplayTable.populate()
            self.setCentralWidget(self.mainSplitter)

    def __set_details_table(self) -> None:
        selectedTeam = self.teamsDisplayTable.getSelectedTeamNumber()
        if selectedTeam == 0:
            return

        self.teamDetailsTable.populate(
            selectedTeam,
            self.data.getTeamDetailedStats(selectedTeam)
        )

if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())