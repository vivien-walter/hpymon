import PyQt5.QtCore as qtc
import PyQt5.QtGui as qtg
import PyQt5.QtWidgets as qtw

from functools import partial
import os

from application_gui.common_gui_functions import CLabel, CLabelledLineEdit, CHorizontalSeparator, warningMessage, _open_window, errorMessage, updateSpinBox
from application_gui.window_server_settings import serverSettingsWindow

from selection import makeSelection, splitPath, getSorted, makeCustomColumns, generateCustomDisplay
from settings import addDisplay, displayExists, getDisplayList, loadDisplay
from ssh_protocol import generateServer

##-\-\-\-\-\-\-\-\-\-\-\-\
## WINDOW FOR USER SETTINGS
##-/-/-/-/-/-/-/-/-/-/-/-/

class selectCustomDisplayWindow(qtw.QMainWindow):
    def __init__(self, parent, column_names=None, example_job=None, loaded_display=None):
        super(selectCustomDisplayWindow, self).__init__(parent)

        # Initialise the subwindow
        self.parent = parent
        self.columns_names = column_names
        self.example_job = example_job
        self.loaded_display = loaded_display
        self.element_list = None

        # Selection elements
        self.sorting_elements = {}

        self.mainWidget = qtw.QWidget()
        self.mainLayout = qtw.QVBoxLayout(self.mainWidget)
        self.setWindowTitle("Generate Custom Display")

        # Populate the panel
        self.createColumnSelection(self.mainLayout)
        self.mainLayout.addWidget(CHorizontalSeparator())
        self.createColumnTreatment(self.mainLayout)
        self.createColumnDisplaySelection(self.mainLayout)
        self.mainLayout.addWidget(CHorizontalSeparator())
        self.createElementSelection(self.mainLayout)
        self.createUserActions(self.mainLayout)

        # Display the panel
        self.mainWidget.setLayout(self.mainLayout)
        self.setCentralWidget(self.mainWidget)
        self.show()
        self.resize(650, 500)
        self.setFixedSize(self.size())

    # ---------------------------------------------------
    # Reinitialise the display when the window is closed
    def closeEvent(self, event=None):
        event.accept()
        self.parent.subWindows['custom_display'] = None

    ##-\-\-\-\-\-\-\-\-\-\
    ## GENERATE THE DISPLAY
    ##-/-/-/-/-/-/-/-/-/-/

    # -------------------------------------------
    # Create the display for the column selection
    def createColumnSelection(self, parentWidget):

        # Generate the widget
        self.columnSelectionWidget = qtw.QWidget()
        self.columnSelectionLayout = qtw.QHBoxLayout(self.columnSelectionWidget)

        # Generate the label
        columnLabel = CLabel("Column for the custom display:")
        self.columnSelectionLayout.addWidget(columnLabel)

        # Get the default settings
        if self.loaded_display is None:
            _default_selection = 'WORK_DIR'
        else:
            _default_selection = self.loaded_display.selection.column

        # Generate the combo box
        self.columnComboBox = qtw.QComboBox()
        for column_name in self.columns_names:
            self.columnComboBox.addItem(column_name)
        self.columnSelectionLayout.addWidget(self.columnComboBox)

        # Select the default column
        col_ID = self.columnComboBox.findText(_default_selection, qtc.Qt.MatchFixedString)
        self.columnComboBox.setCurrentIndex(col_ID)
        self.columnComboBox.currentTextChanged.connect(self.updateColumnList)

        # Display the widget
        self.columnSelectionWidget.setLayout(self.columnSelectionLayout)
        parentWidget.addWidget(self.columnSelectionWidget)

    # --------------------------------------------------------------------
    # Create the display for the treatment to apply to the selected column
    def createColumnTreatment(self, parentWidget):

        # Generate the widget
        self.columnTreatmentWidget = qtw.QWidget()
        self.columnTreatmentLayout = qtw.QHBoxLayout(self.columnTreatmentWidget)

        # Get the default settings
        _default_box = True
        _default_separator = ''
        if self.loaded_display is not None:
            _default_box = self.loaded_display.selection.use_path
            _default_separator = self.loaded_display.selection.separator

        # Generate the checkbox
        self.usePathCheckBox = qtw.QCheckBox("Column is a path?")
        self.usePathCheckBox.setChecked(_default_box)
        self.usePathCheckBox.toggled.connect(self.updateColumnList)
        self.columnTreatmentLayout.addWidget(self.usePathCheckBox)

        # Add the separator entry
        customSeparatorLabelAndEntry, self.customSeparatorEntry = CLabelledLineEdit("Separator to use:")
        self.customSeparatorEntry.setEnabled(not _default_box)
        self.customSeparatorEntry.setText(_default_separator)
        self.customSeparatorEntry.editingFinished.connect(self.updateColumnList)
        self.columnTreatmentLayout.addWidget(customSeparatorLabelAndEntry)

        # Display the widget
        self.columnTreatmentLayout.setContentsMargins(0, 0, 0, 0)
        self.columnTreatmentWidget.setLayout(self.columnTreatmentLayout)
        parentWidget.addWidget(self.columnTreatmentWidget)

    # ----------------------------------------------
    # Generater the selection for the column display
    def createColumnDisplaySelection(self, parentWidget):

        # Generate the widget
        self.columnDisplayWidget = qtw.QWidget()
        self.columnDisplayLayout = qtw.QHBoxLayout(self.columnDisplayWidget)

        # Get the default settings
        _default_box = False
        _default_selection = '---'
        if self.loaded_display is not None:
            if self.loaded_display.subdisplay_name is not None:
                _default_box = True
                _default_selection = self.loaded_display.subdisplay_name

        # Generate the checkbox
        self.useColumnSelectionCheckBox = qtw.QCheckBox("Use Column selection?")
        self.useColumnSelectionCheckBox.setChecked(_default_box)
        self.useColumnSelectionCheckBox.toggled.connect(self.toggleColumnDisplaySelection)
        self.columnDisplayLayout.addWidget(self.useColumnSelectionCheckBox)

        # Generate the combo box
        self.columnDisplayComboBox = qtw.QComboBox()
        self.columnDisplayComboBox.addItem('---')
        self.populateColumnDisplays()
        self.columnDisplayComboBox.setEnabled(_default_box)
        self.columnDisplayLayout.addWidget(self.columnDisplayComboBox)

        # Select the default column
        col_ID = self.columnDisplayComboBox.findText(_default_selection, qtc.Qt.MatchFixedString)
        self.columnDisplayComboBox.setCurrentIndex(col_ID)

        # Display the widget
        self.columnDisplayLayout.setContentsMargins(0, 0, 0, 0)
        self.columnDisplayWidget.setLayout(self.columnDisplayLayout)
        parentWidget.addWidget(self.columnDisplayWidget)

    # --------------------------------------
    # Generate the server settings selection
    def createElementSelection(self, parentWidget):

        # Generate the widget
        self.elementSelectionWidget = qtw.QWidget()
        self.elementSelectionLayout = qtw.QVBoxLayout(self.elementSelectionWidget)

        # Generate the table of servers
        self.columnsTable = qtw.QTableWidget(0, 6)
        self.columnsTable.setHorizontalHeaderLabels( ['Element', '', 'Name', 'Position', '', 'Restrictions'] )

        self.columnsTable.setSelectionMode(qtw.QAbstractItemView.NoSelection)
        self.columnsTable.setEditTriggers(qtw.QAbstractItemView.NoEditTriggers)

        self.columnsTable.setShowGrid(False)
        self.columnsTable.setMinimumHeight(125)
        self.elementSelectionLayout.addWidget(self.columnsTable)

        # Populate the widget
        self.updateColumnList()

        # Add the name entry
        customColumnLabelAndEntry, self.customColumnsEntry = CLabelledLineEdit("Selection Name")

        if self.loaded_display is None:
            self.customColumnsEntry.setText('Custom display name')
        else:
            self.customColumnsEntry.setText( self.loaded_display.name )

        self.elementSelectionLayout.addWidget(customColumnLabelAndEntry)

        # Display the widget
        self.elementSelectionWidget.setLayout(self.elementSelectionLayout)
        parentWidget.addWidget(self.elementSelectionWidget)

    # --------------------------------------
    # Generate the control of the image zoom
    def createUserActions(self, parentWidget):

        # Generate the widget
        self.userActionsWidget = qtw.QWidget()
        self.userActionsLayout = qtw.QHBoxLayout(self.userActionsWidget)

        self.saveButton = qtw.QPushButton("Save")
        self.saveButton.clicked.connect(self.saveCustomSelection)
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

    # -------------------------------------------------
    # Toggle the status of the column display combo box
    def toggleColumnDisplaySelection(self):
        self.columnDisplayComboBox.setEnabled( self.useColumnSelectionCheckBox.isChecked() )

    # -------------------------------------------------------
    # Populate the combo box with the list of column displays
    def populateColumnDisplays(self):

        # Get the list of custom column displays
        custom_column_displays = getDisplayList(column_only=True)

        # Fill the combo box
        for display_name in custom_column_displays:
            self.columnDisplayComboBox.addItem( display_name )

    # ------------------------------------------------
    # Process the content of a column to return a list
    def processColumnContent(self, content):

        # Process a path
        if self.usePathCheckBox.isChecked():

            # Decompose the path
            content_list = splitPath(content)

            # Remove unwanted signs
            content_list = [x for x in content_list if x not in ['\\','/']]

        # Process using a separator
        else:

            # Get the separator
            _separator = self.customSeparatorEntry.text()

            # Split the content
            try:
                content_list = content.split(_separator)
            except:
                content_list = []

        return content_list

    # ----------------------------
    # Populate the list of servers
    def updateColumnList(self):

        # Update the selection
        self.customSeparatorEntry.setEnabled( not self.usePathCheckBox.isChecked() )

        # Delete the values
        rowCount = self.columnsTable.rowCount()
        if rowCount > 0:
            for i in range(rowCount):
                self.columnsTable.removeRow(0)

        # Get the current selection
        selected_column = self.columnComboBox.currentText()
        selected_content = self.example_job[selected_column]

        # Process the selected content
        self.element_list = self.processColumnContent(selected_content)

        # Populate the widget
        self.sorting_checkboxes = []
        self.sorting_names = []
        self.sorting_entries = []
        self.selecting_checkboxes = []
        self.selecting_entries = []

        sorted_elements = False
        if len(self.element_list) > 1:
            for i, name in enumerate(self.element_list):

                # Get the loaded state
                _condition_selected = False
                _condition_name = ''
                _sorting_selected = False
                _sorting_name = ''
                if self.loaded_display is not None:

                    # Set the selection conditions
                    if i in [x for x, _ in self.loaded_display.selection.conditions]:
                        _condition_selected = True
                        _condition_namelist = [x for y, x in self.loaded_display.selection.conditions if y == i][0]

                        _condition_name = _condition_namelist[0]
                        for crt_name in _condition_namelist[1:]:
                            _condition_name += ','+crt_name

                    # Set the sorting conditions
                    if i in self.loaded_display.selection.sorting['columns']:
                        _sorting_selected = True
                        _sorting_name = self.loaded_display.selection.sorting['names'][ self.loaded_display.selection.sorting['columns'].index(i) ]

                        sorted_elements = True

                # Fill the rows
                self.columnsTable.insertRow(i)

                # Prepare the sorting button
                currentSortingCheckBox = qtw.QCheckBox("Sort by...")
                currentSortingCheckBox.setChecked(_sorting_selected)
                currentSortingCheckBox.clicked.connect(partial(self.toggleSorting, id=i))

                self.sorting_checkboxes.append( currentSortingCheckBox )

                # Prepare the entry field
                currentSortingNameEntry = qtw.QLineEdit()
                currentSortingNameEntry.setEnabled(_sorting_selected)

                if _sorting_selected:
                    currentSortingNameEntry.setText(_sorting_name)

                self.sorting_names.append( currentSortingNameEntry )

                # Prepare the spinbox
                currentPositionSpinbox = qtw.QSpinBox()
                currentPositionSpinbox.setEnabled(_sorting_selected)
                currentPositionSpinbox.valueChanged.connect(partial(self.updateSortingPositions, id=i))

                self.sorting_entries.append( currentPositionSpinbox )

                # Prepare the selection button
                currentSelectionCheckBox = qtw.QCheckBox("Select by...")
                currentSelectionCheckBox.setChecked(_condition_selected)
                currentSelectionCheckBox.clicked.connect(partial(self.toggleSelection, id=i))

                self.selecting_checkboxes.append( currentSelectionCheckBox )

                # Prepare the entry field
                currentRestrictionEntry = qtw.QLineEdit()
                currentRestrictionEntry.setEnabled(_condition_selected)

                if _condition_selected:
                    currentRestrictionEntry.setText(_condition_name)

                self.selecting_entries.append( currentRestrictionEntry )

                # Fill the columns
                self.columnsTable.setItem(i, 0, qtw.QTableWidgetItem(str(name)))
                self.columnsTable.setCellWidget(i, 1, currentSortingCheckBox)
                self.columnsTable.setCellWidget(i, 2, currentSortingNameEntry)
                self.columnsTable.setCellWidget(i, 3, currentPositionSpinbox)
                self.columnsTable.setCellWidget(i, 4, currentSelectionCheckBox)
                self.columnsTable.setCellWidget(i, 5, currentRestrictionEntry)

        # Get the positions
        if sorted_elements:
            for pos, id in enumerate( self.loaded_display.selection.sorting['columns'] ):
                updateSpinBox(self.sorting_entries[id], pos)

        # Resize the columns
        header = self.columnsTable.horizontalHeader()
        for i in range( 6 ):
            header.setSectionResizeMode(i, qtw.QHeaderView.ResizeToContents)

    ##-\-\-\-\-\-\-\-\-\-\-\-\-\
    ## MANAGE THE SORTING OPTIONS
    ##-/-/-/-/-/-/-/-/-/-/-/-/-/

    # -------------------------------------------------------
    # Toggle the state of the field for the sorting selection
    def toggleSorting(self, id=0):

        # Get the state of the checkbox
        checkbox_state = self.sorting_checkboxes[id].isChecked()

        # Change the status of the entry
        self.sorting_names[id].setEnabled(checkbox_state)
        self.sorting_entries[id].setEnabled(checkbox_state)

        # Edit the value of the spinbox
        if checkbox_state:

            # Set sorting name entry
            if self.sorting_names[id].text() == "":
                self.sorting_names[id].setText(self.element_list[id])

            # Set new position
            _n_checked_boxes = len(self.sorting_elements.keys())
            self.sorting_elements[id] = _n_checked_boxes

        # Remove the spinbox from the selection
        else:

            # Remove the element from the dictionary and update it
            del self.sorting_elements[id]
            self.removeGapsSorting()

            # Set the new value
            _n_checked_boxes = 0

        updateSpinBox(self.sorting_entries[id], _n_checked_boxes)

    # ----------------------------------------
    # Remove the gaps in the position ordering
    def removeGapsSorting(self):

        if len(self.sorting_elements.keys()) != 0:

            # Extract informations from the dictionary
            list_ids = self.sorting_elements.keys()
            list_positions = [self.sorting_elements[x] for x in list_ids]

            # Sort the lists
            list_ids = [x for _, x in sorted(zip(list_positions, list_ids))]
            list_positions = sorted(list_positions)
            list_new_positions = list(range( len(list_positions) ))

            # Replace the values
            for i, new_position in zip(list_ids, list_new_positions):
                updateSpinBox(self.sorting_entries[i], new_position)

            # Regenerate the dictionary
            self.sorting_elements = dict(zip(list_ids, list_new_positions))

    # -------------------------
    # Update the spinbox values
    def updateSortingPositions(self, id=0):

        # Get the new and old values
        new_value = self.sorting_entries[id].value()
        old_value = self.sorting_elements[id]

        # Coerce value
        if new_value >= len(self.sorting_elements.keys()):
            new_value = len(self.sorting_elements.keys()) - 1
        elif new_value < 0:
            new_value = 0

        # Scan through the intermediate elements
        mod_sign = 1
        if new_value < old_value:
            mod_sign = -1

        for pos in range(old_value+mod_sign, new_value+mod_sign, mod_sign):

            # Get the id of the concerned value
            current_id = [x for x in self.sorting_elements.keys() if self.sorting_elements[x] == pos][0]

            # Edit the spinbox and the dictionary
            updateSpinBox(self.sorting_entries[current_id], pos - mod_sign)
            self.sorting_elements[current_id] = pos - mod_sign

        # Edit the value
        updateSpinBox(self.sorting_entries[id], new_value)
        self.sorting_elements[id] = new_value

    ##-\-\-\-\-\-\-\-\-\-\-\-\-\-\
    ## MANAGE THE SELECTION OPTIONS
    ##-/-/-/-/-/-/-/-/-/-/-/-/-/-/

    # -----------------------------------------------
    # Toggle the state of the field for the selection
    def toggleSelection(self, id=0):

        # Get the state of the checkbox
        checkbox_state = self.selecting_checkboxes[id].isChecked()

        # Change the status of the entry
        self.selecting_entries[id].setEnabled(checkbox_state)

        # Edit the value of the spinbox
        if checkbox_state and self.selecting_entries[id].text() == "":
            self.selecting_entries[id].setText(self.element_list[id])

    ##-\-\-\-\-\-\-\-\-\-\
    ## SAVE THE SELECTIONS
    ##-/-/-/-/-/-/-/-/-/-/

    # ---------------------------------
    # Save the current custom selection
    def saveCustomSelection(self):

        # Process all the columns
        selection_dict = {}
        for id in range(len(self.element_list)):

            # Get the checkboxes status
            to_sort = self.sorting_checkboxes[id].isChecked()
            to_select = self.selecting_checkboxes[id].isChecked()

            # Add the element to the selection
            if to_sort or to_select:

                # Set the sorting options
                if to_sort:
                    sorting_name = self.sorting_names[id].text()
                    sorting_position = self.sorting_entries[id].value()

                else:
                    sorting_name = None
                    sorting_position = -1

                # Set the selection options
                if to_select:
                    selection_elements = self.selecting_entries[id].text().split(",")
                    selection_elements = [x.strip() for x in selection_elements]
                else:
                    selection_elements = None

                # Update the dictionary
                selection_dict[id] = (sorting_name, selection_elements, sorting_position)

        # Check that the selection is not empty
        if len(selection_dict.keys()) == 0:
            errorMessage("Empty Selection", "The current selection is empty. Select at least 1 element to proceed.")

        else:

            # Get the information of the display
            display_name = self.customColumnsEntry.text()
            use_path = self.usePathCheckBox.isChecked()
            separator = self.customSeparatorEntry.text()

            # Generate the new selection
            display_class = makeSelection(selection_dict, column_name=self.columnComboBox.currentText(), display_name=display_name, return_selection=False, use_path=use_path, separator=separator)

            # Add the column selection if set
            if self.useColumnSelectionCheckBox.isChecked() and self.columnDisplayComboBox.currentText() != '---':

                # Retrieve the column list from the selected display
                _display_details = loadDisplay(self.columnDisplayComboBox.currentText())
                loaded_display = generateCustomDisplay(_display_details)

                # Update the column contents
                display_class.display_type = 'selection_column'
                display_class.columns = loaded_display.columns

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
