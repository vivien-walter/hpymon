from HPyMon.get_jobs import getJobList, killJobs
from HPyMon.selection import makeSelection, getSelection, getSorted
from HPyMon.ssh_protocol import Server, sendCommands

##-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\
## SERVER MANAGEMENT AND COMMUNICATION
##-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/

# ------------------------------------
# Open an instance of the Server class
def openServer(ip_address, username, port=22, server_name='default', publickey=True, pkey_path='~/.ssh/id_rsa', password=None, tunnel=None):

    """ Open a server using the given details and return an instance of the Server class
    Argument(s):
        - ip_address { str } - Address of the server to connect to.
        - username { str } - Username to use to connect to the server.
        - port { int } - (Opt.) Port to use for the connection to the server.
                         Default is 22.
        - server_name { str } - (Opt.) Name of the server, for user convenience only.
                                Default is default.
        - publickey { bool } - (Opt.) Specify if the connection should be made using a public key (True) or a password (False).
                               Default is True.
        - pkey_path { str } - (Opt.) Path to the public key to use to connect on the servers.
                              Default is ~/.ssh/id_rsa.
        - password { str } - (Opt.) Password to use to connect to the server if a public key is not used.
                             Default is None.
        - tunnel { Server class } - (Opt.) Server to tunnel through to access to this server.
                                    Default is None (no tunnel).
    Output(s):
        - new_server { Server class } - Instance of the Server class that can be used to access the server.
    """

    # Get the authentification details
    if publickey:
        id_info = {'type':'publickey', 'key':pkey_path}
    else:
        id_info = {'type':'password', 'key':password}

    # Generate the instance
    new_server = Server(server_name, ip_address, username, identification=id_info, port=port, tunnel=tunnel)

    return new_server

# ---------------------------
# Send commands to the server
def doCommands(server_class, *commands, output=True):

    """ Send a list of commands in a server
    Argument(s):
        - server_class { Server class } - Instance of the server class to send the commands to.
        - commands { multiple str } - Command or list of commands to submit on the server.
        - output { bool } - (Opt.) Return the output from the command line.
                            Default is True.
    Output(s):
        - outputs { list of str } - List of all the string obtained when running the commands in input.
                                    If output is set to False, the function returns None.
    """

    # Send the commands to the server
    outputs = sendCommands(server_class, *commands, output=output)

    return outputs

##-\-\-\-\-\-\-\-\-\-\-\
## ONLINE JOB MANAGEMENT
##-/-/-/-/-/-/-/-/-/-/-/

# ------------------------------
# Fetch the list of running jobs
def getJobs(server, command='squeue -o %all -u', username=None, selection=None, column_name='WORK_DIR'):

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

    # Get the list of jobs
    job_df = getJobList(server, command=command, username=username, selection=selection, column_name=column_name)

    return job_df

# -----------------------------
# Cancel the given list of jobs
def cancelJobs(server, *job_ids, command='scancel'):

    """ Kill the selected jobs.
    Argument(s):
        - server { Server class } - Instance of the server class to send the commands to.
        - job_ids { multiple int or str } - Job ID or list of job IDs to kill on the server.
        - command { str } - (Opt.) Command line used to kill the jobs.
                            Default is scancel.
    """

    # Kill the selected jobs
    killJobs(server, *job_ids, command=command)

##-\-\-\-\-\-\-\-\-\-\
## SELECT AND SORT JOBS
##-/-/-/-/-/-/-/-/-/-/

# -------------------------------------------
# Generate an instance of the Selection class
def generateSelection(selection, column_name='WORK_DIR'):

    """ Generate an instance of the Selection class to process jobs.
    Argument(s):
        - selection { dict of tuples } - Dictionary of the conditions to select and sort the jobs.
                                         The dictionary should be of the following format:
                                         work_dir_path_index : (sorting name, [selection condition(s)], sorting position)
                                         e.g. 6: ('Lipid', ["DPPC","DOPC"], 3)
        - column_name { str } - (Opt.) Name of the column to read the path from to sort the columns.
                                Default is WORK_DIR
    Output(s):
        - selection_class { Selection class } - Instance of the Selection class to select and sort jobs.
    """

    # Make the selection
    selection_class = makeSelection(selection, column_name=column_name)

    return selection_class

# --------------------------------------
# Select specific jobs from the job list
def selectJobs(job_df, selection, column_name='WORK_DIR'):

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

    # Select the jobs
    selected_df = getSelection(job_df, selection, column_name=column_name)

    return selected_df

# -------------------------
# Sort the jobs in the list
def sortJobs(job_df, selection, column_name='WORK_DIR'):

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

    # Sort the jobs
    selected_df = getSorted(job_df, selection, column_name=column_name)

    return selected_df
