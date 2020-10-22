import PyQt5.QtCore as qtc
import PyQt5.QtGui as qtg
import PyQt5.QtWidgets as qtw

from application_gui.common_gui_functions import _open_window, errorMessage, warningMessage
from application_gui.window_column_selection import selectColumnsWindow
from application_gui.window_custom_display import selectCustomDisplayWindow

from get_jobs import getJobList, killJobs
from settings import getDisplayList, loadDisplay
from selection import generateCustomDisplay

##-\-\-\-\-\-\-\-\-\-\-\-\-\-\
## TAB DISPLAY FOR THE MAIN GUI
##-/-/-/-/-/-/-/-/-/-/-/-/-/-/

class mainTabWidget(qtw.QTabWidget):
    def __init__(self, application, parent):
        super(mainTabWidget, self).__init__()

        # Initialise the parameters
        self.application = application
        self.parent = parent

        # Initialise the tab display
        self.displayedTabs = []

    # ------------------------------
    # Add a blank tab to the display
    def blankTab(self):

        # Append the tab to the list
        self.displayedTabs.append( serverTab(self.parent, None) )

        # Append the tab to the widget
        self.addTab( self.displayedTabs[-1].tabWidget, "" )
        self.setCurrentIndex( self.count() - 1 )

    # ------------------------
    # Add a tab to the display
    def newTab(self, server_class):

        # Append the tab to the list
        self.displayedTabs.append( serverTab(self.parent,server_class) )

        # Append the tab to the widget
        self.addTab( self.displayedTabs[-1].tabWidget, server_class.name )
        self.setCurrentIndex( self.count() - 1 )

    ##-\-\-\-\-\-\-\-\-\
    ## UPDATE THE DISPLAY
    ##-/-/-/-/-/-/-/-/-/

    # ----------------------------------------
    # Update the custom selection in all items
    def updateCustomSelections(self):

        # Get the list of selections
        custom_displays = getDisplayList()

        # Loop through all the tabs
        for tab in self.displayedTabs:

            # Save the current selection of the combo box
            current_selection = tab.customDisplayComboBox.currentText()

            # Reset the tab memory
            tab.custom_displays = custom_displays

            # Reset the combobox
            tab.customDisplayComboBox.clear()

            # Populate the combobox
            tab.customDisplayComboBox.addItem("---")
            for display_name in custom_displays:
                tab.customDisplayComboBox.addItem(display_name)

            # Put the selection back
            if current_selection in custom_displays:
                index = tab.customDisplayComboBox.findText(current_selection, qtc.Qt.MatchFixedString)
                if index >= 0:
                     tab.customDisplayComboBox.setCurrentIndex(index)

##-\-\-\-\-\-\
## TAB CONTENT
##-/-/-/-/-/-/

