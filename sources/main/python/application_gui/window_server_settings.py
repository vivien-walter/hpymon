import PyQt5.QtCore as qtc
import PyQt5.QtGui as qtg
import PyQt5.QtWidgets as qtw

from application_gui.common_gui_functions import CLabel, CHorizontalSeparator, warningMessage, CLabelledLineEdit

from settings import addServer, serverExists, getDisplayList
from ssh_protocol import generateServer

##-\-\-\-\-\-\-\-\-\-\-\-\
## WINDOW FOR USER SETTINGS
##-/-/-/-/-/-/-/-/-/-/-/-/

class serverSettingsWindow(qtw.QMainWindow):
    def __init__(self, parent, opened_server=None, replace=False):
        super(serverSettingsWindow, self).__init__(parent)

        # Initialise the subwindow
        self.parent = parent

        self.mainWidget = qtw.QWidget()
        self.mainLayout = qtw.QVBoxLayout(self.mainWidget)
        self.setWindowTitle("Server Settings")

        # Load the server to display
        if opened_server is None:
            self.defaultServer()
        else:
            self.loadServer(opened_server)
        self.replace = replace

        # Populate the panel
        self.createTabDisplay(self.mainLayout)
        self.createUserActions(self.mainLayout)

        # Display the panel
        self.mainWidget.setLayout(self.mainLayout)
        self.setCentralWidget(self.mainWidget)
        self.show()
        self.setFixedSize(self.size())

    # ---------------------------------------------------
    # Reinitialise the display when the window is closed
    def closeEvent(self, event=None):
        event.accept()
        self.parent.subWindows['server_settings'] = None

    ##-\-\-\-\-\-\-\-\-\-\
    ## GENERATE THE DISPLAY
    ##-/-/-/-/-/-/-/-/-/-/

    # -----------------------------------
    # Generate the tab widget for display
    def createTabDisplay(self, parentWidget):

        # Define the widget
        self.tabWidget = qtw.QTabWidget()

        # Add the basic user settings tab
        self.tabWidget.addTab(self.createServerSettings(), "Connection")

        # Add the advanced user settings tab
        self.tabWidget.addTab(self.createTunnelSettings(), "Tunnel")

        # Add the advanced user settings tab
        self.tabWidget.addTab(self.createAdvancedSettings(), "Advanced")

        # Load the widget
        parentWidget.addWidget(self.tabWidget)

    # --------------------------------------
    # Generate the server settings selection
    def createServerSettings(self):

        # Generate the widget
        self.serverSettingsWidget = qtw.QWidget()
        self.serverSettingsLayout = qtw.QGridLayout(self.serverSettingsWidget)

        # Add the name entry
        _currentRow = 0
        self.serverSettingsLayout.addWidget( CLabel("Server Name"), _currentRow, 0, 1, 1)
        self.serverNameEntry = qtw.QLineEdit()
        self.serverNameEntry.setText( self.server_details['name'] )
        self.serverNameEntry.setStatusTip("Name of the server.")
        self.serverSettingsLayout.addWidget( self.serverNameEntry, _currentRow, 1, 1, 1)

        # Add read job checkbox
        _currentRow += 1
        self.readJobsCheckBox = qtw.QCheckBox("Read job from this server?")
        self.readJobsCheckBox.setChecked( self.server_details['read_jobs'] )
        self.serverSettingsLayout.addWidget(self.readJobsCheckBox, _currentRow, 0, 1, -1)

        _currentRow += 1
        self.serverSettingsLayout.addWidget( CHorizontalSeparator(), _currentRow, 0, 1, -1)

        # Add the address entry
        _currentRow += 1
        self.serverSettingsLayout.addWidget( CLabel("Server Address"), _currentRow, 0, 1, 1)
        self.serverAddressEntry = qtw.QLineEdit()
        self.serverAddressEntry.setText( self.server_details['address'] )
        self.serverAddressEntry.setStatusTip("Address of the server.")
        self.serverSettingsLayout.addWidget( self.serverAddressEntry, _currentRow, 1, 1, 1)

        # Add the port entry
        _currentRow += 1
        self.serverSettingsLayout.addWidget( CLabel("Server Port"), _currentRow, 0, 1, 1)
        self.serverPortEntry = qtw.QLineEdit()
        self.serverPortEntry.setText( self.server_details['port'] )
        self.serverPortEntry.setStatusTip("Port of the server.")
        self.serverSettingsLayout.addWidget( self.serverPortEntry, _currentRow, 1, 1, 1)

        # Add the username entry
        _currentRow += 1
        self.serverSettingsLayout.addWidget( CLabel("Username"), _currentRow, 0, 1, 1)
        self.serverUserNameEntry = qtw.QLineEdit()
        self.serverUserNameEntry.setText( self.server_details['username'] )
        self.serverUserNameEntry.setStatusTip("Username to use to connect to the server.")
        self.serverSettingsLayout.addWidget( self.serverUserNameEntry, _currentRow, 1, 1, 1)

        # Identification type selection
        self.idTypeGroupButton = qtw.QButtonGroup(self.serverSettingsWidget)

        _currentRow += 1
        use_pkey = self.server_details['use_key']
        self.publicKeyRadiobutton = qtw.QRadioButton("Use a Public key")
        if use_pkey:
            self.publicKeyRadiobutton.setChecked(True)
        self.publicKeyRadiobutton.toggled.connect(self.updateIdentificationLabel)
        self.publicKeyRadiobutton.setStatusTip(
            "Use a public key to connect to the server."
        )
        self.idTypeGroupButton.addButton(self.publicKeyRadiobutton)
        self.serverSettingsLayout.addWidget(self.publicKeyRadiobutton, _currentRow, 0, 1, -1)

        _currentRow += 1
        self.passwordRadiobutton = qtw.QRadioButton("Use a Password")
        if not use_pkey:
            self.passwordRadiobutton.setChecked(True)
        self.passwordRadiobutton.toggled.connect(self.updateIdentificationLabel)
        self.passwordRadiobutton.setStatusTip(
            "Use a password to connect to the server."
        )
        self.idTypeGroupButton.addButton(self.passwordRadiobutton)
        self.serverSettingsLayout.addWidget(self.passwordRadiobutton, _currentRow, 0, 1, -1)

        # Add the identification entry
        _currentRow += 1
        self.indentificationLabel = CLabel("Path to Key")
        self.serverSettingsLayout.addWidget( self.indentificationLabel, _currentRow, 0, 1, 1)
        self.indentificationEntry = qtw.QLineEdit()
        self.indentificationEntry.setStatusTip("Identification to connect to the server.")
        self.updateIdentificationLabel()
        self.serverSettingsLayout.addWidget( self.indentificationEntry, _currentRow, 1, 1, 1)

        _currentRow += 1
        self.serverSettingsLayout.addWidget( CHorizontalSeparator(), _currentRow, 0, 1, -1)

        # Add use custom display checkbox
        _currentRow += 1
        self.useDisplayCheckBox = qtw.QCheckBox("Use custom display?")
        self.useDisplayCheckBox.setChecked( self.server_details['use_display'] )
        self.useDisplayCheckBox.toggled.connect(self.updateDisplayComboBox)
        self.serverSettingsLayout.addWidget(self.useDisplayCheckBox, _currentRow, 0, 1, -1)

        # Get the custom display list
        _custom_displays = getDisplayList()

        # Combobox to use the custom display
        _currentRow += 1
        self.customDisplayComboBox = qtw.QComboBox()
        self.customDisplayComboBox.addItem("---")
        for display_name in _custom_displays:
            self.customDisplayComboBox.addItem(display_name)
        self.customDisplayComboBox.setEnabled( self.server_details['use_display'] )

        # Select the default display
        if self.server_details['use_display']:
            _col_ID = self.customDisplayComboBox.findText(self.server_details['display_name'], qtc.Qt.MatchFixedString)
            self.customDisplayComboBox.setCurrentIndex(_col_ID)

        self.serverSettingsLayout.addWidget(self.customDisplayComboBox, _currentRow, 0, 1, -1)

        # Display the widget
        self.serverSettingsWidget.setLayout(self.serverSettingsLayout)
        return self.serverSettingsWidget
        #parentWidget.addWidget(self.serverSettingsWidget)

    # -----------------------------------------
    # Generate the tab with the tunnel settings
    def createTunnelSettings(self):

        # Generate the widget
        self.tunnelSettingsWidget = qtw.QWidget()
        self.tunnelSettingsLayout = qtw.QVBoxLayout(self.tunnelSettingsWidget)

        # Add use tunnel checkbox
        self.useTunnelCheckBox = qtw.QCheckBox("Use a tunnel?")
        self.useTunnelCheckBox.setChecked( self.server_details['use_tunnel'] )
        self.useTunnelCheckBox.toggled.connect(self.updateTunnelComboBox)
        self.tunnelSettingsLayout.addWidget(self.useTunnelCheckBox)

        # Add the tunnel label
        self.tunnelSettingsLayout.addWidget( CLabel("Tunnel through:"))

        # Add the tunnel selection
        self.tunnelServerComboBox = qtw.QComboBox()

        self.tunnelServerComboBox.addItem("---")
        for ip, server in self.parent.server_list:
            self.tunnelServerComboBox.addItem(server)

        # Set the pre-selected value
        if self.server_details['use_tunnel']:
            index = self.tunnelServerComboBox.findText(self.server_details['tunnel_selection'], qtc.Qt.MatchFixedString)
            if index >= 0:
                 self.tunnelServerComboBox.setCurrentIndex(index)
        else:
            self.tunnelServerComboBox.setDisabled(True)

        self.tunnelServerComboBox.setStatusTip(
            "Select the server to tunnel through."
        )
        self.tunnelSettingsLayout.addWidget(self.tunnelServerComboBox)

        # Display the widget
        self.tunnelSettingsLayout.setAlignment(qtc.Qt.AlignTop)
        self.tunnelSettingsWidget.setLayout(self.tunnelSettingsLayout)
        return self.tunnelSettingsWidget
        #parentWidget.addWidget(self.tunnelSettingsWidget)

    # ----------------------------------------
    # Generate the advanced settings selection
    def createAdvancedSettings(self):

        # Generate the widget
        self.advancedSettingsWidget = qtw.QWidget()
        self.advancedSettingsLayout = qtw.QVBoxLayout(self.advancedSettingsWidget)

        # Username checkbox
        self.jobUserNameCheckBox = qtw.QCheckBox("Use same Username in job query?")
        self.jobUserNameCheckBox.setChecked( self.server_details['use_queryname'] )
        self.jobUserNameCheckBox.toggled.connect(self.updateQueryNameEntry)
        self.advancedSettingsLayout.addWidget(self.jobUserNameCheckBox)

        # Username Entry
        queryNameEntry_l, self.queryNameEntry = CLabelledLineEdit('Job query Username:')
        self.queryNameEntry.setText( self.server_details['queryname'] )
        self.advancedSettingsLayout.addWidget(queryNameEntry_l)
        self.updateQueryNameEntry()

        self.advancedSettingsLayout.addWidget( CHorizontalSeparator())

        # Add a label
        serverCommandsLabel = CLabel("Server Commands")
        self.advancedSettingsLayout.addWidget(serverCommandsLabel)

        # Add the entry to get jobs
        getJobCmdEntry_l, self.getJobCmdEntry = CLabelledLineEdit('Get jobs:')
        self.getJobCmdEntry.setText( self.server_details['get_jobs'] )
        self.advancedSettingsLayout.addWidget(getJobCmdEntry_l)

        # Add the entry to kill jobs
        killJobCmdEntry_l, self.killJobCmdEntry = CLabelledLineEdit('Kill jobs:')
        self.killJobCmdEntry.setText( self.server_details['kill_jobs'] )
        self.advancedSettingsLayout.addWidget(killJobCmdEntry_l)

        # Add the entry for the job ID
        jobIdColEntry_l, self.jobIdColEntry = CLabelledLineEdit('Column for job IDs:')
        self.jobIdColEntry.setText( self.server_details['kill_col'] )
        self.advancedSettingsLayout.addWidget(jobIdColEntry_l)

        # Display the widget
        self.advancedSettingsLayout.setAlignment(qtc.Qt.AlignTop)
        self.advancedSettingsWidget.setLayout(self.advancedSettingsLayout)
        return self.advancedSettingsWidget
        #parentWidget.addWidget(self.advancedSettingsWidget)

    # --------------------------------------
    # Generate the control of the image zoom
    def createUserActions(self, parentWidget):

        # Generate the widget
        self.userActionsWidget = qtw.QWidget()
        self.userActionsLayout = qtw.QHBoxLayout(self.userActionsWidget)

        self.saveButton = qtw.QPushButton("Save")
        self.saveButton.clicked.connect(self.saveServerSettings)
        self.saveButton.setStatusTip("Save the settings.")
        self.saveButton.setFixedWidth(125)
        self.userActionsLayout.addWidget(self.saveButton)

        self.closeButton = qtw.QPushButton("Close")
        self.closeButton.clicked.connect(self.close)
        self.closeButton.setStatusTip("Close the current window.")
        self.closeButton.setFixedWidth(125)
        self.userActionsLayout.addWidget(self.closeButton)

        # Display the widget
        self.userActionsWidget.setLayout(self.userActionsLayout)
        parentWidget.addWidget(self.userActionsWidget)

    ##-\-\-\-\-\-\-\-\-\
    ## UPDATE THE DISPLAY
    ##-/-/-/-/-/-/-/-/-/

    # -----------------------
    # Load the default server
    def defaultServer(self):

        self.server_details = {
        'name': 'Default',
        'address' : "0.0.0.0",
        'port' : "22",
        'username': self.parent.config['USER']['username'],
        'use_key': self.parent.config['USER']['use_key'].capitalize() == 'True',
        'path_key': self.parent.config['USER']['path_key'],
        'read_jobs': True,
        'use_display':False,
        'display_name':'---',
        'use_tunnel': False,
        'tunnel_selection': None,
        'use_queryname': True,
        'queryname': "",
        'get_jobs': self.parent.config['USER']['get_jobs'],
        'kill_jobs': self.parent.config['USER']['kill_jobs'],
        'kill_col': self.parent.config['USER']['kill_col'],
        }

    # ---------------------
    # Load the given server
    def loadServer(self, name):

        # Get the server
        opened_server = [self.parent.config[x] for x in self.parent.config.keys() if x == name][0]

        # UPDATE -------------------
        # --------------------------

        # Check if new settings are missing
        if 'use_display' not in opened_server.keys():
            opened_server['use_display'] = False
            opened_server['display_name'] = '---'

        # --------------------------

        # Prepare the data
        self.server_details = {
        'name': name,
        'address' : opened_server['address'],
        'port' : opened_server['port'],
        'username': opened_server['user'],
        'use_key': opened_server['id_type'] == 'publickey',
        'path_key': opened_server['id_key'],
        'read_jobs': opened_server['read_jobs'] == 'True',
        'use_display': opened_server['use_display'] == 'True',
        'display_name':opened_server['display_name'],
        'use_tunnel': False,
        'tunnel_selection': None,
        'use_queryname': True,
        'queryname': "",
        'get_jobs': opened_server['get_jobs'],
        'kill_jobs': opened_server['kill_jobs'],
        'kill_col': opened_server['kill_col']
        }

        # Check for the tunnel
        if opened_server['tunnel'] != 'None':
            self.server_details['use_tunnel'] = True
            self.server_details['tunnel_selection'] = opened_server['tunnel']

        # Check for the query name
        if opened_server['query_name'] != opened_server['user']:
            self.server_details['use_queryname'] = False
            self.server_details['queryname'] = opened_server['query_name']

    # ---------------------------------------------------------
    # Update the window depending on the type of identification
    def updateIdentificationLabel(self):

        # Select the label and the echo method for the entry
        if self.publicKeyRadiobutton.isChecked():
            text = "Path to Key"
            self.indentificationEntry.setEchoMode(qtw.QLineEdit.Normal)

            if self.server_details['use_key']:
                passphrase = self.server_details['path_key']
            else:
                passphrase = ""

        else:
            text = "Password"
            self.indentificationEntry.setEchoMode(qtw.QLineEdit.Password)

            if self.server_details['use_key']:
                passphrase = ""
            else:
                passphrase = self.server_details['path_key']

        # Set the text of the label
        self.indentificationLabel.setText( text )
        self.indentificationEntry.setText( passphrase )

    # ------------------------------------------
    # Update the status of the display combo box
    def updateDisplayComboBox(self):
        self.customDisplayComboBox.setEnabled( self.useDisplayCheckBox.isChecked() )

    # -----------------------------------------
    # Update the status of the tunnel combo box
    def updateTunnelComboBox(self):
        self.tunnelServerComboBox.setEnabled( self.useTunnelCheckBox.isChecked() )

    # -----------------------------------------
    # Update the status of the query name entry
    def updateQueryNameEntry(self):
        self.queryNameEntry.setEnabled( not self.jobUserNameCheckBox.isChecked() )

    ##-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\
    ## SAVE THE PARAMETERS IN THE CONFIG FILE
    ##-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/

    # ----------------------------------
    # Save the user settings in the file
    def saveServerSettings(self):

        # Get the details
        new_server_details = {
        'name': self.serverNameEntry.text(),
        'address' : self.serverAddressEntry.text(),
        'port' : self.serverPortEntry.text(),
        'username': self.serverUserNameEntry.text(),
        'use_key': self.publicKeyRadiobutton.isChecked(),
        'path_key': self.indentificationEntry.text(),
        'read_jobs': self.readJobsCheckBox.isChecked(),
        'use_display':False,
        'display_name':'---',
        'use_tunnel': False,
        'tunnel_selection': None,
        'queryname': self.serverUserNameEntry.text(),
        'get_jobs': self.getJobCmdEntry.text(),
        'kill_jobs': self.killJobCmdEntry.text(),
        'kill_col': self.jobIdColEntry.text(),
        }

        # Check for the custom display
        if self.useDisplayCheckBox.isChecked() and self.customDisplayComboBox.currentText() != "---":
            new_server_details['use_display'] = True
            new_server_details['display_name'] = self.customDisplayComboBox.currentText()

        # Check for the query name
        if not self.jobUserNameCheckBox.isChecked():
            new_server_details['queryname'] = self.queryNameEntry.text()

        # Check the tunnel
        if self.readJobsCheckBox.isChecked() and self.tunnelServerComboBox.currentText() != "---":
            new_server_details['use_tunnel'] = self.readJobsCheckBox.isChecked()
            new_server_details['tunnel_selection'] = self.tunnelServerComboBox.currentText()

        # Create the server instance
        server_instance = generateServer(new_server_details)

        # Check if the server already exists
        server_exists, previous_address = serverExists(server_instance)
        save_in_file = True
        if server_exists and not self.replace:
            save_in_file = warningMessage("Server in memory", "The selected name is already in the memory under the address "+previous_address+". Are you sure you want to replace this server?")

        # Add the server to the config file
        if save_in_file:
            addServer(server_instance)

            # Refresh the main server list
            self.parent.refreshServerList()

            # Close the window at the end
            self.close()
