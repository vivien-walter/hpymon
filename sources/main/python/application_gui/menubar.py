import PyQt5.QtGui as qtg
import PyQt5.QtWidgets as qtw

from application_gui.common_gui_functions import _open_window
from application_gui.window_about import aboutHelpWindow
from application_gui.window_column_selection import selectColumnsWindow
from application_gui.window_connect_servers import connectServersWindow
from application_gui.window_custom_display import selectCustomDisplayWindow
from application_gui.window_user import userSettingsWindow
from application_gui.window_manage_displays import manageDisplayWindow
from application_gui.window_manage_servers import manageServerWindow
from application_gui.window_server_settings import serverSettingsWindow

##-\-\-\-\-\-\-\-\-\-\-\-\
## MENUBAR OF THE MAIN GUI
##-/-/-/-/-/-/-/-/-/-/-/-/

class menuBar:
    def __init__(self, parent):

        # Initialise the menu bar
        self.parent = parent
        self.mainMenu = self.parent.menuBar()
        self.mainMenu.setNativeMenuBar(True)

        # Call the different submenus
        self.createServerMenu()
        self.createDisplayMenu()
        self.createHelpMenu()

    ##-\-\-\-\-\-\-\-\-\-\
    ## INTERFACE GENERATION
    ##-/-/-/-/-/-/-/-/-/-/

    # ---------------------------
    # Generate the SERVER submenu
    def createServerMenu(self):

        # Initialise
        self.serverMenu = self.mainMenu.addMenu("Servers")

        # Open a file submenu
        self.serverMenu.connectSubMenu = qtw.QMenu('Connect to...', self.parent)

        # Load all servers
        self.serverMenu.connectAllButton = qtw.QAction("All", self.parent)
        self.serverMenu.connectAllButton.setShortcut("Ctrl+O")
        self.serverMenu.connectAllButton.setStatusTip("Load from all servers in memory.")
        self.serverMenu.connectAllButton.triggered.connect(self.connectAllServers)
        self.serverMenu.connectSubMenu.addAction(self.serverMenu.connectAllButton)

        # Open server selection
        self.serverMenu.selectServerButton = qtw.QAction("Select", self.parent)
        self.serverMenu.selectServerButton.setShortcut("Ctrl+Shift+O")
        self.serverMenu.selectServerButton.setStatusTip("Select the server to connect to.")
        self.serverMenu.selectServerButton.triggered.connect(self.callConnectServersWindow)
        self.serverMenu.connectSubMenu.addAction(self.serverMenu.selectServerButton)

        self.serverMenu.addMenu(self.serverMenu.connectSubMenu)

        self.serverMenu.addSeparator()

        # Add new server
        self.serverMenu.newServerButton = qtw.QAction("Add Server", self.parent)
        self.serverMenu.newServerButton.setShortcut("Ctrl+N")
        self.serverMenu.newServerButton.setStatusTip("Add a new server in the memory.")
        self.serverMenu.newServerButton.triggered.connect(self.callServerSettingsWindow)
        self.serverMenu.addAction(self.serverMenu.newServerButton)

        # Manage the existing servers
        self.serverMenu.manageServerButton = qtw.QAction("Manage Servers", self.parent)
        self.serverMenu.manageServerButton.setStatusTip("Manage the servers saved in the memory.")
        self.serverMenu.manageServerButton.triggered.connect(self.callServerManagementWindow)
        self.serverMenu.addAction(self.serverMenu.manageServerButton)

        self.serverMenu.addSeparator()

        # Quit the software
        self.serverMenu.closeButton = qtw.QAction("Quit H-PyMon", self.parent)
        self.serverMenu.closeButton.setShortcut("Ctrl+Q")
        self.serverMenu.closeButton.setStatusTip("Close the software.")
        self.serverMenu.closeButton.triggered.connect(self.parent.close)
        self.serverMenu.addAction(self.serverMenu.closeButton)

    # ---------------------------
    # Generate the DISPLAY submenu
    def createDisplayMenu(self):

        # Initialise
        self.displayMenu = self.mainMenu.addMenu("Job Display")

        # Add new column selection
        self.displayMenu.newDisplayButton = qtw.QAction("New Column Selection", self.parent)
        self.displayMenu.newDisplayButton.setStatusTip("Create a new custom column selection for the jobs.")
        self.displayMenu.newDisplayButton.triggered.connect(self.callNewColumnDisplayWindow)
        self.displayMenu.addAction(self.displayMenu.newDisplayButton)

        # Add new custom display
        self.displayMenu.newDisplayButton = qtw.QAction("New Custom Display", self.parent)
        self.displayMenu.newDisplayButton.setStatusTip("Create a new custom display for the jobs.")
        self.displayMenu.newDisplayButton.triggered.connect(self.callNewCustomDisplayWindow)
        self.displayMenu.addAction(self.displayMenu.newDisplayButton)

        self.displayMenu.addSeparator()

        # Manage the existing servers
        self.displayMenu.manageDisplayButton = qtw.QAction("Manage Custom Displays", self.parent)
        self.displayMenu.manageDisplayButton.setStatusTip("Manage the custom display settings saved in the memory.")
        self.displayMenu.manageDisplayButton.triggered.connect(self.callDisplayManagementWindow)
        self.displayMenu.addAction(self.displayMenu.manageDisplayButton)

    # -------------------------
    # Generate the HELP submenu
    def createHelpMenu(self):

        # Initialise
        self.helpMenu = self.mainMenu.addMenu("Help")

        # Open the user settings
        self.helpMenu.userSettingsButton = qtw.QAction("User Settings", self.parent)
        self.helpMenu.userSettingsButton.setStatusTip("Edit the default user settings.")
        self.helpMenu.userSettingsButton.triggered.connect(self.callUserSettingsWindow)
        self.helpMenu.addAction(self.helpMenu.userSettingsButton)

        self.helpMenu.addSeparator()

        # Open the About menu
        self.helpMenu.aboutButton = qtw.QAction("About...", self.parent)
        self.helpMenu.aboutButton.setStatusTip("General informations on the software.")
        self.helpMenu.aboutButton.triggered.connect(self.callAboutInfos)
        self.helpMenu.addAction(self.helpMenu.aboutButton)

    ##-\-\-\-\-\-\-\-\-\-\-\
    ## INTERFACE INTERACTION
    ##-/-/-/-/-/-/-/-/-/-/-/

    # ----------------------------------
    # Display the server settings window
    def connectAllServers(self):
        self.parent.connectAllServers()

    # ----------------------------------
    # Display the server settings window
    def callConnectServersWindow(self):
        _open_window(self.parent, connectServersWindow, 'connect_servers')

    # ----------------------------------
    # Display the server settings window
    def callServerSettingsWindow(self):
        _open_window(self.parent, serverSettingsWindow, 'server_settings')

    # ------------------------------------
    # Display the server management window
    def callServerManagementWindow(self):
        _open_window(self.parent, manageServerWindow, 'manage_servers')

    # -------------------------------------
    # Display the display management window
    def callNewColumnDisplayWindow(self):

        # Only process if an active die is displayed
        if self.parent.active_server:

            # Select the current tab and retrieve the job list
            _current_tab_id = self.parent.serverTabDisplay.currentIndex()
            column_names = self.parent.serverTabDisplay.displayedTabs[ _current_tab_id ].jobs.columns

            # Open the new selection option
            _open_window(self.parent, selectColumnsWindow, 'column_selection', column_names=column_names)

    # -------------------------------------
    # Display the display management window
    def callNewCustomDisplayWindow(self):

        # Only process if an active die is displayed
        if self.parent.active_server:

            # Select the current tab and retrieve the job list
            _current_tab_id = self.parent.serverTabDisplay.currentIndex()
            job_content = self.parent.serverTabDisplay.displayedTabs[ _current_tab_id ].jobs.loc[0]
            column_names = self.parent.serverTabDisplay.displayedTabs[ _current_tab_id ].jobs.columns

            # Open the new selection option
            _open_window(self.parent, selectCustomDisplayWindow, 'custom_display', column_names=column_names, example_job=job_content)

    # -------------------------------------
    # Display the display management window
    def callDisplayManagementWindow(self):
        _open_window(self.parent, manageDisplayWindow, 'manage_displays')

    # --------------------------------
    # Display the user settings window
    def callUserSettingsWindow(self):
        _open_window(self.parent, userSettingsWindow, 'user_settings')

    # --------------------------------
    # Display the user settings window
    def callAboutInfos(self):
        _open_window(self.parent, aboutHelpWindow, 'about')
