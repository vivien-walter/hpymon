# H-PyMon

Python package to display the job running on a distant HPC

## Installation

1. Download the package
2. Open in a Terminal
3. Run the following command:
    ```sh
    > python3 setup.py install
    ```

## How to use

### Connect directly

```python
from HPyMon.ssh_protocol import Server
from HPyMon.get_jobs import getJobList

final_server = Server('192.168.0.2', 'default_user', port=22)

job_df = getJobList(final_server)

print(job_df)
```

### Connect through a tunnel

```python
from HPyMon.ssh_protocol import Server
from HPyMon.get_jobs import getJobList

tunnel_server = Server('192.168.0.1', 'default_user', port=22)
final_server = Server('192.168.0.2', 'default_user', tunnel=tunnel_server)

job_df = getJobList(final_server)

print(job_df)
```
