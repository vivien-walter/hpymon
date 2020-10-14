# HPyMon

![HPyMon logo](https://github.com/vivien-walter/hpymon/blob/main/sources/main/icons/linux/256.png)

![version](https://img.shields.io/badge/version-beta-f39f37)

HPyMon is a Python-based GUI software made to display the job running on a distant HPC.

## Description

### General Information

**Current Version:** beta

**Release Data:** 14-10-2020

**Author:** Vivien Walter

**Contact:** https://vivien-walter.github.io

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

## Installation

### Using the executable

The easiest way to use HPyMon is by downloading the executable and using it on your computer.
All the executables available can be found in **/executables/** folder inside their respective .zip archives.

The (new) executables will be uploaded as soon as they are generated.

**Executable(s) available:**

* **MacOSX High Sierra** (10.13) and above (uploaded: 14/10/2020)

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

![User settings - Basic tab](https://github.com/vivien-walter/hpymon/blob/main/sources/main/resources/base/help/user_2.png)

An *advanced settings* tab is also available, with the following inputs:

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
