# HPyMon

![HPyMon logo](https://github.com/vivien-walter/hpymon/blob/main/sources/main/icons/linux/256.png)

![version](https://img.shields.io/badge/version-1.0.1-f39f37)

HPyMon (HPC Python Monitor) is a Python-based GUI software made to display the job running on a distant HPC.

![Main window](https://github.com/vivien-walter/hpymon/blob/main/sources/main/resources/base/help/main.png)

## Description

### General Information

**Current Version:** 1.0.1

**Release Data:** 23-10-2020

**Author:** Vivien Walter

**Contact:** https://vivien-walter.github.io

HPyMon is relying on **PyQt5** for its graphical user interface (GUI). All other packages, libraries and modules used by
HPyMon are listed in the *Requirements* list below.

### Requirements

The following libraries and modules are required to run HPyMon. If you are using the executable,
the modules are pre-installed inside the executable and no further action is required.

* fbs == 0.9.0
* PyQt5 == 5.9.2
* numpy == 1.19.2
* pandas == 1.1.3
* paramiko == 2.7.2
* sshtunnel == 0.1.5
* appdirs == 1.4.4
* keyring == 21.4.0

*Note: newer or older version(s) of the modules could work, but the author only tested those.*

## Table of Contents

* [Installation](#installation)
    * [Using the executable](#using-the-executable)
    * [Compile from source](#compile-from-source)
    * [Use the library](#use-the-library)
* [How-To Use HPyMon](#how-to-use-hpymon)
    * [User Settings](#user-settings)
    * [Server Settings](#server-settings)
    * [Connection to a server](#connection-to-a-server)
    * [Job list display](#job-list-display)
    * [Custom display creation](#custom-display-creation)
    * [Custom display management](#custom-display-management)
* [Troubleshooting](#troubleshooting)

## Installation

### Using the executable

The easiest way to use HPyMon is by downloading the executable and using it on your computer.
All the executables available can be found in **/executables/** folder inside their respective .zip archives.

The (new) executables will be uploaded as soon as they are generated.

**Executable(s) available:**

* **MacOSX High Sierra** (10.13) and above (uploaded: 22/10/2020)

### Compile from source

If your Operating System is not available in the provided executables, it is possible for you
to use HPyMon by downloading the source file and compiling them into an executable yourself.

The [instructions](https://github.com/vivien-walter/hpymon/blob/main/sources/README.md) along with the source files are given in the **/sources/** folder of the repo.

### Use the library

The main functions of the software are available to use as a standalone Python library. The library is available on a different branch of the GitHub repo, [library_only](https://github.com/vivien-walter/hpymon/tree/library_only).

## How-To Use HPyMon

Below are described the main features of HPyMon and how to use them.

### User Settings

During your first connection to HPyMon, you will be invited to input your **user settings**. These information will be used to define the default settings of each new server you will create.
This information are only here to save you time when setting a server, and they can all be changed while creating a server if needed.

![User settings - Basic tab](https://github.com/vivien-walter/hpymon/blob/main/sources/main/resources/base/help/user_1.png)

The description of the different inputs are listed below:

* **User Name:** Default user name used to connect to the server. Will be used to pre-fill each new server settings when created.

* **Use public key?** HPyMon relies preferably on *public keys* to connect to the servers. By un-ticking this box, the default identification type will be set to *passphrase*.

    Instructions on how to create public keys can be found on the Internet, e.g. [here](https://www.ssh.com/ssh/keygen/). Please use the appropriate tutorial to your settings.

* **Path to key:** Absolute path to the file where the public keys are stored on your computer.

* **Use dark theme?** Set the graphic theme of HPyMon to dark. Changing the theme requires HPyMon to be restarted in order to be applied.

* **Auto-connect on start?** Tick this box to automatically connect to the servers in memory when HPyMon is started.

![User settings - Basic tab](https://github.com/vivien-walter/hpymon/blob/main/sources/main/resources/base/help/user_2.png)

An *advanced settings* tab is also available, with the following inputs:

* **Enable Auto-Refresh?** Tick this box to automatically periodically refresh the job status of all opened servers. The time between refresh is specified in the following entry.

* **Time between refresh (min)** Type the amount of minutes before refreshing the job status of all opened servers. Value can be a float (*e.g.* 1.5 minutes = 1 minutes and 30 seconds)

* **Get jobs:** Command to use on the HPC server to retrieve the list of jobs. The command is completed with the username, such as the command

    ```bash
    > squeue -o %all -u
    ```

    will be completed by HPyMon as

    ```bash
    > squeue -o %all -u username
    ```

* **Kill jobs:** Command to use on the HPC server to kill the selected jobs if requested. The identification of the jobs are retrieved using the input *Column for job IDs* set below.

* **Column for job IDs:** Column of the job list display table in HPyMon to use to get the job identifications and use them to kill the jobs on the server.

The user settings can be changed anytime, by going in the menu of HPyMon and selecting **Help/User Settings.**

### Server Settings

In order to connect to a server, you will have to create its settings and save them in the memory. This can be done in the menu **Servers/Add Server** of HPyMon - or by pressing the *Ctrl + N* (or *CMD + N* on MacOSX) keys.

The Server Settings window can also be used to Edit the settings after creation.

![Server settings - Connexion tab](https://github.com/vivien-walter/hpymon/blob/main/sources/main/resources/base/help/server_1.png)

This window have the following inputs:

* **Server Name:** Name of the server to display in HPyMon. Only useful for organisation purposes.
* **Read job from this server?** If this box is ticked, HPyMon will send a query to retrieve a list of jobs on this server. Unticking the box can be useful if the server is only used as a tunnel (see below).
* **Server Address:** Address of the server to connect to. Can be either an IP address or a standard address (e.g myservername.myuniversity.co.uk). You should use the same address as the one you use to connect on your HPC via Terminal.
* **Server Port:** Port of the server to connect to. You should use the same port as the one you use to connect on your HPC via Terminal.
* **Username:** Username used to connect on the server. You should use the same username as the one you use to connect on your HPC via Terminal.
* **Use a Public key/Password:** Selection of the type of identification to use on the server. See below.
* **Path to Key:** (*when Use a Public Key is selected*) Absolute path to the file where the public keys are stored on your computer.
* **Password:** (*when Use a Password is selected*) Password to use to connect on the server. *Note: the password is stored on the crypted keyring of the computer, not in the HPyMon files.*
* **Use custom display?** Tick this box to load the list of running jobs on the server with a custom display. Use the combo box to select the desired display to use.

![Server settings - Tunnel tab](https://github.com/vivien-walter/hpymon/blob/main/sources/main/resources/base/help/server_2.png)

To connect on some remote server, it might be critical to tunnel through another server. This can be set in HPyMon in the *tunnel* tab. This tab has the following inputs:

* **Use a tunnel?** Tick this box to use a tunnel to connect to this server.

* **Tunnel through:** Select the server to use as a tunnel to connect to this one. The tunnel server should be already saved in HPyMon memory in order to be used.

![Server settings - Advanced tab](https://github.com/vivien-walter/hpymon/blob/main/sources/main/resources/base/help/server_3.png)

Similarly to the User Settings, an *advanced settings* tab is available on the Server settings window.

* **Use same Username in job query?** When this box is ticked, the username used to connect to the server is used for the job query command. If unticked, the username used instead
will be the one specified in *Job query Username* below. This can be useful to check the status of the job of another user.

* **Job query Username:** Username to use for the job query.

* **Get jobs:** Command to use on the HPC server to retrieve the list of jobs. The command is completed with the username, such as the command

    ```bash
    > squeue -o %all -u
    ```

    will be completed by HPyMon as

    ```bash
    > squeue -o %all -u username
    ```

* **Kill jobs:** Command to use on the HPC server to kill the selected jobs if requested. The identification of the jobs are retrieved using the input *Column for job IDs* set below.

* **Column for job IDs:** Column of the job list display table in HPyMon to use to get the job identifications and use them to kill the jobs on the server.

### Connection to a server

Once the server(s) have been defined, you can connect to them using different ways:

* **Connect to a single server.** This can be done using the HPyMon menu and selecting **Servers/Connect to.../Select** - or alternatively the shortcut *Ctrl + Shift + O* (*CMD + Shift + O* on MacOS).
This will open a new window where you can select the server you want to connect to.

    ![Connect to a single server](https://github.com/vivien-walter/hpymon/blob/main/sources/main/resources/base/help/connection.png)

* **Connect to all servers at once.** To save time, you can decide to connect to all the servers stored in the memory - depending whether you have ticked the box *Read job from this server?* in the settings of course.
To do so, you have four options: (i) Enable **Autoconnect** in the User settings and start HPyMon, (ii) Using the **Connect** button on the front panel of HPyMon, (iii) Using the HPyMon menu and selecting **Servers/Connect to.../All** or (iv) using the shortcut *Ctrl + O* (*CMD + O* on MacOS).

    When the connection to all the servers is running, a popup window with a progress bar will appear to keep track of the progress of the network connection.

Before retrieving the jobs, HPyMon will briefly try to connect to the server, sending a basic useless command (i.e. *ls*). If the command cannot be passed, HPyMon will assume that the server cannot be reached and send
an error message. During multiple connection, HPyMon should proceed to the next server when one server crashes.

### Job list display

After connection to the server(s), the main display of HPyMon will be used to display the jobs running on the different servers. Each server will have its jobs displayed in its **own tab**.

![Main window](https://github.com/vivien-walter/hpymon/blob/main/sources/main/resources/base/help/main.png)

The job list and status is not constantly refreshed. To refresh the list, use the **Refresh** button which has replaced the *Connect* one. If you have ticked *Auto-Refresh* in the User settings, the job list will refresh automatically. 
*Note: This button will only refresh the list of the server/tab currently selected.*

Two types of interactions can be made with the display:

* **Use custom display?** By default, all the columns returned by the *squeue* command (in *Slurm*) will be displayed - which can be too much sometimes. After ticking this box, the desired custom display should be selected in the Combo box next to it.

* **Contextual menu.** Right click on any row of the job list table will display a contextual menu, with several options to interact with the selected job(s).

    ![Contextual menu](https://github.com/vivien-walter/hpymon/blob/main/sources/main/resources/base/help/context_menu.png)

    * **Kill Job** will send a command to the server to cancel this specific job. An alert will ask the user to confirm its choice, but once the cancellation has been confirmed this operation cannot be undone.
* **Select Columns** (*If no custom display has been selected*). This will open a new window to create a column selection of the job list. See below for more information.
  
    * **Define Custom Display** (*If no custom display has been selected*). This will open a new window to create a custom display of the job list. See below for more information.
* **Edit Current Display** (*If a custom display has been selected*). This will open a new window to edit the current selected custom display of the job list. See below for more information.

### Custom display creation

Custom display of the job list can be created using the *contextual menu* of the main job list display (see above), or alternatively the HPyMon menu by selecting
**Job Display/New Column Selection **or **Job Display/New Custom Display**. This will open a new window to create the new custom display of the appropriate format.

#### Column Selection

The first available type of custom display is named *Column Selection*. This help refining the column being displayed in the main interface by only selecting a list of them.

![Column Selection creation](https://github.com/vivien-walter/hpymon/blob/main/sources/main/resources/base/help/column_selection.png)

*Note: Connection to at least one server is required to open the custom display creation window, as HPyMon will retrieve the list of columns from the server.*

To keep a column in the custom display, just **tick the corresponding checkbox** next to it. Give the custom display a name in the **Selection Name** entry field to find it later.
When you are done, just click on the **Save** button.

Once the custom display has been created, you can select it in the combo box of the main panel of HPyMon to refine the job list display.

#### Selecting and Sorting jobs

The second available type of custom display, simply named *Custom Display*, will select and sort jobs based on the given user selection.

![Custom display creation](https://github.com/vivien-walter/hpymon/blob/main/sources/main/resources/base/help/custom_display.png)

*Note: Connection to at least one server is required to open the custom display creation window, as HPyMon will retrieve the list of columns from the server.*

The custom display will look at one of the columns from the job list, usually the *WORK_DIR* column that gather the list of the folders in which the simulation is stored, and generate a list of elements from it.

For example, if the folder path ressembles

```shell
>>> /username/molecule/concentration/temperature/
```

HPyMon will extract 4 elements from it: (1) username, (2) molecule, (3) concentration and (4) temperature. The user can then select which element should be used to select and/or sort the job to refine the display.

When creating the display, the following options can be selected:

* **Column for the custom display.** Name of the column (extracted in the job list) to use to set the pattern to use to select and sort the jobs.
* **Column is a path?** This box is ticked by default, as HPyMon has been designed to use the content of the column WORK_DIR on slurm. By unticking this box, a separator can be picked instead.
* **Separator to use.** Specify the separator to use in the column to sort the elements.
* **Use Column selection?** Add a specific column selection display to this custom display. To chose from the list of Column selection displays already in the memory.

The displayed table in the window corresponds to all the elements found. Each of the elements can be picked to either **select** and or **sort** by the values found for these elements.

* **Sort by...** Using this option will sort all the jobs from the list based on the values of this element.

    * **Name** Generic name to display for this element (*e.g.* Concentration, Temperature, Llamas)
    * **Position** Relative position in the tree presentation of the jobs.

* **Select by...** Using this option will refine the jobs from the list by selecting only the jobs that have a value matching the one specified for this element.
* **Restrictions** List of the value(s) for the element to be kept for the job display. To use several values, separate each of them by a simple coma ,

A typical output will look like the following screenshot

![Custom display creation](https://github.com/vivien-walter/hpymon/blob/main/sources/main/resources/base/help/display_example.png)

### Custom display management

To edit or delete existing custom display, you can use the custom display manager of HPyMon. It can be accessed using the HPyMon menu by selecting **Job Display/Manage Custom Displays**.

![Custom display manager](https://github.com/vivien-walter/hpymon/blob/main/sources/main/resources/base/help/display_manager.png)

In this interface, similar to the server manager, you can chose to **Edit** or **Delete** any of the custom displays currently stored in HPyMon memory.

## Troubleshooting

The following note(s) should be taken into consideration while using HPyMon:

* HPyMon has only been tested on HPC servers managed using the **Slurm** scheduler. While it should be versatile enough to be used with other scheduler, they have not been tested and might require some adjustments.
