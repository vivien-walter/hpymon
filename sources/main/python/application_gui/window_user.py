import PyQt5.QtCore as qtc
import PyQt5.QtGui as qtg
import PyQt5.QtWidgets as qtw

from application_gui.common_gui_functions import CLabel, CLabelledLineEdit, warningMessage, CHorizontalSeparator

from settings import editUser

##-\-\-\-\-\-\-\-\-\-\-\-\
## WINDOW FOR USER SETTINGS
##-/-/-/-/-/-/-/-/-/-/-/-/

class userSettingsWindow(qtw.QMainWindow):
    def __init__(self, parent):
        super(userSettingsWindow, self).__init__(parent)

        # Initialise the subwindow
        self.parent = parent
        self.setWindowModality(qtc.Qt.ApplicationModal)

        self.mainWidget = qtw.QWidget()
        self.mainLayout = qtw.QVBoxLayout(self.mainWidget)
        self.setWindowTitle("User Settings")

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
        self.parent.subWindows['user_settings'] = None

    ##-\-\-\-\-\-\-\-\-\-\
    ## GENERATE THE DISPLAY
    ##-/-/-/-/-/-/-/-/-/-/

    # -----------------------------------
    # Generate the tab widget for display
    def createTabDisplay(self, parentWidget):

        # Define the widget
        self.tabWidget = qtw.QTabWidget()

        # Add the basic user settings tab
        self.tabWidget.addTab(self.createUserSettings(), "Settings")

        # Add the advanced user settings tab
        self.tabWidget.addTab(self.createAdvancedSettings(), "Advanced")

        # Load the widget
        parentWidget.addWidget(self.tabWidget)

    # ------------------------------------
    # Generate the user settings selection
    def createUserSettings(self):

        # Generate the widget
        self.userSettingsWidget = qtw.QWidget()
        self.userSettingsLayout = qtw.QVBoxLayout(self.userSettingsWidget)

        # Add the name entry
        userNameEntry_l, self.userNameEntry = CLabelledLineEdit('User Name')
        self.userNameEntry.setText( self.parent.config['USER']['username'] )
        self.userSettingsLayout.addWidget(userNameEntry_l)

        self.userSettingsLayout.addWidget(CHorizontalSeparator())

        # Add public key checkbox
        self.useKeyCheckBox = qtw.QCheckBox("Use public key?")
        self.useKeyCheckBox.setChecked( self.parent.config['USER']['use_key'].capitalize() == 'True' )
        self.userSettingsLayout.addWidget(self.useKeyCheckBox)

        # Add the path to public key entry
        publicKeyEntry_l, self.publicKeyEntry = CLabelledLineEdit('Path to key')
        self.publicKeyEntry.setText( self.parent.config['USER']['path_key'] )
        self.userSettingsLayout.addWidget(publicKeyEntry_l)

        self.userSettingsLayout.addWidget(CHorizontalSeparator())

        # Add dark theme checkbox
        self.darkThemeCheckBox = qtw.QCheckBox("Use dark theme?")
        self.darkThemeCheckBox.setChecked( self.parent.config['USER']['dark_theme'].capitalize() == 'True' )
        self.userSettingsLayout.addWidget(self.darkThemeCheckBox)

        self.userSettingsLayout.addWidget(CHorizontalSeparator())

        # Add public key checkbox
        self.autoConnectCheckBox = qtw.QCheckBox("Auto-connect on start?")
        self.autoConnectCheckBox.setChecked( self.parent.config['USER']['autostart'].capitalize() == 'True' )
        self.userSettingsLayout.addWidget(self.autoConnectCheckBox)

        # Display the widget
        self.userSettingsLayout.setAlignment(qtc.Qt.AlignTop)
        self.userSettingsWidget.setLayout(self.userSettingsLayout)
        return self.userSettingsWidget
        #parentWidget.addWidget(self.userSettingsWidget)

    # ----------------------------------------
    # Generate the advanced settings selection
    def createAdvancedSettings(self):

        # Generate the widget
        self.advancedSettingsWidget = qtw.QWidget()
        self.advancedSettingsLayout = qtw.QVBoxLayout(self.advancedSettingsWidget)

        # Add a label
        autoRefreshLabel = CLabel("Auto-Refresh")
        self.advancedSettingsLayout.addWidget(autoRefreshLabel)

        # Add public key checkbox
        self.autoRefreshCheckBox = qtw.QCheckBox("Enable Auto-Refresh?")
        self.autoRefreshCheckBox.setChecked( self.parent.config['USER']['autorefresh'].capitalize() == 'True' )
        self.advancedSettingsLayout.addWidget(self.autoRefreshCheckBox)

        # Add the entry to get jobs
        getRefreshTimeEntry_l, self.getRefreshTimeEntry = CLabelledLineEdit('Time between refresh (min):')
        self.getRefreshTimeEntry.setText( self.parent.config['USER']['refresh_time'] )
        self.advancedSettingsLayout.addWidget(getRefreshTimeEntry_l)

        self.advancedSettingsLayout.addWidget(CHorizontalSeparator())

        # Add a label
        serverCommandsLabel = CLabel("Server Commands")
        self.advancedSettingsLayout.addWidget(serverCommandsLabel)

        # Add the entry to get jobs
        getJobCmdEntry_l, self.getJobCmdEntry = CLabelledLineEdit('Get jobs:')
        self.getJobCmdEntry.setText( self.parent.config['USER']['get_jobs'] )
        self.advancedSettingsLayout.addWidget(getJobCmdEntry_l)

        # Add the entry to kill jobs
        killJobCmdEntry_l, self.killJobCmdEntry = CLabelledLineEdit('Kill jobs:')
        self.killJobCmdEntry.setText( self.parent.config['USER']['kill_jobs'] )
        self.advancedSettingsLayout.addWidget(killJobCmdEntry_l)

        # Add the entry for the job ID
        jobIdColEntry_l, self.jobIdColEntry = CLabelledLineEdit('Column for job IDs:')
        self.jobIdColEntry.setText( self.parent.config['USER']['kill_col'] )
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

        # Auto contrast and histogram crop
        self.saveButton = qtw.QPushButton("Save")
        self.saveButton.clicked.connect(self.saveUserSettings)
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

    ##-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\
    ## SAVE THE PARAMETERS IN THE CONFIG FILE
    ##-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/

    # ----------------------------------
    # Save the user settings in the file
    def saveUserSettings(self):

        # Raise warning if the theme as been changed
        old_theme = self.parent.config['USER']['dark_theme'].capitalize() == 'True'
        if self.darkThemeCheckBox.isChecked() != old_theme:
            warningMessage("Theme Changed","Please restart the software to apply the new theme.", add_ok=False)

        # Collect the user input
        self.parent.config['USER']['username'] = self.userNameEntry.text()
        self.parent.config['USER']['use_key'] = str(self.useKeyCheckBox.isChecked())
        self.parent.config['USER']['path_key'] = self.publicKeyEntry.text()
        self.parent.config['USER']['dark_theme'] = str(self.darkThemeCheckBox.isChecked())
        self.parent.config['USER']['autostart'] = str(self.autoConnectCheckBox.isChecked())
        self.parent.config['USER']['autorefresh'] = str(self.autoRefreshCheckBox.isChecked())
        self.parent.config['USER']['refresh_time'] = str(self.getRefreshTimeEntry.text())
        self.parent.config['USER']['get_jobs'] = self.getJobCmdEntry.text()
        self.parent.config['USER']['kill_jobs'] = self.killJobCmdEntry.text()

        # Save in the file
        editUser(self.parent.config['USER'])

        # Start auto refresh
        if self.autoRefreshCheckBox.isChecked() and self.parent.active_server:
            self.parent.periodicRefresh()

        # Close the window at the end
        self.close()
