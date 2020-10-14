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

class aboutHelpWindow(qtw.QMainWindow):
    def __init__(self, parent):
        super(aboutHelpWindow, self).__init__(parent)

        # Initialise the subwindow
        self.parent = parent
        self.setWindowModality(qtc.Qt.ApplicationModal)

        self.mainWidget = qtw.QWidget()
        self.mainLayout = qtw.QVBoxLayout(self.mainWidget)
        self.setWindowTitle('About...')

        # Show the logo
        imageWidget = qtw.QLabel()
        image = qtg.QPixmap( self.parent.appctxt.get_resource('hpymon_logo.png') )
        imageWidget.setPixmap(image)
        self.mainLayout.addWidget(imageWidget, alignment=qtc.Qt.AlignCenter)

        # Show the title
        titleText = CLabel("H-PyMon - beta version")
        self.mainLayout.addWidget(titleText, alignment=qtc.Qt.AlignCenter)

        # Show the text
        aboutText = qtw.QLabel("""Release Date: 14/10/2020
Author: Vivien Walter
Contact: walter.vivien@gmail.com

More information and documentation can be found on the website of the software:
https://github.com/vivien-walter/hpymon""")
        self.mainLayout.addWidget(aboutText)#, alignment=qtc.Qt.AlignCenter)

        # Exit button
        self.exitButton = qtw.QPushButton("Close")
        self.exitButton.setFixedWidth(125)
        self.exitButton.clicked.connect(self.close)
        self.mainLayout.addWidget(self.exitButton, alignment=qtc.Qt.AlignCenter)

        # Display the panel
        #self.mainLayout.setAlignment(qtc.Qt.AlignCenter)
        self.mainWidget.setLayout(self.mainLayout)
        self.setCentralWidget(self.mainWidget)
        self.resize(300, 300)
        self.show()
        self.setFixedSize(self.size())

    # ---------------------------------------------------
    # Reinitialise the display when the window is closed
    def closeEvent(self, event=None):
        event.accept()
        self.parent.subWindows['about'] = None
