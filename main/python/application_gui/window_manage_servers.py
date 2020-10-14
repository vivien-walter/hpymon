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

class manageServerWindow(qtw.QMainWindow):
    def __init__(self, parent):
        super(manageServerWindow, self).__init__(parent)

        # Initialise the subwindow
        self.parent = parent

        self.mainWidget = qtw.QWidget()
        self.mainLayout = qtw.QVBoxLayout(self.mainWidget)
        self.setWindowTitle("Manage Servers")

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
        self.parent.subWindows['manage_servers'] = None

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
        self.serversTable = qtw.QTableWidget(0, 4)
        self.serversTable.setHorizontalHeaderLabels( ['', '', 'Name', 'Address'] )

        self.serversTable.setSelectionMode(qtw.QAbstractItemView.NoSelection)
        self.serversTable.setEditTriggers(qtw.QAbstractItemView.NoEditTriggers)

        self.serversTable.setShowGrid(False)
        self.serversTable.setMinimumHeight(125)
        self.serverSettingsLayout.addWidget(self.serversTable)

        # Populate the widget
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

        # Add the new server button
        self.addServerButton = qtw.QPushButton("Add Server")
        self.addServerButton.clicked.connect(self.addServer)
        self.addServerButton.setStatusTip("Create a new server.")
        self.addServerButton.setFixedWidth(125)
        self.userActionsLayout.addWidget(self.addServerButton, alignment=qtc.Qt.AlignLeft)

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
        if len(self.parent.server_list) > 0:
            for i, (ip, name) in enumerate(self.parent.server_list):

                # Fill the rows
                self.serversTable.insertRow(i)

                # Prepare the edit button
                serverEditButton = qtw.QPushButton("Edit")
                serverEditButton.clicked.connect(partial(self.editServer, name=name))
                serverEditButton.setFixedWidth(75)

                # Prepare the edit button
                serverDeleteButton = qtw.QPushButton("Delete")
                serverDeleteButton.clicked.connect(partial(self.deleteServer, name=name))
                serverDeleteButton.setFixedWidth(75)

                # Fill the columns
                self.serversTable.setCellWidget(i, 0, serverEditButton)
                self.serversTable.setCellWidget(i, 1, serverDeleteButton)
                self.serversTable.setItem(i, 2, qtw.QTableWidgetItem(str(name)))
                self.serversTable.setItem(i, 3, qtw.QTableWidgetItem(str(ip)))

        # Resize the columns
        header = self.serversTable.horizontalHeader()
        for i in range( 4 ):
            header.setSectionResizeMode(i, qtw.QHeaderView.ResizeToContents)

    ##-\-\-\-\-\-\-\-\-\
    ## MANAGE THE SERVERS
    ##-/-/-/-/-/-/-/-/-/

    # ---------------------------------------------
    # Close the window and edit the selected server
    def addServer(self):

        # Open the edit settings window
        _open_window(self.parent, serverSettingsWindow, 'server_settings')

        # Close the current window
        self.close()

    # ---------------------------------------------
    # Close the window and edit the selected server
    def editServer(self, name=None):

        # Open the edit settings window
        _open_window(self.parent, serverSettingsWindow, 'server_settings', opened_server=name, replace=True)

        # Close the current window
        self.close()

    # ---------------------------------------------
    # Delete the selected server
    def deleteServer(self, name=None):

        # Display a warning message before proceeding
        if warningMessage('Delete Server','Are you sure you want to delete this server from the memory?'):

            # Delete from the file
            removeServer(name)

            # Refresh the main server list
            self.parent.refreshServerList()

            # Refresh the display
            self.updateServerList()
