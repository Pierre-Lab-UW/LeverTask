import os
import sys

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import (
    QApplication, QWidget, QScrollArea, QVBoxLayout, QPushButton,
    QLabel, QLineEdit, QFileDialog, QHBoxLayout
)


class ParamWindow(QWidget):
    def __init__(self, param_list, title, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setGeometry(400, 400, 400, 400)
        self.param_list = param_list
        self.input_fields = {}
        self.filename = None

        layout = QVBoxLayout(self)

        for param in param_list:
            label = QLabel(param)
            input_box = QLineEdit()
            self.input_fields[param] = input_box
            layout.addWidget(label)
            layout.addWidget(input_box)

        save_button = QPushButton("Save to CSV")
        save_button.clicked.connect(self.save_parameters)
        layout.addWidget(save_button)

        open_button = QPushButton("Select CSV File")
        open_button.clicked.connect(self.openFileNameDialog)
        layout.addWidget(open_button)

    def openFileNameDialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "CSV Files (*.csv)")
        if file_path:
            self.filename = file_path
            print("Selected file:", file_path)

    @pyqtSlot()
    def save_parameters(self):
        if self.filename:
            # Collect values from all input fields
            values = []
            for param in self.param_list:
                value = self.input_fields[param].text()
                values.append(value)

            # Join all values into a single CSV-formatted string
            written_result = ",".join(values)
            with open(self.filename, "a") as f:
                f.write(written_result + "\n")
            print("Saved:", written_result)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Select Parameter Type")
        self.setGeometry(300, 300, 300, 150)

        self.lever_params = [
            "Subject", "Date", "study code", "Initials", "Schedule",
            "Schedule Parameter", "Session Length", "Timeout", "ITI",
            "RewardNum", "Reward Delay"
        ]
        self.go_no_go_params = [
            "subject", "ITI", "NG_DELAY_PERIOD", "RatioTrials", "Reward", "AbortTrialTime"
        ]

        layout = QVBoxLayout(self)

        label = QLabel("Choose which parameters to edit:")
        layout.addWidget(label)

        lever_btn = QPushButton("Edit LEVER_PARAMS")
        lever_btn.clicked.connect(self.open_lever_params)
        layout.addWidget(lever_btn)

        gng_btn = QPushButton("Edit GO_NO_GO")
        gng_btn.clicked.connect(self.open_go_no_go)
        layout.addWidget(gng_btn)

    def open_lever_params(self):
        self.param_window = ParamWindow(self.lever_params, "LEVER_PARAMS")
        self.param_window.show()

    def open_go_no_go(self):
        self.param_window = ParamWindow(self.go_no_go_params, "GO_NO_GO")
        self.param_window.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
