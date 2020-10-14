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

* fbs==0.9.0
* PyQt5==5.9.2
* numpy==1.19.2
* pandas==1.1.3
* paramiko==2.7.2
* sshtunnel==0.1.5
* appdirs==1.4.4
* keyring==21.4.0

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
