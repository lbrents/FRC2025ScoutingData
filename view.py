
from enum import Enum

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
import pandas as pd

from model import Spreadsheets



class QStatCell(QTableWidgetItem):
    
    def __init__(self, value: float, precision: int = 2, percent: bool = False):
        super().__init__()

        text = f"{ int(value) if precision == 0 else round(value, precision)}" \
            + ("%" if percent else "")
        self.setText(text)

        self.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFlags(self.flags() &~ Qt.ItemFlag.ItemIsEditable)

class QTeamsTableController(QWidget):
    """Exposes a list of buttons that are intended to sort the main table."""

    # Components
    teamNumber: QPushButton
    leaveFrq: QPushButton
    autonCycles: QPushButton
    teleopCycles: QPushButton
    climbFrq: QPushButton
    disableFrq: QPushButton
    reverseSort: QCheckBox

    def __init__(self):
        super().__init__()

        # Set properties
        self.setMaximumWidth(128)

        # Instantiate components
        mainLayout = QVBoxLayout()

        label = QLabel("Sort")
        self.teamNumber   = QPushButton("Team Number")
        self.leaveFrq     = QPushButton("Leave Frq")
        self.autonCycles  = QPushButton("Auton Cycles")
        self.teleopCycles = QPushButton("Teleop Cycles")
        self.climbFrq     = QPushButton("Climb Frq")
        self.disableFrq   = QPushButton("Disable Frq")
        separator = QFrame()
        self.reverseSort = QCheckBox("Reverse")

        # Add Components
        self.setLayout(mainLayout)
        
        mainLayout.addWidget(label)
        mainLayout.addWidget(self.teamNumber)
        mainLayout.addWidget(self.leaveFrq)
        mainLayout.addWidget(self.autonCycles)
        mainLayout.addWidget(self.teleopCycles)
        mainLayout.addWidget(self.climbFrq)
        mainLayout.addWidget(self.disableFrq)

        mainLayout.addSpacing(8)
        mainLayout.addWidget(separator)
        
        mainLayout.addWidget(self.reverseSort)
        mainLayout.addStretch()

        # Set component properties
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        separator.setFrameShape(QFrame.Shape.HLine)

class QTeamsDisplayTable(QTableWidget):

    class Sort(Enum):
        TeamNumber   = "Team Number"
        LeaveFrq     = "Leave Frq"
        AutonCycles  = "Auton Cycles"
        TeleopCycles = "Teleop Cycles"
        ClimbFrq     = "Climb Frq"
        DisableFrq   = "Disable Frq"

    # Variables
    data: pd.DataFrame
    currentSort: Sort
    reverse: bool

    def __init__(self, data: pd.DataFrame):
        super().__init__()

        # Set variables
        self.setData(data)
        self.currentSort = self.Sort.TeamNumber
        self.reverse = False

        # Guard check
        if data.empty:
            return

        # Add components
        self.populate()

    def setData(self, data: pd.DataFrame) -> None:
        self.data = data

        self.clear()

        rows, cols = self.data.shape
        self.setRowCount(rows)
        self.setColumnCount(cols)
        self.setHorizontalHeaderLabels(self.data.head())
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        hHeader = self.horizontalHeader()
        hHeader.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        hHeader.setSectionsClickable(False)

    def populate(self) -> None:
        self.clearSelection()

        self.data.sort_values(
            by = self.currentSort.value,
            ascending = not self.reverse,
            inplace = True
        )

        i_int = [0]
        i_frq = [1, 4, 5]
        for r_index, (_, row) in enumerate(self.data.iterrows()):
            for c_index, col in enumerate(row):
                item = QStatCell(col, 0 if c_index in i_int else 2, c_index in i_frq)
                self.setItem(r_index, c_index, item)

    def setSort(self, sort: Sort) -> None:
        self.currentSort = sort
        self.populate()

    def setReverse(self, reverse: bool) -> None:
        self.reverse = reverse
        self.populate()

    def toggleReverse(self) -> None:
        self.setReverse(not self.reverse)

    def getSelectedTeamNumber(self) -> int:
        if self.selectedItems() == []:
            return 0
        return int(self.selectedItems()[0].text())

class QTeamDetailsTable(QWidget):

    # Components
    teamLabel: QLabel
    notesList: QListWidget
    autonTable: QTableWidget
    teleopTable: QTableWidget
    extrasTable: QTableWidget

    def __init__(self):
        super().__init__()

        # Instantiate widgets
        mainLayout = QHBoxLayout()
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        leftWidget = QWidget()
        leftLayout = QVBoxLayout()

        labelLayout = QHBoxLayout()
        self.teamLabel = QLabel("Team: [ Blank ]")
        self.notesList = QListWidget()

        rightWidget = QWidget()
        rightLayout = QHBoxLayout()

        self.autonTable = QTableWidget(8, 3)
        self.teleopTable = QTableWidget(7, 3)
        self.extrasTable = QTableWidget(5, 1)

        # Add components
        self.setLayout(mainLayout)
        mainLayout.addWidget(splitter)

        splitter.addWidget(leftWidget)
        leftWidget.setLayout(leftLayout)
        
        leftLayout.addLayout(labelLayout)
        labelLayout.addStretch()
        labelLayout.addWidget(self.teamLabel)
        labelLayout.addStretch()
        leftLayout.addWidget(self.notesList)

        splitter.addWidget(rightWidget)
        rightWidget.setLayout(rightLayout)

        rightLayout.addWidget(self.autonTable)
        rightLayout.addWidget(self.teleopTable)
        rightLayout.addWidget(self.extrasTable)

        # Set component properties
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        rightLayout.setStretch(0, 2)
        rightLayout.setStretch(1, 2)
        rightLayout.setStretch(2, 1)

        self.autonTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.autonTable.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.autonTable.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)

        self.teleopTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.teleopTable.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.teleopTable.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)

        self.extrasTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.extrasTable.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.extrasTable.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)

    def populate(self, teamNumber: int, teamData: tuple[int, pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]) -> None:

        # Unpack teamData
        (teamNumber, auton, teleop, extra, notes) = teamData

        # Error check
        if teamNumber == 0:
            return

        # Set the team number label
        self.teamLabel.setText(f"Team: {teamNumber}")

        # Populate the notes list
        self.notesList.clear()
        self.notesList.setWordWrap(True)
        self.notesList.setSpacing(4)
        self.notesList.addItems([ note for note in notes ])

        # Populate the auton table
        self.autonTable.setHorizontalHeaderLabels(["Avg", "Min", "Max"])
        self.autonTable.setVerticalHeaderLabels(auton.head())
        for c_index, (_, col) in enumerate(auton.iterrows()):
            for r_index, value in enumerate(col):
                item = QStatCell(value)
                self.autonTable.setItem(r_index, c_index, item)

        # Populate the teleop table
        self.teleopTable.setHorizontalHeaderLabels(["Avg", "Min", "Max"])
        self.teleopTable.setVerticalHeaderLabels(teleop.head())
        for c_index, (_, col) in enumerate(teleop.iterrows()):
            for r_index, value in enumerate(col):
                item = QStatCell(value)
                self.teleopTable.setItem(r_index, c_index, item)

        # Populate the extras table
        self.extrasTable.setHorizontalHeaderLabels(["Frq"])
        self.extrasTable.setVerticalHeaderLabels(extra.index)
        for index, value in enumerate(extra):
            item = QStatCell(value, percent = True)
            self.extrasTable.setItem(index, 0, item)