class serverTab:
    def __init__(self, parent, server):

        # Keep the server in memory
        self.parent = parent
        self.server = server

        self.loaded_display= None

        if self.server is not None:
            self.refreshJobList()

            # Load the list of custom displays
            self.refreshDisplayList()
        else:
            self.selected_columns = []
            self.custom_displays = []

        # Initialise the widget
        self.tabWidget = qtw.QWidget()
        self.tabLayout = qtw.QVBoxLayout(self.tabWidget)

        # Add the custom display options
        self.createCustomDisplayWidget(self.tabLayout)
        self.createTableWidget(self.tabLayout)

        if self.server is not None:
            self.selectDisplayType()

        # Load the layout
        self.tabWidget.setLayout(self.tabLayout)

    # ----------------------------
    # Add the checkbox for display
    def createCustomDisplayWidget(self, parentWidget):

        # Initialise the widget
        self.customDisplayWidget = qtw.QWidget()
        self.customDisplayLayout = qtw.QHBoxLayout(self.customDisplayWidget)

        # Checkbox to use the custom display
        self.customDisplayCheckBox = qtw.QCheckBox("Use custom display?")

        if self.server is None:
            self.customDisplayCheckBox.setEnabled(False)
        else:
            self.customDisplayCheckBox.setChecked( self.server.use_display )

        self.customDisplayCheckBox.toggled.connect(self.selectDisplayType)
        self.customDisplayLayout.addWidget(self.customDisplayCheckBox)

        # Combobox to use the custom display
        self.customDisplayComboBox = qtw.QComboBox()
        self.customDisplayComboBox.addItem("---")
        for display_name in self.custom_displays:
            self.customDisplayComboBox.addItem(display_name)

        if self.server is None:
            self.customDisplayComboBox.setEnabled(False)
        else:
            if self.server.use_display:
                _col_ID = self.customDisplayComboBox.findText(self.server.display_name, qtc.Qt.MatchFixedString)
                self.customDisplayComboBox.setCurrentIndex(_col_ID)

        self.customDisplayComboBox.currentTextChanged.connect(self.selectDisplayType)
        self.customDisplayLayout.addWidget(self.customDisplayComboBox)

        # Display the widget
        self.customDisplayWidget.setLayout(self.customDisplayLayout)
        parentWidget.addWidget(self.customDisplayWidget)

    # ----------------------------
    # Add the checkbox for display
    def createTableWidget(self, parentWidget):

        # Initialise the widget
        self.tableWidget = qtw.QWidget()
        self.tableLayout = qtw.QVBoxLayout(self.tableWidget)

        # Generate the table
        if self.server is not None:
            self.selected_columns = self.jobs.columns
        self.generateTable(custom_display=False)

        # Display the widget
        self.tableWidget.setLayout(self.tableLayout)
        parentWidget.addWidget(self.tableWidget)

    ##-\-\-\-\-\-\-\-\-\
    ## UPDATE THE DISPLAY
    ##-/-/-/-/-/-/-/-/-/

    # -------------------------------
    # Refresh the custom display list
    def refreshDisplayList(self):
        self.custom_displays = getDisplayList()

    # -----------------------------------------
    # Select the type of display for the window
    def selectDisplayType(self):

        # Get the selection
        use_custom = self.customDisplayCheckBox.isChecked()
        custom_selection = self.customDisplayComboBox.currentText()

        # Remove the previous widget
        self.jobsTable.deleteLater()

        # Retrieve and apply the custom display
        if use_custom and custom_selection != "---" and custom_selection != "":

            # Retrieve the custom display instance
            _display_details = loadDisplay(custom_selection)
            self.loaded_display = generateCustomDisplay(_display_details)

            # Process a column selection
            if self.loaded_display.display_type == 'column':

                # Get the name of the column to display
                self.selected_columns = self.loaded_display.columns

                # Load the table content
                self.generateTable(custom_display=False)

            # Process a custom selection
            elif 'selection' in self.loaded_display.display_type:

                # Make the job selection
                if len(self.loaded_display.selection.sorting['columns']) != 0:
                    self.selected_jobs = self.loaded_display.selection.sortJobs(self.jobs)
                else:
                    self.selected_jobs = self.loaded_display.selection.selectJobs(self.jobs)

                # Use a column selection
                if self.loaded_display.display_type == 'selection_column':
                    self.selected_columns = self.loaded_display.columns

                # Use the full names
                else:
                    self.selected_columns = self.jobs.columns

                # Load the table content
                self.generateTable(custom_display=True)

        # Use the basic display
        else:
            self.selected_columns = self.jobs.columns
            self.generateTable(custom_display=False)

    # --------------------
    # Refresh the job list
    def refreshJobList(self):
        self.jobs = getJobList(self.server, command=self.server.get_jobs, username=self.server.queryname)

    # ----------------------
    # Generate the job table
    def generateTable(self, custom_display=False):

        # Table for the results
        self.jobsTable = qtw.QTableWidget(0, len( self.selected_columns ))
        self.jobsTable.setHorizontalHeaderLabels( self.selected_columns )
        self.jobsTable.setSelectionBehavior(qtw.QAbstractItemView.SelectRows)
        self.jobsTable.setEditTriggers(qtw.QAbstractItemView.NoEditTriggers)

        if self.server is not None:
            self.jobsTable.setContextMenuPolicy(qtc.Qt.CustomContextMenu)
            self.jobsTable.customContextMenuRequested.connect(self.makeMenuEvent)

        self.jobsTable.setMinimumHeight(175)
        self.tableLayout.addWidget(self.jobsTable)

        # Populate the table
        if self.server is not None:
            self.jobInTable(custom_display=custom_display)

        # Resize the columns
        header = self.jobsTable.horizontalHeader()
        for i in range(len( self.selected_columns )):
            header.setSectionResizeMode(i, qtw.QHeaderView.ResizeToContents)

    # -------------------------
    # Add the jobs to the table
    def jobInTable(self, custom_display=False):

        # Delete the values
        rowCount = self.jobsTable.rowCount()
        if rowCount > 0:
            for i in range(rowCount):
                self.jobsTable.removeRow(0)

        # Custom display
        if custom_display:
            self.addCustomTableContent(self.selected_jobs, current_id=0)

        # Normal display
        else:

            # Fill the table
            if len(self.jobs) > 0:
                for i, row in self.jobs.iterrows():

                    # Fill the rows
                    self.jobsTable.insertRow(i)

                    # Fill the columns
                    j = 0
                    for data, column_name in zip(row, row.index):
                        if column_name in self.selected_columns:
                            item = qtw.QTableWidgetItem(str(data))
                            self.jobsTable.setItem(i, j, item)
                            j += 1

    # ------------------------------
    # Add a custom selection of jobs
    def addCustomTableContent(self, job_list, pre_symbol='', current_id=0, name_id=0):

        # Process a dictionary
        if isinstance(job_list, dict):

            # Set the font
            boldFont = qtg.QFont()
            boldFont.setBold(True)

            # Process all sections
            for section_name in job_list.keys():

                # Fill the rows
                self.jobsTable.insertRow(current_id)

                # Add the header
                section_type = self.loaded_display.selection.sorting['names'][name_id]
                headerText = pre_symbol + ' ' + section_type + ': ' + section_name.capitalize()
                item = qtw.QTableWidgetItem(headerText)
                self.jobsTable.setSpan(current_id, 0, 1, len( self.selected_columns ))
                self.jobsTable.setItem(current_id, 0, item)
                self.jobsTable.item(current_id,0).setFont(boldFont)

                # Color the background of the cell
                if self.parent.config['USER']['dark_theme'] == 'True':
                    bcg_color = qtg.QColor(100,130,147)
                else:
                    bcg_color = qtg.QColor(245,245,245)

                self.jobsTable.item(current_id,0).setBackground(bcg_color)

                current_id += 1

                # Process the content of the dictionary element
                current_id = self.addCustomTableContent(job_list[section_name], pre_symbol=pre_symbol+'>', current_id=current_id, name_id=name_id+1)

        # Fill the table
        else:
            if len(job_list) > 0:
                for i, row in job_list.iterrows():

                    # Fill the rows
                    self.jobsTable.insertRow(current_id)

                    # Fill the columns
                    j = 0
                    for data, column_name in zip(row, row.index):
                        if column_name in self.selected_columns:
                            item = qtw.QTableWidgetItem(str(data))
                            self.jobsTable.setItem(current_id, j, item)
                            j += 1

                    current_id += 1

        return current_id

    ##-\-\-\-\-\-\-\-\
    ## CONTEXTUAL MENU
    ##-/-/-/-/-/-/-/-/

    # ------------------------------------
    # Define the context Menu of the table
    def makeMenuEvent(self, event):

        contextMenu = qtw.QMenu()

        # Get the row
        row = self.jobsTable.rowAt(event.y())

        # Kill the selected job
        killJobAction = contextMenu.addAction("Kill Job")
        killJobAction.triggered.connect(lambda : self.killSelectedJob(row_id=row))

        #openAct = contextMenu.addAction("Restart Job")

        contextMenu.addSeparator()

        # Get the selection
        use_custom = self.customDisplayCheckBox.isChecked()
        custom_selection = self.customDisplayComboBox.currentText()

        if use_custom and custom_selection != "---":
            customColumns = contextMenu.addAction("Edit Current Display")
            customColumns.triggered.connect(self.editColumnsDisplay)
        else:
            customColumns = contextMenu.addAction("Select Columns")
            customColumns.triggered.connect(self.selectColumnsDisplay)

            customDisplay = contextMenu.addAction("Define Custom Display")
            customDisplay.triggered.connect(lambda : self.createCostumDisplay(row_id=row))

        action = contextMenu.exec_(qtg.QCursor.pos())

    # ---------------------
    # Kill the selected job
    def killSelectedJob(self, row_id=0):

        # Check if killing the job is possible
        if self.server.username != self.server.queryname:
            errorMessage("Incorrect Owner", "The username used to connect ("+self.server.username+") is not the owner of the selected job ("+self.server.queryname+"). The job cannot be killed.")

        else:
            # Get the job ID to kill
            job_id = self.jobs[ self.server.kill_col ].loc[row_id]

            # Ask for the confirmation
            if warningMessage("Delete Job", "Are you sure you want to delete the job "+job_id+"? This operation cannot be cancelled."):
                killJobs(self.server, job_id, command=self.server.kill_jobs)

    # --------------------
    # New column selection
    def selectColumnsDisplay(self):
        _open_window(self.parent, selectColumnsWindow, 'column_selection', column_names=self.jobs.columns)

    # ---------------------
    # Edit column selection
    def editColumnsDisplay(self):

        # Load the current selection
        display_name = self.customDisplayComboBox.currentText()
        display_dict = loadDisplay(display_name)
        selected_display = generateCustomDisplay(display_dict)

        # Open the selection in the window
        _open_window(self.parent, selectColumnsWindow, 'column_selection', column_names=self.jobs.columns, loaded_display=selected_display)

    # ----------------------
    # New custom job display
    def createCostumDisplay(self, row_id=0):

        # Get the job to use as ref
        job_content = self.jobs.loc[row_id]

        # Open the custom display creation window
        _open_window(self.parent, selectCustomDisplayWindow, 'custom_display', column_names=self.jobs.columns, example_job=job_content)
