import os
import pandas as pd
import re

##-\-\-\-\-\-\-\-\
## SELECTION CLASS
##-/-/-/-/-/-/-/-/

class Selection:
    def __init__(self, column_name, conditions, sorting_columns, sorting_names, use_path=True, separator=""):

        # Get the name of the column to extract
        self.column = column_name
        self.use_path = use_path
        self.separator = separator

        # Return the conditions for the selection
        self.conditions = conditions

        # Return the sorting conditions
        self.sorting = {
        'columns': sorting_columns,
        'names': sorting_names
        }

    # -------------------------------------------------------
    # Get the list of indices in agreement with the selection
    def selectJobs(self, job_df):

        # Get the indices
        job_ids = _select_indices(job_df, self.conditions, column_name=self.column, use_path=self.use_path, separator=self.separator)

        # Select the rows to keep
        selected_df =  job_df.iloc[job_ids]

        return selected_df

    # ---------------------------------
    # Sort the jobs using the selection
    def sortJobs(self, job_df, select_jobs=True):

        # Select first the jobs to process
        if select_jobs:
            job_df = self.selectJobs(job_df)

        # Sort the jobs
        jobs_dict = _sort_jobs(job_df, self.sorting['columns'], self.sorting['names'], column_name=self.column, use_path=self.use_path, separator=self.separator)

        return jobs_dict

##-\-\-\-\-\-\-\
## DISPLAY CLASS
##-/-/-/-/-/-/-/

class CustomDisplay:
    def __init__(self, name, display_type='column', column_names=None, selection_class=None, subdisplay=None):

        # Settings of the display
        self.name = name
        self.display_type = display_type
        self.subdisplay_name = subdisplay

        # Settings for the custom column display
        self.columns = column_names
        if column_names is not None:
            self._load_column_names(column_names)

        # Settings for the custom display
        self.selection = selection_class

    # ------------------------------------
    # Load the column names from the input
    def _load_column_names(self, column_names):

        # Keep the list
        if isinstance(column_names, list):
            self.columns = column_names

        # Convert the string in a list
        else:
            self.columns = re.findall("\'(.+?)\'", column_names)

##-\-\-\-\-\-\-\-\-\
## PRIVATE FUNCTIONS
##-/-/-/-/-/-/-/-/-/

# ---------------------------
# Process the input selection
def _process_selection(selection):

    # Initialise the new lists
    path_conditions = []

    # Process all the selections
    new_selection_dict = {}
    for path_index in selection.keys():

        # Extract the selection details
        display_name, selection_list, display_position = selection[path_index]

        # Append to the list of conditions
        if selection_list is not None:
            path_conditions.append( (path_index, selection_list) )

        # Invert display position and element index
        if display_position != -1:
            new_selection_dict[display_position] = [path_index, display_name]

    # Sort the sorting selection by increasing display positions
    display_positions = sorted(list(new_selection_dict.keys()))
    sorting_columns = [ new_selection_dict[x][0] for x in display_positions ]
    sorting_names = [ new_selection_dict[x][1] for x in display_positions ]

    return path_conditions, sorting_columns, sorting_names

# -------------------------------------------------------------------
# Split a path into all its components - from O'Reilly online library
def _splitall(path, use_path=True, separator=''):

    # Read the path
    if use_path:
        allparts = []
        while 1:
            parts = os.path.split(path)

            if parts[0] == path:  # sentinel for absolute paths
                allparts.insert(0, parts[0])
                break
            elif parts[1] == path: # sentinel for relative paths
                allparts.insert(0, parts[1])
                break
            else:
                path = parts[0]
                allparts.insert(0, parts[1])

    # Use a separator
    else:
        allparts = path.split(separator)

    return allparts

# -------------------------------------------
# Select the indices to keep in the selection
def _select_indices(job_df, path_conditions, column_name='WORK_DIR', use_path=True, separator=''):

    # Get the column to read
    all_jobs = job_df[column_name]

    # Select the indices
    selected_jobs = []
    for job_id, job_path in enumerate(all_jobs):

        # Split the path in the column
        path_elements = [x for x in _splitall(job_path, use_path=use_path, separator=separator) if x not in ["/", "\\"]]

        # Check if the ID should be kept or not
        keep_id = True
        for condition_index, condition_values in path_conditions:
            if not path_elements[condition_index] in condition_values:
                keep_id = False

        # Append the ID if the job can be kept
        if keep_id:
            selected_jobs.append(job_id)

    return selected_jobs

