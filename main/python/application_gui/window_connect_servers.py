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

class connectServersWindow(qtw.QMainWindow):
    def __init__(self, parent):
        super(connectServersWindow, self).__init__(parent)

        # Initialise the subwindow
        self.parent = parent

        self.mainWidget = qtw.QWidget()
        self.mainLayout = qtw.QVBoxLayout(self.mainWidget)
        self.setWindowTitle("Connect To Server")

        # Populate the panel
        self.createListServers(self.mainLayout)
        self.createUserActions(self.mainLayout)

        # Display the panel
        self.mainWidget.setLayout(self.mainLayout)
        self.setCentralWidget(self.mainWidget)
        self.show()
        self.resize(450, 200)
        self.setFixedSize(self.size())

    # ---------------------------------------------------
    # Reinitialise the display when the window is closed
    def closeEvent(self, event=None):
        event.accept()
        self.parent.subWindows['connect_servers'] = None

    ##-\-\-\-\-\-\-\-\-\-\
    ## GENERATE THE DISPLAY
    ##-/-/-/-/-/-/-/-/-/-/

    # --------------------------------------
    # Generate the server settings selection
    def createListServers(self, parentWidget):

        # Generate the widget
        self.serverSettingsWidget = qtw.QWidget()
        self.serverSettingsLayout = qtw.QVBoxLayout(self.serverSettingsWidget)

        # Generate the table of servers
        self.serversTable = qtw.QTableWidget(0, 3)
        self.serversTable.setHorizontalHeaderLabels( ['', 'Name', 'Address'] )

        self.serversTable.setSelectionMode(qtw.QAbstractItemView.NoSelection)
        self.serversTable.setEditTriggers(qtw.QAbstractItemView.NoEditTriggers)

        self.serversTable.setShowGrid(False)
        self.serversTable.setMinimumHeight(125)
        self.serverSettingsLayout.addWidget(self.serversTable)

        # Populate the table
        self.updateServerList()

        # Display the widget
        self.serverSettingsWidget.setLayout(self.serverSettingsLayout)
        parentWidget.addWidget(self.serverSettingsWidget)

    # --------------------------------------
    # Generate the control of the image zoom
    def createUserActions(self, parentWidget):

        # Generate the widget
        self.userActionsWidget = qtw.QWidget()
        self.userActionsLayout = qtw.QHBoxLayout(self.userActionsWidget)

        # Add the close button
        self.closeButton = qtw.QPushButton("Close")
        self.closeButton.clicked.connect(self.close)
        self.closeButton.setStatusTip("Close the current window.")
        self.closeButton.setFixedWidth(125)
        self.userActionsLayout.addWidget(self.closeButton, alignment=qtc.Qt.AlignRight)

        # Display the widget
        self.userActionsWidget.setLayout(self.userActionsLayout)
        parentWidget.addWidget(self.userActionsWidget)

    ##-\-\-\-\-\-\-\-\-\
    ## UPDATE THE DISPLAY
    ##-/-/-/-/-/-/-/-/-/

    # ----------------------------
    # Populate the list of servers
    def updateServerList(self):

        # Delete the values
        rowCount = self.serversTable.rowCount()
        if rowCount > 0:
            for i in range(rowCount):
                self.serversTable.removeRow(0)

        # Fill the table
        if len(self.parent.server_jobs) > 0:
            for i, (ip, name) in enumerate(self.parent.server_jobs):

                # Fill the rows
                self.serversTable.insertRow(i)

                # Prepare the connect button
                serverEditButton = qtw.QPushButton("Connect")
                serverEditButton.clicked.connect(partial(self.connectServer, name=name))
                serverEditButton.setFixedWidth(125)

                # Fill the columns
                self.serversTable.setCellWidget(i, 0, serverEditButton)
                self.serversTable.setItem(i, 1, qtw.QTableWidgetItem(str(name)))
                self.serversTable.setItem(i, 2, qtw.QTableWidgetItem(str(ip)))

        # Resize the columns
        header = self.serversTable.horizontalHeader()
        for i in range( 3 ):
            header.setSectionResizeMode(i, qtw.QHeaderView.ResizeToContents)

    ##-\-\-\-\-\-\-\-\-\
    ## MANAGE THE SERVERS
    ##-/-/-/-/-/-/-/-/-/

    # ---------------------------------------------
    # Close the window and edit the selected server
    def connectServer(self, name=None):

        # Get the server IP
        self.parent.connectSingleServer(name=name)

        # Close the current window
        self.close()
