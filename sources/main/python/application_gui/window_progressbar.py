import PyQt5.QtCore as qtc
import PyQt5.QtGui as qtg
import PyQt5.QtWidgets as qtw

from functools import partial

from application_gui.common_gui_functions import CLabel, CHorizontalSeparator, warningMessage, _open_window
from application_gui.window_server_settings import serverSettingsWindow

from settings import addServer, serverExists, removeServer
from ssh_protocol import generateServer

##-\-\-\-\-\-\-\-\-\-\-\-\
## WINDOW FOR USER SETTINGS
##-/-/-/-/-/-/-/-/-/-/-/-/

class progressBarWindow(qtw.QMainWindow):
    def __init__(self, parent, title=None, text=None):
        super(progressBarWindow, self).__init__(parent)

        # Initialise the subwindow
        self.parent = parent
        self.setWindowModality(qtc.Qt.ApplicationModal)

        self.mainWidget = qtw.QWidget()
        self.mainLayout = qtw.QVBoxLayout(self.mainWidget)
        self.setWindowTitle(title)

        # Show the progress bar text
        self.progressBarLabel = CLabel(text)
        self.mainLayout.addWidget(self.progressBarLabel, alignment=qtc.Qt.AlignCenter)

        # Show the progress bar
        self.progressBarWidget = qtw.QProgressBar()
        self.mainLayout.addWidget(self.progressBarWidget)

        # Close and minimize properties
        self.setWindowFlags(self.windowFlags() | qtc.Qt.CustomizeWindowHint)
        self.setWindowFlag(qtc.Qt.WindowMinimizeButtonHint, False)
        self.setWindowFlag(qtc.Qt.WindowCloseButtonHint, False)

        # Display the panel
        self.mainLayout.setAlignment(qtc.Qt.AlignCenter)
        self.mainWidget.setLayout(self.mainLayout)
        self.setCentralWidget(self.mainWidget)
        self.resize(300, 175)
        self.show()
        self.setFixedSize(self.size())

    # ---------------------------------------------------
    # Reinitialise the display when the window is closed
    def closeEvent(self, event=None):
        event.accept()
        self.parent.subWindows['progress_bar'] = None

    ##-\-\-\-\-\-\-\-\-\
    ## UPDATE THE DISPLAY
    ##-/-/-/-/-/-/-/-/-/

    # -------------------------------------
    # Update the status of the progress bar
    def updateProgress(self, new_text, bar_progress=0):

        # Close the current window
        if bar_progress >= 100:
            self.close()

        # Update the text display
        self.progressBarLabel.setText( new_text )

        # Update the status of the progress bar
        self.progressBarWidget.setValue(bar_progress)
