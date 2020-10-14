import PyQt5.QtCore as qtc
import PyQt5.QtGui as qtg
import PyQt5.QtWidgets as qtw

from application_gui.app_styles import applyStyle
from application_gui.common_gui_functions import _open_window, CLabel, choice2Message, errorMessage
from application_gui.display_tab import mainTabWidget
from application_gui.menubar import menuBar
from application_gui.window_progressbar import progressBarWindow
from application_gui.window_user import userSettingsWindow
from application_gui.window_server_settings import serverSettingsWindow

from settings import checkFirstUse, loadConfig, loadServer
from ssh_protocol import openServer, checkConnection

##-\-\-\-\-\-\-\-\-\-\-\-\
## MAIN GUI OF THE SOFTWARE
##-/-/-/-/-/-/-/-/-/-/-/-/

class mainGUI(qtw.QMainWindow):
    def __init__(self, application_context):
        super(mainGUI, self).__init__()

        # Initialize the properties of the software Main GUI
        self.appctxt = application_context
        self.application = application_context.app
        self.title = "H-PyMon"
        self.version = "beta" #"v1.0.0"
        self.subWindows = {}
        self.servers = []
        self.active_server = False

        # Retrieve the configuration
        if checkFirstUse():
            self.config = loadConfig()
            _open_window(self, userSettingsWindow, 'user_settings')
        else:
            self.config = loadConfig()
        self.refreshServerList()

        # Generate the display
        self.setWindowTitle(self.title + " (" + self.version + ")")
        self.menuBar = menuBar(self)

        # Populate the window
        self.genCentralWidget()

        # Apply the style and display the window
        self.statusBar()
        if self.config['USER']['dark_theme'].capitalize() == 'True':
            applyStyle( self.application )
        self.show()
        self.setFixedSize(850,450)

    # --------------------------
    # Initialise the main widget
    def genCentralWidget(self):

        # Define the widget
        self.mainWidget = qtw.QWidget()
        self.mainLayout = qtw.QVBoxLayout(self.mainWidget)

        # Add the tab widget
        self.defaultWidget(self.mainLayout)

        # Add the button widget
        self.genButtonWidget(self.mainLayout)

        # Display the widget
        self.mainWidget.setLayout(self.mainLayout)
        self.setCentralWidget(self.mainWidget)

    # -----------------------------
    # Put a blank widget on opening
    def defaultWidget(self, parentWidget):

        # Display the widget
        self.serverTabDisplay = mainTabWidget(self.mainWidget, self)

        # Add a blank table
        self.serverTabDisplay.blankTab()

        # Add the tab display to the layout
        parentWidget.addWidget( self.serverTabDisplay )

    # ----------------------------
    # Initialise the button widget
    def genButtonWidget(self, parentWidget, add_refresh=False):

        # Generate the widget
        self.buttonsWidget = qtw.QWidget()
        self.buttonsLayout = qtw.QHBoxLayout(self.buttonsWidget)

        # Refresh button
        if add_refresh:
            self.actionButton = qtw.QPushButton("Refresh")
            self.actionButton.clicked.connect(self.retrieveJobList)
        else:
            self.actionButton = qtw.QPushButton("Connect")
            self.actionButton.clicked.connect(self.connectAllServers)
        self.actionButton.setFixedWidth(125)
        self.buttonsLayout.addWidget(self.actionButton, alignment=qtc.Qt.AlignLeft)

        # Exit button
        self.exitButton = qtw.QPushButton("Exit")
        self.exitButton.setFixedWidth(125)
        self.exitButton.clicked.connect(qtw.qApp.quit)
        self.buttonsLayout.addWidget(self.exitButton, alignment=qtc.Qt.AlignRight)

        # Display the widget
        self.buttonsWidget.setLayout(self.buttonsLayout)
        parentWidget.addWidget(self.buttonsWidget)

    ##-\-\-\-\-\-\-\-\
    ## SERVER HANDLING
    ##-/-/-/-/-/-/-/-/

    # ------------------------------------
    # Connect to the specific given server
    def connectSingleServer(self, name=None):

        # Check if the server is already open
        all_names = [x.name for x in self.servers]
        if name in all_names:
            errorMessage('Server already open',"The selected server ("+str(name)+") has already been opened.")
            return 0

        # Get the number of servers in the memory
        n_servers = len(self.server_jobs)
        if n_servers == 0:
            errorMessage('No Server',"No Server have been defined in the memory of H-PyMon. Please add servers.")
            return 0

        # Get the server
        opened_server = openServer(name, use_name=True)

        # Check if the connection is working
        if not checkConnection(opened_server):

            # Check what to do next
            userChoice = choice2Message("No Connection", "H-PyMon cannot connect to the selected server ("+str(name)+"). Please check the settings or retry.", "Edit", icon=qtw.QMessageBox.Critical)

            # Edit the server
            if userChoice:
                _open_window(self, serverSettingsWindow, 'server_settings', opened_server=name, replace=True)

        # Load the server
        else:

            # Add the server to the list
            self.servers.append( OpenedServer(opened_server) )

            # Reset the GUI if needed
            if len(self.servers) == 1:

                # Set the variable
                self.active_server = True

                # Reset the background
                self.mainWidget.deleteLater()
                self.mainWidget = qtw.QWidget()
                self.mainLayout = qtw.QVBoxLayout(self.mainWidget)

                # Display the widget
                self.serverTabDisplay = mainTabWidget(self.mainWidget, self)
                self.mainLayout.addWidget( self.serverTabDisplay )
                self.setCentralWidget(self.mainWidget)

                # Add the button widget
                self.genButtonWidget(self.mainLayout, add_refresh=True)

                # Load the newbackground
                self.mainWidget.setLayout(self.mainLayout)
                self.setCentralWidget(self.mainWidget)

            # Add the tab to the display
            self.serverTabDisplay.newTab(opened_server)

    # ----------------------------------------
    # Connect to all the servers in the memory
    def connectAllServers(self):

        # Check the list of opened servers
        all_names = [x.name for x in self.servers]

        # Get the number of servers in the memory
        n_servers = str(len(self.server_jobs))
        if n_servers == "0":
            errorMessage('No Server',"No Server have been defined in the memory of H-PyMon. Please add servers.")
            return 0

        # Open the progress bar window
        _open_window(self, progressBarWindow, 'progress_bar', title='Connection...', text='Opening Server 1/'+n_servers)
        self.application.processEvents()

        # Open all the servers if not already open
        for i, (job_address, job_name) in enumerate(self.server_jobs):

            # Load the server
            if job_name not in all_names:
                self.connectSingleServer(name=job_name)

            # Update the progress bar window
            self.subWindows['progress_bar'].updateProgress('Opening Server '+str(i+1)+'/'+n_servers, (i+1)*100/int(n_servers))
            self.application.processEvents()

    # -------------------------------
    # Refresh the job list in the tab
    def retrieveJobList(self):

        # Get the current tab ID
        tabIndex = self.serverTabDisplay.currentIndex()

        # Refresh the job list in memory
        self.serverTabDisplay.displayedTabs[tabIndex].refreshJobList()

        # Refresh the tab display
        self.serverTabDisplay.displayedTabs[tabIndex].jobInTable()

    # -----------------------
    # Refresh the server list
    def refreshServerList(self):

        # Reload the config from the file
        self.config = loadConfig()

        # Reload the server list
        self.server_list = [(self.config[x]['address'], x) for x in self.config.keys() if x != 'USER']

        # Reload the server list for jobs
        self.server_jobs = []
        for server in self.config.keys():
            if server != 'USER':
                if self.config[server]['read_jobs'] == 'True':
                    self.server_jobs.append( (self.config[server]['address'], server) )

##-\-\-\-\-\-\-\-\-\-\
## OPENED SERVER CLASS
##-/-/-/-/-/-/-/-/-/-/

class OpenedServer:
    def __init__(self, server_class):

        # General information on the server
        self.name = server_class.name
        self.address = server_class.ip
        self.server = server_class
