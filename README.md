# H-PyMon

Python package to display the job running on a distant HPC

## Installation

1. Download the package
2. Open in a Terminal
3. Run the following command:
    ```sh
    > python3 setup.py install
    ```

## Tutorials

### Connection to a server

#### Connect directly to a server to send a command

In order to connect to a server and send a simple command, we need to do two things:
1. Define the server in an instance of a class called *Server*, using the **openServer()** function
2. Send the command to the server defined above using the **doCommands()** function.

Here is a typical example on how to do connect to a server and run the *ls* command to
list all the files in the home directory and return the output in a variable to display.

```python
from HPyMon import *

# Create the server instance
final_server = openServer('192.168.0.2', 'default_user', port=22)

# List the files in the home directory of the user on the server
file_list = doCommands(final_server, 'ls')

print(file_list)
```

If you want to execute more than one command at one, just add them in the arguments of the function, e.g.

```python
file_list = doCommands(final_server, 'ls', 'df -h', 'scancel 12345678')
```

#### Connect through a tunnel

It can be sometimes required to tunnel through a first server to reach the server of interest. This can be done
by defining several instances of the *Server* class and adding the tunnel ones to their respective destination.

```python
from HPyMon import *

tunnel_server = openServer('192.168.0.1', 'default_user', port=22)
final_server = openServer('192.168.0.2', 'default_user', tunnel=tunnel_server)
```

### Interact with the running jobs

#### Fetch the list of jobs currently running

The main design of H-PyMon is to fetch the jobs running on a **high-performance center** and display the list
without having to connect on the server via the Terminal and SSH. This is done by using the **getJobs()** function.

```python
from HPyMon import *

# Create the server instance
final_server = openServer('192.168.0.2', 'default_user', port=22)

# Get the list of the jobs currently running
job_list = getJobs(final_server)

print(job_list)
```

The list of jobs returned is contained in a Pandas Data Frame table-like structure.

This function assumes that (1) the HPC is using Slurm to schedule the jobs, and (2) that the jobs have been submitted
by the same username connecting to the server in the **openServer()** function. This can be modified using respectively
the arguments *command=* and *username=*.

```python
job_list = getJobs(final_server, command='squeue -o %all -u', username='other_user')
```

Since the function will concatenate the strings for *command=* and *username=*, it is essential to keep the username at the end of
of the expected command and not specify it in the command, e.g. avoid "squeue -u other_user -o %all" as the resulting command
send to the server will be "squeue -u other_user -o %all other_user".

One way to circumvent this issue, is to set ```username=""``` (empty string).

#### Kill running job(s)

Jobs can be directly cancelled on the server by specifying their ID in the scheduler. This is done
using the function **cancelJobs()**.

Similarly to *doCommands()*, multiple job IDs can be passed in the argument of the function.

```python
from HPyMon import *

# Create the server instance
final_server = openServer('192.168.0.2', 'default_user', port=22)

# Get the list of the jobs currently running
cancelJobs(final_server, 12345678, 12345679)
```

### Select and sort jobs