# ---------
# Sort jobs
def _sort_jobs(job_df, sorting_columns, sorting_names, column_name='WORK_DIR', use_path=True, separator=''):

    # Get the column to read
    all_jobs = job_df[column_name]

    # Select the indices
    sorted_jobs = {}
    for job_id, job_path in enumerate(all_jobs):

        # Split the path in the column
        path_elements = [x for x in _splitall(job_path, use_path=use_path, separator=separator) if x not in ["/", "\\"]]

        # Sort the jobs
        prev_selection = []
        for i, (path_id, name) in enumerate(zip(sorting_columns, sorting_names)):

            # Get the current path element name
            element_name = path_elements[path_id]

            # Get the current level of the dict
            current_dict = sorted_jobs
            if i != 0:
                for j in range(i):
                    current_dict = current_dict[prev_selection[j]]

            # Initialise dict if required
            if element_name not in current_dict.keys():
                current_dict[element_name] = {}

            # Add the name to the previous selection tracking
            prev_selection.append(element_name)

        # Convert the last element in an array
        if len(current_dict[element_name]) == 0:
            current_dict[element_name] = []

        # Add the job to the element
        current_dict[element_name].append(job_id)

    # Convert the list in the last level of the dictionary in dataframes
    sorted_jobs = _dict_items2list(job_df, sorted_jobs)

    return sorted_jobs

# ---------------------------------------------------------------------------------------
# Process all the elements of a multi-level dict to convert the last level in a dataframe
def _dict_items2list(job_df, multi_dict):

    # Process all the keys
    for key in multi_dict.keys():

        # Convert the level if it is a list
        if isinstance(multi_dict[key], list):
            multi_dict[key] = job_df.iloc[multi_dict[key]]

        # Otherwise, process the next level
        else:
            multi_dict[key] = _dict_items2list(job_df, multi_dict[key])

    return multi_dict

# ------------------------------------------------------------
# Convert the settings all-string input in a set of dictionary
def _setting2custom(settings_dict):

    # Get the name of the column for selection
    column_selection = settings_dict['column_selection']

    # Get all the conditions
    all_conditions = []
    sorting_indices = []
    sorting_names = []
    for key in settings_dict.keys():

        # Read the selection conditions
        if 'conditions_' in key:
            index = int( key.split('_')[1] )
            condition = re.findall("\'(.+?)\'", settings_dict[key])

            all_conditions.append((index, condition))

        elif 'sorting_' in key:
            index = int( key.split('_')[1] )
            name = re.findall("\'(.+?)\'", settings_dict[key])[0]

            sorting_indices.append(index)
            sorting_names.append(name)

    # Get column splitting options
    use_path = settings_dict['use_path'] == 'True'
    separator = ""
    if settings_dict['separator'] != 'None':
        separator = settings_dict['separator']

    # Prepare the instance
    new_selection = Selection(column_selection, all_conditions, sorting_indices, sorting_names, use_path=use_path, separator=separator)

    return new_selection

##-\-\-\-\-\-\-\-\
## PUBLIC FUNCTIONS
##-/-/-/-/-/-/-/-/

# --------------------------------------------
# Split the input path into a list of elements
def splitPath(selection):

    """ Decompose a path into the list of all elements.
    Argument(s):
        - selection { str } - Path to decompose.
    Output(s):
        - element_list { list of str } - List of all the elements composing the input path.
    """

    element_list = _splitall(selection)

    return element_list

# ----------------------------------------
# Create the custom column selection class
def makeCustomColumns(column_names, name='Custom'):

    """ Generate an instance of the CustomDisplay class to display only selected columns.
    Argument(s):
        - column_names { list of str } - List of the columns to display in the custom selection.
        - name { str } - (Opt.) Name of the selection.
                         Default is Custom
    Output(s):
        - display_instance { CustomDisplay class } - Instance of the CustomDisplay class to select and display columns.
    """

    # Generate the instance
    display_instance = CustomDisplay(name, display_type='column', column_names=column_names)

    return display_instance

