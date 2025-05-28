import os
from pathlib import Path

import pandas as pd

class Spreadsheets:

    root: Path
    data: pd.DataFrame
    teamNumbers: list[int]

    @property
    def isLoaded(self) -> bool:
        return not self.data.empty

    def __init__(self, root: Path | None):
        self.loadData(root)

    def loadData(self, root: Path):
        self.root = root
        self.__import_data()
        self.__load_team_numbers()

    def __import_data(self) -> None:
        # Check if root is not none
        if self.root == None:
            self.data = pd.DataFrame()
            return

        # Check if root is valid
        if not self.root.is_dir():
            self.data = pd.DataFrame()
            return

        # Get all .csv paths in the given folder
        paths = [ f"{self.root}/{path}" for path in os.listdir(self.root) if path.endswith(".csv") ]
        
        # Check if no csv paths were found
        if paths == []:
            self.data = pd.DataFrame()
            return

        # Load each spreadsheet as a DataFrame
        self.data = pd.concat( [ pd.read_csv(path) for path in paths ] )

    def __load_team_numbers(self):
        self.teamNumbers = self.data["teamNumber"].unique() if self.isLoaded else []

    def getTeamMatches(self, teamNumber: int) -> pd.DataFrame:
        """Given a team number that exists, returns a DataFrame of that team's matches."""

        if not self.isLoaded:
            return pd.DataFrame()

        if teamNumber not in self.teamNumbers:
            return pd.DataFrame()

        return self.data[ self.data["teamNumber"] == teamNumber ]

    def __avg_auton_coral_cycles(self, teamData: pd.DataFrame) -> float:
        return (
            teamData["autonCoralL1"].sum() +
            teamData["autonCoralL2"].sum() +
            teamData["autonCoralL3"].sum() +
            teamData["autonCoralL4"].sum()
        ) / teamData.shape[0]

    def __avg_teleop_coral_cycles(self, teamData: pd.DataFrame) -> float:
        return (
            teamData["teleopCoralL1"].sum() +
            teamData["teleopCoralL2"].sum() +
            teamData["teleopCoralL3"].sum() +
            teamData["teleopCoralL4"].sum()
        ) / teamData.shape[0]

    def __avg_climb_frequency(self, teamData: pd.DataFrame) -> float:
        occurrences = teamData["climbState"].value_counts()
        return (
            occurrences.get(2, 0) +
            occurrences.get(3, 0)
        ) / self.data.shape[0]

    def getTeamDisplayStats(self, teamNumber: int) -> pd.Series:
        """Given a team number that exists, calculates stats as a dict to display alongside other teams."""

        if not self.isLoaded:
            return pd.Series()

        teamData = self.getTeamMatches(teamNumber)

        if teamData.empty:
            return pd.Series()

        return pd.Series({
            "Team Number"   : teamData["teamNumber"].iloc[0],
            "Leave Frq"     : teamData["autonLeave"].mean() * 100,
            "Auton Cycles"  : self.__avg_auton_coral_cycles(teamData),
            "Teleop Cycles" : self.__avg_teleop_coral_cycles(teamData),
            "Climb Frq"     : self.__avg_climb_frequency(teamData) * 100,
            "Disable Frq"   : teamData["didRobotDisable"].mean() * 100
        })

    def getAllTeamDisplayStats(self) -> pd.DataFrame:
        """Retrieves all team data and calculates their display stats."""

        if not self.isLoaded:
            return pd.DataFrame()

        return pd.DataFrame([ self.getTeamDisplayStats(teamNumber) for teamNumber in self.teamNumbers ])

    def __avg_climb_state(self, occurrences: pd.Series, index: int) -> float:
        return (occurrences.get(index, 0) / occurrences.sum()) * 100

    def getTeamDetailedStats(self, teamNumber: int) -> tuple[int, pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """Given a team number that exists, calculates in depths stats for that team."""

        if not self.isLoaded:
            return (0, pd.DataFrame(), pd.DataFrame(), pd.Series(), pd.Series())

        teamData = self.getTeamMatches(teamNumber)

        if teamData.empty:
            return (0, pd.DataFrame(), pd.DataFrame(), pd.Series(), pd.Series())

        # Define labels to drop
        colsToDrop = ["uid", "onShift", "matchNumber", "teamNumber", "climbState", "additionalNotes"]
        rowsToDrop = ["count", "std", "25%", "50%", "75%"]

        # Calculate basic stats DataFrame
        stats = teamData.drop(colsToDrop, axis = 1).describe().drop(rowsToDrop, axis = 0)

        # Calculate auton
        auton = pd.DataFrame({
            "Auton Leave Frq" : stats["autonLeave"],
            "Auton L1"        : stats["autonCoralL1"],
            "Auton L2"        : stats["autonCoralL2"],
            "Auton L3"        : stats["autonCoralL3"],
            "Auton L4"        : stats["autonCoralL4"],
            "Auton Processor" : stats["autonAlgaeProcessor"],
            "Auton Net"       : stats["autonAlgaeNet"],
            "Algae Removed"   : stats["autonAlgaeRemoved"]
        })

        # Calculate teleop
        teleop = pd.DataFrame({
            "Teleop L1"        : stats["teleopCoralL1"],
            "Teleop L2"        : stats["teleopCoralL2"],
            "Teleop L3"        : stats["teleopCoralL3"],
            "Teleop L4"        : stats["teleopCoralL4"],
            "Teleop Processor" : stats["teleopAlgaeProcessor"],
            "Teleop Net"       : stats["teleopAlgaeNet"],
            "Algae Removed"    : stats["teleopAlgaeRemoved"]
        })

        # Calculate extra
        occurrences = teamData["climbState"].value_counts()
        extra = pd.Series({
            "No Climb" : self.__avg_climb_state(occurrences, 0),
            "Parked"   : self.__avg_climb_state(occurrences, 1),
            "Shallow"  : self.__avg_climb_state(occurrences, 2),
            "Deep"     : self.__avg_climb_state(occurrences, 3),
            "Disable"  : stats["didRobotDisable"]["mean"] * 100
        })

        # Calculate notes
        notesSeries = teamData.loc[ teamData["additionalNotes"].notnull() ][["additionalNotes", "matchNumber"]]
        notes = pd.Series(
            { row["matchNumber"] : f"Match {row["matchNumber"]:.0f}: {row["additionalNotes"]}" for (_, row) in notesSeries.iterrows() }
        )

        return (teamNumber, auton, teleop, extra, notes)



