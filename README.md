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

H-PyMon can be used to select specific jobs and sort them based on the path of their source directory - assuming that the
directories have been sorted initially.

For instance, let's take the following paths of different jobs:

```bash
>>> /user_name/lipids/DPPC/288K/
>>> /user_name/lipids/DPPC/358K/
>>> /user_name/lipids/DOPC/288K/
>>> /user_name/lipids/DSPC/288K/
>>> /user_name/proteins/KALP/
```

In this example, we can see that the source directories of the jobs can be sorted by type of molecule (lipids/proteins), molecule name (DPPC/DOPC for the lipids, KALP for the proteins) and, for the lipids only, by temperature (288K/358K). using H-PyMon we will see how the job list can be refined to only display a specific list of simulation.

#### The selection syntax

The selection of jobs in H-PyMon is made using a dictionary describing which elements of the path should be considered, and what for. To illustrate it, let us take the following path and split it in its different elements:

```
/user_name/lipids/DPPC/288K/
 (0)       (1)    (2)  (3)
```

The path here is made of 4 folder levels: (0) the user name, (1) the type of molecule, (2) the name of the molecule and (3) the temperature. These indices are essential as we need them to point which element should be used to select or sort the jobs.

The standard syntax for the dictionary is

```python
selection_dict = {
element_idx : ( sorting_name, [selection_values], sorting_position )
}
```

* The *element_idx* is the index of the element in the source directory path to use for sorting and/or selecting. E.g. to sort by temperature in the example above, *element_idx* should be equal to 3.
* The *sorting_name* is a string that can is used to display the category used to sort the jobs. It can be anything, even unrelated
to the names found in the folders (e.g. "Lipid name"). If the element is not used to sort but only select, use None here instead.
* The list of *[selection_values]* is an list of folder names that can be used to select only specific jobs. E.g. if we want to select
the jobs related to DSPC and DOPC lipids, the list should be ['DPPC','DSPC']. For only the DPPC, use then ['DPPC']. If the element is not used to select but only sort, use None here instead.
* The *sorting_position* is the position of the element in the tree structure obtained by sorting the jobs on several levels.
The value should be an integer going from 0 to inf. If the element is not used to sort, use -1 instead.

**Example(s):**

*All the follow examples are based on the bath given above*

* Select based on one element, here the type of molecule (select only 'lipids'):
    ```python
    selection_dict = {
    1 : ( None, ['lipids'], -1 )
    }
    ```

* Select based on two elements, here the type of molecule (select only 'lipids') and the molecule name (select only 'DPPC' and 'DSPC')
  ```python
  selection_dict = {
  1 : ( None, ['lipids'], -1 ),
  2 : ( None, ['DPPC', 'DSPC'], -1 )
  }
  ```

* Sort based on one element, here the name of the lipid
  ```python
  selection_dict = {
  2 : ( 'Lipid name', None, 0 ),
  }
  ```

* Sort based on two elements, here the name of the lipid and the temperature, but sort by the temperature first
  ```python
  selection_dict = {
  2 : ( 'Lipid name', None, 1 ),
  3 : ( 'Temperature', None, 0 )
  }
  ```

* Select based on one element and sort based on another element, here respectively the type of molecule and the temperature
  ```python
  selection_dict = {
  1 : ( None, ['lipids'], -1 ),
  3 : ( 'Temperature', None, 0 )
  }
  ```

* Select based on one element and sort while selecting based on another element, here respectively the type of molecule and the
molecule name
  ```python
  selection_dict = {
  1 : ( None, ['lipids'], -1 ),
  2 : ( 'Lipid name', ['DPPC', 'DSPC'], 0 )
  }
  ```

All combinations can be used.

#### The Selection class 