# ------------------------------------
# Get the custom display from the file
def generateCustomDisplay(display_dict):

    # Generate the instance for a column selection
    if display_dict['display_type'] == 'column':
        display_instance = CustomDisplay(display_dict['name'], display_type=display_dict['display_type'], column_names=display_dict['column_names'])

    # Generate the instance for a custom display
    elif 'selection' in display_dict['display_type']:
        new_selection = _setting2custom(display_dict)
        display_instance = CustomDisplay(display_dict['name'], display_type=display_dict['display_type'], selection_class=new_selection)

        # Load column selection
        if display_dict['display_type'] == 'selection_column':
            display_instance.subdisplay_name = display_dict['subdisplay_name']
            display_instance._load_column_names(display_dict['column_names'])

    return display_instance

# ---------------------------
# Create the selection to use
def makeSelection(selection, column_name='WORK_DIR', display_name='default', return_selection=True, use_path=True, separator=''):

    """ Generate an instance of the Selection class to process jobs.
    Argument(s):
        - selection { dict of tuples } - Dictionary of the conditions to select and sort the jobs.
                                         The dictionary should be of the following format:
                                         work_dir_path_index : (sorting name, [selection condition(s)], sorting position)
                                         e.g. 6: ('Lipid', ["DPPC","DOPC"], 3)
        - column_name { str } - (Opt.) Name of the column to read the path from to sort the columns.
                                Default is WORK_DIR
        - display_name { str } - (Opt.) Name of the display.
                                Default is default
        - return_selection { bool } - (Opt.) Return an instance of the Selection class.
                                      Default is True
    Output(s):
        - selection { Selection class } - Instance of the Selection class to select and sort jobs.
    """

    # Process the selection to get the elements
    path_conditions, sorting_columns, sorting_names = _process_selection(selection)

    # Generate the instance of the Selection class
    new_selection = Selection(column_name, path_conditions, sorting_columns, sorting_names, use_path=use_path, separator=separator)

    if return_selection:
        return new_selection

    else:
        display_instance = CustomDisplay(display_name, display_type='selection', selection_class=new_selection)
        return display_instance

# --------------------------------------------
# Return the jobs based on the given selection
def getSelection(job_df, selection, column_name='WORK_DIR', use_path=True, separator=''):

    """ Select a list of jobs based on the selection conditions.
    Argument(s):
        - job_df { pandas DataFrame } - Table with all the jobs and their properties.
        - selection { Selection class     - Instance of the Selection class or dictionary of the conditions to select and sort the jobs.
                      or dict of tuples }   If a dictionary is provided, it should has the same format as the input in the makeSelection() function.
        - column_name { str } - (Opt.) Name of the column to read the path from to sort the columns.
                                Default is WORK_DIR
    Output(s):
        - selected_df { pandas DataFrame } - Table with all the selected jobs and their properties.
    """

    # Turn the selection into a class if it's a dictionary
    if isinstance(selection, dict):
        selection = makeSelection(selection, column_name=column_name, use_path=use_path, separator=separator)

    # Get the selected jobs
    selected_df = selection.selectJobs(job_df)

    return selected_df

# -----------------------------------------
# Sort the job based on the given selection
def getSorted(job_df, selection, column_name='WORK_DIR', use_path=True, separator=''):

    """ Select and sort a list of jobs based on the selection conditions.
    Argument(s):
        - job_df { pandas DataFrame } - Table with all the jobs and their properties.
        - selection { Selection class     - Instance of the Selection class or dictionary of the conditions to select and sort the jobs.
                      or dict of tuples }   If a dictionary is provided, it should has the same format as the input in the makeSelection() function.
        - column_name { str } - (Opt.) Name of the column to read the path from to sort the columns.
                                Default is WORK_DIR
    Output(s):
        - selected_df { dict of pandas DataFrame } - Dict of sorted tables with all the selected jobs and their properties.
    """

    # Turn the selection into a class if it's a dictionary
    if isinstance(selection, dict):
        selection = makeSelection(selection, column_name=column_name, use_path=use_path, separator=separator)

    # Get the selected jobs
    selected_df = selection.sortJobs(job_df, select_jobs=True)

    return selected_df
