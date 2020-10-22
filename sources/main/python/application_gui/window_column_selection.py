import PyQt5.QtCore as qtc
import PyQt5.QtGui as qtg
import PyQt5.QtWidgets as qtw

from functools import partial

from application_gui.common_gui_functions import CLabel, CLabelledLineEdit, CHorizontalSeparator, warningMessage, _open_window, errorMessage
from application_gui.window_server_settings import serverSettingsWindow

from selection import makeCustomColumns
from settings import addDisplay, displayExists
from ssh_protocol import generateServer

##-\-\-\-\-\-\-\-\-\-\-\-\
## WINDOW FOR USER SETTINGS
##-/-/-/-/-/-/-/-/-/-/-/-/

class selectColumnsWindow(qtw.QMainWindow):
    def __init__(self, parent, column_names=None, loaded_display=None):
        super(selectColumnsWindow, self).__init__(parent)

        # Initialise the subwindow
        self.parent = parent
        self.columns_names = column_names
        self.loaded_display = loaded_display

        self.mainWidget = qtw.QWidget()
        self.mainLayout = qtw.QVBoxLayout(self.mainWidget)
        self.setWindowTitle("Select Columns to Display")

        # Populate the panel
        self.createListColumns(self.mainLayout)
        self.createUserActions(self.mainLayout)

        # Display the panel
        self.mainWidget.setLayout(self.mainLayout)
        self.setCentralWidget(self.mainWidget)
        self.show()
        self.resize(450, 400)
        self.setFixedSize(self.size())

    # ---------------------------------------------------
    # Reinitialise the display when the window is closed
    def closeEvent(self, event=None):
        event.accept()
        self.parent.subWindows['column_selection'] = None

    ##-\-\-\-\-\-\-\-\-\-\
    ## GENERATE THE DISPLAY
    ##-/-/-/-/-/-/-/-/-/-/

    # --------------------------------------
    # Generate the server settings selection
    def createListColumns(self, parentWidget):

        # Generate the widget
        self.columnSelectionWidget = qtw.QWidget()
        self.columnSelectionLayout = qtw.QVBoxLayout(self.columnSelectionWidget)

        # Generate the table of servers
        self.columnsTable = qtw.QTableWidget(0, 2)
        self.columnsTable.setHorizontalHeaderLabels( ['Column', ''] )

        self.columnsTable.setSelectionMode(qtw.QAbstractItemView.NoSelection)
        self.columnsTable.setEditTriggers(qtw.QAbstractItemView.NoEditTriggers)

        self.columnsTable.setShowGrid(False)
        self.columnsTable.setMinimumHeight(125)
        self.columnSelectionLayout.addWidget(self.columnsTable)

        # Populate the widget
        self.updateElementList()

        # Add the name entry
        customColumnLabelAndEntry, self.customColumnsEntry = CLabelledLineEdit("Selection Name")

        if self.loaded_display is None:
            self.customColumnsEntry.setText('Custom column display')
        else:
            self.customColumnsEntry.setText( self.loaded_display.name )

        self.columnSelectionLayout.addWidget(customColumnLabelAndEntry)

        # Display the widget
        self.columnSelectionWidget.setLayout(self.columnSelectionLayout)
        parentWidget.addWidget(self.columnSelectionWidget)

    # --------------------------------------
    # Generate the control of the image zoom
    def createUserActions(self, parentWidget):

        # Generate the widget
        self.userActionsWidget = qtw.QWidget()
        self.userActionsLayout = qtw.QHBoxLayout(self.userActionsWidget)

        self.saveButton = qtw.QPushButton("Save")
        self.saveButton.clicked.connect(self.saveColumnSelection)
        self.saveButton.setStatusTip("Save the settings.")
        self.saveButton.setFixedWidth(125)
        self.userActionsLayout.addWidget(self.saveButton, alignment=qtc.Qt.AlignLeft)

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

    # -----------------------------
    # Populate the list of elements
    def updateElementList(self):

        # Delete the values
        rowCount = self.columnsTable.rowCount()
        if rowCount > 0:
            for i in range(rowCount):
                self.columnsTable.removeRow(0)

        # Populate the widget
        self.column_checkboxes = []
        if len(self.columns_names) > 0:
            for i, name in enumerate(self.columns_names):

                # Fill the rows
                self.columnsTable.insertRow(i)

                # Prepare the connect button
                currentDisplayCheckBox = qtw.QCheckBox("Display")

                # Pre-check the value
                if self.loaded_display is not None:
                    for item in self.loaded_display.columns:
                        if name == item:
                            currentDisplayCheckBox.setChecked(True)

                self.column_checkboxes.append( currentDisplayCheckBox )

                # Fill the columns
                self.columnsTable.setItem(i, 0, qtw.QTableWidgetItem(str(name)))
                self.columnsTable.setCellWidget(i, 1, currentDisplayCheckBox)

        # Resize the columns
        header = self.columnsTable.horizontalHeader()
        for i in range( 2 ):
            header.setSectionResizeMode(i, qtw.QHeaderView.ResizeToContents)

    ##-\-\-\-\-\-\-\-\-\-\
    ## SAVE THE SELECTIONS
    ##-/-/-/-/-/-/-/-/-/-/

    # -------------------------
    # Save the column selection
    def saveColumnSelection(self):

        # Get all the selections
        _selected_columns = [i for i,x in enumerate(self.column_checkboxes) if x.isChecked() is True]

        # Raise a warning if no selection has been made
        if len(_selected_columns) == 0:
            errorMessage("Empty Selection", "The current selection is empty. Select at least 1 column to display to proceed.")

        # Get the list of column names
        else:
            column_names = [x for i, x in enumerate(self.columns_names) if i in _selected_columns]

            # Get the name of the display
            display_name = self.customColumnsEntry.text()

            # Create the selection
            display_class = makeCustomColumns(column_names, name=display_name)

            # Check if the name is not in the file
            save_in_file = True
            if displayExists(display_class):
                save_in_file = warningMessage("Display in memory", "The Display name ("+display_name+") is already used in the memory. Are you sure you want to replace this display?")

            # Add the display to the config file
            if save_in_file:
                addDisplay(display_class)

                # Refresh the custom display list
                self.parent.serverTabDisplay.updateCustomSelections()

                # Close the current window
                self.close()
