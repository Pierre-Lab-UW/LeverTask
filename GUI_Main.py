import os
import sys


from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QWidget, QScrollArea, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, \
    QLineEdit, QFileDialog
from PyQt5.QtGui import QIcon



class MainWindow(QWidget):



    def __init__(self):
        super().__init__()

        input_prams = {"Subject", "Date", "study code", "Initials", "Schedule", "Schedule Parameter", "Session Length",
                       "Timeout", "ITI", "RewardNum", "Reward Delay"}

        # Set the main window's properties

        self.setWindowTitle('LEVER_INPUT_PARAMS')
        self.setGeometry(300, 300, 500, 200)

        # Store QLineEdit references
        self.input_fields = {}

        # Create a QScrollArea
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)

        # Create a QWidget for your contents
        content = QWidget()
        scroll.setWidget(content)

        self.filename = None

        # Layout for the contents inside the scroll area
        layout = QVBoxLayout(content)

        h_layout = QHBoxLayout()
        layout.addLayout(h_layout)  # add this functionality of horizontal layout the main GUI

        # create horizontal layout

        self.setLayout(layout)

        # Add some widgets to the layout
        for p in input_prams:
            layout.addWidget(QLabel(p, self))
            text_input = QLineEdit()
            self.input_fields[p] = text_input
            layout.addWidget(text_input)

        # Set the layout for the main window
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll)

        # self.input_fields[param] = text_input

        button = QPushButton("Save Parameters")
        layout.addWidget(button)
        button.clicked.connect(self.on_click)  # Connect the button's clicked signal to the on_click slot

        button = QPushButton("OpenFile")
        layout.addWidget(button)
        button.clicked.connect(self.openFileNameDialog)  # Connect the button's clicked signal to the on_click slot




    # saves to the LeverParameter File
    @pyqtSlot()
    def on_click(self):

      if os.path.exists(self.filename):
          # Collect data from input fields
          written_result: str = ""
          for p, text_input in self.input_fields.items():
              written_result += text_input.text() + ","

          # Remove the last comma to avoid an extra column in CSV
          written_result = written_result.rstrip(',')

          # Append data to the file with a newline to ensure it starts on a new line
          with open(self.filename, "a") as file:
            file.write(written_result + "\n")
            print(written_result)


    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "CSV Files (*.csv)")
        print(file_path) # test if its working





if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
