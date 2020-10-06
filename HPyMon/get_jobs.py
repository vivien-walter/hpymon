import numpy as np
import pandas as pd

from HPyMon.selection import getSelection
from HPyMon.ssh_protocol import sendCommands

##-\-\-\-\-\-\-\-\-\
## PRIVATE FUNCTIONS
##-/-/-/-/-/-/-/-/-/

# --------------------------
# Get the list on the server
def _get_on_server(server, command='squeue -o %all -u', username=None):

    # Get the full command line
    if username is None:
        username = server.username
    command = command.strip() + ' ' + username.strip()

    # Fetch the information on the server
    raw_joblist = sendCommands(server, command, output=True)

    return raw_joblist

# ----------------------------------------------
# Convert the raw job list in a pandas dataframe
def _list2df(raw_joblist):

    # Convert the job list in an array of string
    all_jobs = raw_joblist.strip().split('\n')

    job_array = []
    for job in all_jobs:
        job_array.append(job.replace(" ", "").split('|'))
    job_array = np.array(job_array).T

    # Convert the array into a dataframe
    job_df = pd.DataFrame( {job_array[0,0]:job_array[0,1:]} )
    for i in range(1, job_array.shape[0]):
        job_df[job_array[i,0]] = job_array[i,1:]

    return job_df

##-\-\-\-\-\-\-\-\
## PUBLIC FUNCTIONS
##-/-/-/-/-/-/-/-/

# ---------------------
# Retrieve the job list
def getJobList(server, command='squeue -o %all -u', username=None, selection=None, column_name='WORK_DIR'):

    """ Get the list of the job submitted and/or running.
    Argument(s):
        - server { Server class } - Instance of the server class to send the commands to.
        - command { str } - (Opt.) Command line used to kill the jobs.
                            Default is squeue -o %all -u.
        - username { str } - (Opt.) Username on the server, if different from the username to connect to the server.
                             Default (None) is same username.
        - selection { Selection class     - (Opt.) Instance of the Selection class or dictionary of the conditions to select and sort the jobs.
                      or dict of tuples }   If a dictionary is provided, it should has the same format as the input in the makeSelection() function.
                                            Default is None (no selection).
        - column_name { str } - (Opt.) Name of the column to read the path from to sort the columns.
                                Default is WORK_DIR
    Output(s):
        - job_df { pandas DataFrame } - Table with all the jobs and their properties.
    """

    # Get the information from the server
    raw_joblist = _get_on_server(server, command=command, username=username)
    raw_joblist = raw_joblist[0]

    # Convert the job list in a pandas dataframe
    job_df = _list2df(raw_joblist)

    # Return only the selected columns if required
    if selection is not None:
        job_df = getSelection(job_df, selection, column_name=column_name)

    return job_df

# ----------------------
# Kill the selected jobs
def killJobs(server, *job_ids, command='scancel'):

    """ Kill the selected jobs.
    Argument(s):
        - server { Server class } - Instance of the server class to send the commands to.
        - job_ids { multiple int or str } - Job ID or list of job IDs to kill on the server.
        - command { str } - (Opt.) Command line used to kill the jobs.
                            Default is scancel.
    """

    # Create the command
    for j_id in job_ids:
        command += ' ' + str(j_id)

    # Kill all the selected jobs
    sendCommands(server, command, output=False)
