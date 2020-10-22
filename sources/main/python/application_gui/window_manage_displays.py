import PyQt5.QtCore as qtc
import PyQt5.QtGui as qtg
import PyQt5.QtWidgets as qtw

from functools import partial

from application_gui.common_gui_functions import CLabel, CHorizontalSeparator, warningMessage, _open_window
from application_gui.window_column_selection import selectColumnsWindow
from application_gui.window_custom_display import selectCustomDisplayWindow

from selection import generateCustomDisplay
from settings import addServer, serverExists, removeDisplay, getDisplayNameTypeList, loadDisplay
from ssh_protocol import generateServer

##-\-\-\-\-\-\-\-\-\-\-\-\
## WINDOW FOR USER SETTINGS
##-/-/-/-/-/-/-/-/-/-/-/-/

class manageDisplayWindow(qtw.QMainWindow):
    def __init__(self, parent):
        super(manageDisplayWindow, self).__init__(parent)

        # Initialise the subwindow
        self.parent = parent

        self.mainWidget = qtw.QWidget()
        self.mainLayout = qtw.QVBoxLayout(self.mainWidget)
        self.setWindowTitle("Manage Custom Displays")

        # Get the list of display
        self.display_list, self.display_types = getDisplayNameTypeList()

        # Populate the panel
        self.createListDisplays(self.mainLayout)
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
        self.parent.subWindows['manage_displays'] = None

    ##-\-\-\-\-\-\-\-\-\-\
    ## GENERATE THE DISPLAY
    ##-/-/-/-/-/-/-/-/-/-/

    # --------------------------------------
    # Generate the server settings selection
    def createListDisplays(self, parentWidget):

        # Generate the widget
        self.displaySettingsWidget = qtw.QWidget()
        self.displaySettingsLayout = qtw.QVBoxLayout(self.displaySettingsWidget)

        # Generate the table of servers
        self.displaysTable = qtw.QTableWidget(0, 4)
        self.displaysTable.setHorizontalHeaderLabels( ['', '', 'Name', 'Type'] )

        self.displaysTable.setSelectionMode(qtw.QAbstractItemView.NoSelection)
        self.displaysTable.setEditTriggers(qtw.QAbstractItemView.NoEditTriggers)

        self.displaysTable.setShowGrid(False)
        self.displaysTable.setMinimumHeight(125)
        self.displaySettingsLayout.addWidget(self.displaysTable)

        # Populate the widget
        self.updateDisplayList()

        # Display the widget
        self.displaySettingsWidget.setLayout(self.displaySettingsLayout)
        parentWidget.addWidget(self.displaySettingsWidget)

    # --------------------------------------
    # Generate the control of the image zoom
    def createUserActions(self, parentWidget):

        # Generate the widget
        self.userActionsWidget = qtw.QWidget()
        self.userActionsLayout = qtw.QHBoxLayout(self.userActionsWidget)

        # Add the new server button
        self.addDisplayButton = qtw.QPushButton("Add Server")
        self.addDisplayButton.clicked.connect(self.addDisplay)
        self.addDisplayButton.setStatusTip("Create a new custom display.")
        self.addDisplayButton.setFixedWidth(125)
        self.userActionsLayout.addWidget(self.addDisplayButton, alignment=qtc.Qt.AlignLeft)

        if not self.parent.active_server:
            self.addDisplayButton.setEnabled(False)

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
    def updateDisplayList(self):

        # Delete the values
        rowCount = self.displaysTable.rowCount()
        if rowCount > 0:
            for i in range(rowCount):
                self.displaysTable.removeRow(0)

        # Fill the table
        if len(self.display_list) > 0:
            for i, name in enumerate(self.display_list):

                # Fill the rows
                self.displaysTable.insertRow(i)

                # Prepare the edit button
                serverEditButton = qtw.QPushButton("Edit")
                serverEditButton.clicked.connect(partial(self.editDisplay, id=i))
                serverEditButton.setFixedWidth(75)

                if not self.parent.active_server:
                    serverEditButton.setEnabled(False)

                # Prepare the edit button
                serverDeleteButton = qtw.QPushButton("Delete")
                serverDeleteButton.clicked.connect(partial(self.deleteDisplay, name=name))
                serverDeleteButton.setFixedWidth(75)

                # Fill the columns
                self.displaysTable.setCellWidget(i, 0, serverEditButton)
                self.displaysTable.setCellWidget(i, 1, serverDeleteButton)
                self.displaysTable.setItem(i, 2, qtw.QTableWidgetItem(str(name)))
                self.displaysTable.setItem(i, 3, qtw.QTableWidgetItem(str(self.display_types[i])))

        # Resize the columns
        header = self.displaysTable.horizontalHeader()
        for i in range( 4 ):
            header.setSectionResizeMode(i, qtw.QHeaderView.ResizeToContents)

    ##-\-\-\-\-\-\-\-\-\
    ## MANAGE THE SERVERS
    ##-/-/-/-/-/-/-/-/-/

    # ---------------------------------------------
    # Close the window and edit the selected server
    def addDisplay(self):

        # Select the current tab and retrieve the job list
        _current_tab_id = self.parent.serverTabDisplay.currentIndex()
        column_names = self.parent.serverTabDisplay.displayedTabs[ _current_tab_id ].jobs.columns

        # Open the new selection option
        _open_window(self.parent, selectColumnsWindow, 'column_selection', column_names=column_names)

        # Close the current window
        self.close()

    # ---------------------------------------------
    # Close the window and edit the selected server
    def editDisplay(self, id=0):

        # Get the current display
        name = self.display_list[id]
        current_type = self.display_types[id]

        # Get the current tab
        _current_tab_id = self.parent.serverTabDisplay.currentIndex()
        current_tab = self.parent.serverTabDisplay.displayedTabs[ _current_tab_id ]
        job_content = current_tab.jobs.loc[0]
        column_names = current_tab.jobs.columns

        # Load the current selection
        display_dict = loadDisplay(name)
        selected_display = generateCustomDisplay(display_dict)

        # Load a column selection
        if current_type == 'column':
            _open_window(self.parent, selectColumnsWindow, 'column_selection', column_names=column_names, loaded_display=selected_display)

        else:
            _open_window(self.parent, selectCustomDisplayWindow, 'custom_display', column_names=column_names, example_job=job_content, loaded_display=selected_display)

        # Close the current window
        self.close()

    # ---------------------------
    # Delete the selected display
    def deleteDisplay(self, name=None):

        # Display a warning message before proceeding
        if warningMessage('Delete Display','Are you sure you want to delete this custom display from the memory?'):

            # Delete from the file
            removeDisplay(name)

            # Get the list of display
            self.display_list, self.display_types = getDisplayNameTypeList()

            # Refresh the display
            self.updateDisplayList()

            # Refresh the main display
            self.parent.serverTabDisplay.updateCustomSelections()
