import os
import pandas as pd

##-\-\-\-\-\-\-\-\
## SELECTION CLASS
##-/-/-/-/-/-/-/-/

class Selection:
    def __init__(self, column_name, conditions, sorting_columns, sorting_names):

        # Get the name of the column to extract
        self.column = column_name

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
        job_ids = _select_indices(job_df, self.conditions, column_name=self.column)

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
        jobs_dict = _sort_jobs(job_df, self.sorting['columns'], self.sorting['names'], column_name=self.column)

        return jobs_dict

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
def _splitall(path):

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
    return allparts

# -------------------------------------------
# Select the indices to keep in the selection
def _select_indices(job_df, path_conditions, column_name='WORK_DIR'):

    # Get the column to read
    all_jobs = job_df[column_name]

    # Select the indices
    selected_jobs = []
    for job_id, job_path in enumerate(all_jobs):

        # Split the path in the column
        path_elements = [x for x in _splitall(job_path) if x not in ["/", "\\"]]

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
def _sort_jobs(job_df, sorting_columns, sorting_names, column_name='WORK_DIR'):

    # Get the column to read
    all_jobs = job_df[column_name]

    # Select the indices
    sorted_jobs = {}
    for job_id, job_path in enumerate(all_jobs):

        # Split the path in the column
        path_elements = [x for x in _splitall(job_path) if x not in ["/", "\\"]]

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

##-\-\-\-\-\-\-\-\
## PUBLIC FUNCTIONS
##-/-/-/-/-/-/-/-/

# ---------------------------
# Create the selection to use
def makeSelection(selection, column_name='WORK_DIR'):

    """ Generate an instance of the Selection class to process jobs.
    Argument(s):
        - selection { dict of tuples } - Dictionary of the conditions to select and sort the jobs.
                                         The dictionary should be of the following format:
                                         work_dir_path_index : (sorting name, [selection condition(s)], sorting position)
                                         e.g. 6: ('Lipid', ["DPPC","DOPC"], 3)
        - column_name { str } - (Opt.) Name of the column to read the path from to sort the columns.
                                Default is WORK_DIR
    Output(s):
        - selection { Selection class } - Instance of the Selection class to select and sort jobs.
    """

    # Process the selection to get the elements
    path_conditions, sorting_columns, sorting_names = _process_selection(selection)

    # Generate the instance of the Selection class
    new_selection = Selection(column_name, path_conditions, sorting_columns, sorting_names)

    return new_selection

# --------------------------------------------
# Return the jobs based on the given selection
def getSelection(job_df, selection, column_name='WORK_DIR'):

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
        selection = makeSelection(selection, column_name=column_name)

    # Get the selected jobs
    selected_df = selection.selectJobs(job_df)

    return selected_df

# -----------------------------------------
# Sort the job based on the given selection
def getSorted(job_df, selection, column_name='WORK_DIR'):

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
        selection = makeSelection(selection, column_name=column_name)

    # Get the selected jobs
    selected_df = selection.sortJobs(job_df, select_jobs=True)

    return selected_df
