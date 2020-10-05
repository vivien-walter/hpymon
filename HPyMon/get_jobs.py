import numpy as np
import pandas as pd

from HPyMon.ssh_protocol import sendCommands

##-\-\-\-\-\-\-\-\-\
## PRIVATE FUNCTIONS
##-/-/-/-/-/-/-/-/-/

# --------------------------
# Get the list on the server
def _get_on_server(server, command='squeue -o %all -u ', username=None):

    # Get the full command line
    if username is None:
        username = server.username
    command = command + username

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
def getJobList(server, command='squeue -o %all -u ', username=None):

    # Get the information from the server
    raw_joblist = _get_on_server(server, command=command, username=username)
    raw_joblist = raw_joblist[0]

    # Convert the job list in a pandas dataframe
    job_df = _list2df(raw_joblist)

    return job_df
