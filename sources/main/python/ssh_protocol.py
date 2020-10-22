import keyring
from paramiko import SSHClient, AutoAddPolicy
from sshtunnel import SSHTunnelForwarder

from settings import loadServer

##-\-\-\-\-\-\
## SERVER CLASS
##-/-/-/-/-/-/

# Define the server class
class Server:
    def __init__(self, name, ip_address, username, identification={'type':'publickey', 'key':'~/.ssh/id_rsa'}, port=22, tunnel=None, read=True, commands={'get_jobs':'squeue -o %all -u', 'kill_jobs':'scancel'}, queryname=None, kill_col='JOBID', display={'use_display':True, 'display_name':'---'}):

        # Get the server info
        self.name = name
        self.ip = ip_address
        self.port = port
        self.read = read

        # Get the authentification info
        self.username = username
        if identification['type'] == 'publickey':
            self.identification = identification
        else:
            self.getPassword(identification['key'])

        # Get the tunnel if required
        self.tunnel = tunnel

        # Get the name for job query
        if queryname is None:
            self.queryname = username
        else:
            self.queryname = queryname

        # Get the custom commands
        self.get_jobs = commands['get_jobs']
        self.kill_jobs = commands['kill_jobs']
        self.kill_col = kill_col

        # Get the custom display
        self.use_display = display['use_display']
        self.display_name = display['display_name']

    ##-\-\-\-\-\-\-\-\-\-\
    ## ACCESS INFORMATIONS
    ##-/-/-/-/-/-/-/-/-/-/

    # -----------------------
    # Set the password to use
    def setPassword(self, key):

        # Prepare the keyring identification
        keyring_id = self.name + '_' + self.ip + '_' + self.username

        # Get the password from input
        keyring.set_password('hpymon',keyring_id,key)

        # Prepare the ID infos
        self.identification = {
        'type': 'password',
        'key': 'crypted'
        }

    # ----------------
    # Get the password
    def getPassword(self, key):

        # Get the password from input
        password = keyring.get_password('hpymon',key)

        # Check if the password exists
        if password is None:
            self.setPassword(key)
            return None

        # Return the password
        else:
            return password

##-\-\-\-\-\-\-\-\-\
## PRIVATE FUNCTIONS
##-/-/-/-/-/-/-/-/-/

# -----------------------------------------
# Connect to a server and execute a command
def _connect_and_execute(ip, port, username, identification, *commands, output=True):

    # Get the ID details
    id_type = identification['type']
    id_key = identification['key']

    # Open the SSH client
    client = SSHClient()

    # Load the key from the system
    client.load_system_host_keys()

    # Connect with a public key
    if id_type == 'publickey':
        client.set_missing_host_key_policy(AutoAddPolicy())

        # Connect the to server
        client.connect(ip, port, username=username)

    # Connect with a password
    else:
        client.connect(ip, username=username, port=port, password=id_key)

    # Prepare the commands
    if not isinstance(output, list):
        output = [output] * len(commands)

    # Send all the commands
    all_output = []
    for i, cmd in enumerate(commands):

        # Execute the command
        stdin, stdout, stderr = client.exec_command(cmd)

        # Store the output
        if output[i]:
            all_output.append(stdout.read().decode("utf8"))
        stdout.close()

    # Return the result
    if len(all_output) == 0:
        all_output = None

    # Close the client
    client.close()

    return all_output

# ----------------
# Do the tunneling
def _tunneling(tunnel_list, *commands, output=True, tunnel_id=0):

    # Get the first server on the list
    crt_tunnel = tunnel_list[0]
    next_tunnel = tunnel_list[1]

    # Get the ID details
    id_type = crt_tunnel.identification['type']
    id_key = crt_tunnel.identification['key']

    # Define the information on the next step
    next_ip = '0.0.0.'+str(tunnel_id)

    # Start the tunnel with public key
    if id_type == 'publickey':
        with SSHTunnelForwarder (
            (crt_tunnel.ip, crt_tunnel.port),

            # Connection info
            ssh_username=crt_tunnel.username,
            ssh_pkey=id_key,

            # Next step info
            remote_bind_address=(next_tunnel.ip, next_tunnel.port),
            local_bind_address=(next_ip, 10022)
        ) as tunnel:

            # Move to the next tunnel if needed
            if len(tunnel_list) > 2:
                outputs = _tunneling(tunnel_list[1:], *commands, output=output, tunnel_id=tunnel_id+1)

            else:
                outputs = _connect_and_execute(next_ip, 10022, next_tunnel.username, next_tunnel.identification, *commands, output=output)

    # Start the tunnel with password
    else:
        with SSHTunnelForwarder (
            (crt_tunnel.ip, crt_tunnel.port),

            # Connection info
            ssh_username=crt_tunnel.username,
            ssh_password=id_key,

            # Next step info
            remote_bind_address=(next_tunnel.ip, next_tunnel.port),
            local_bind_address=(next_ip, 10022)
        ) as tunnel:

            # Move to the next tunnel if needed
            if len(tunnel_list) > 2:
                outputs = _tunneling(tunnel_list[1:], *commands, output=output, tunnel_id=tunnel_id+1)

            else:

                # Connect with a public key
                if next_tunnel.identification['type'] == 'publickey':
                    identification = next_tunnel.identification

                # Connect with a password
                else:
                    identification = {
                    'type': next_tunnel.identification['type'],
                    'key': next_tunnel.getPassword( next_tunnel.identification['key'] )
                    }

                outputs = _connect_and_execute(next_ip, 10022, next_tunnel.username, identification, *commands, output=output)

    return outputs

# ----------------------
# Use a tunnel if needed
def _get_tunnel_chain(server_class, *commands, output=True):

    # Get the informations on the tunnel
    crt_tunnel = server_class
    tunnel_servers = [crt_tunnel]

    # Check the chain
    read_tunnels = True
    while read_tunnels:

        # Get the next tunnel in the chain =
        if crt_tunnel.tunnel is not None:
            crt_tunnel = crt_tunnel.tunnel
            tunnel_servers.append(crt_tunnel)

        # Exit the loop
        else:
            read_tunnels = False

    # Start the tunneling
    outputs = _tunneling(tunnel_servers[::-1], *commands, output=output)

    return outputs

# --------------------------
# Format the dictionary from
def _format_dictionary(server_dict):

    # Format the dictionary
    server_details = {
    'name':server_dict['name'],
    'address':server_dict['address'],
    'port':server_dict['port'],
    'username':server_dict['user'],
    'use_key': server_dict['id_type'] == 'publickey',
    'path_key': server_dict['id_key'],
    'read_jobs':server_dict['read_jobs'] == 'True',
    'use_display':server_dict['use_display'] == 'True',
    'display_name': server_dict['display_name'],
    'use_tunnel':False,
    'tunnel_selection': None,
    'queryname': server_dict['query_name'],
    'get_jobs': server_dict['get_jobs'],
    'kill_jobs': server_dict['kill_jobs'],
    'kill_col': server_dict['kill_col']
    }

    # Add the tunnel
    if server_dict['tunnel'] != 'None':
        server_details['use_tunnel'] = True
        server_details['tunnel_selection'] = server_dict['tunnel']

    return server_details

##-\-\-\-\-\-\-\-\
## PUBLIC FUNCTIONS
##-/-/-/-/-/-/-/-/

# -------------------------------------------
# Generate a server from the details provided
def generateServer(server_details):

    """ Create the server
    Argument(s):
        - server_details { dict } - Dictionary of the details used to create the instance of the Server class.
    Output(s):
        - server_class { Server class } - Instance of the Server class to send the commands to.
    """

    # UPDATE -------------------
    # --------------------------

    # Check if new settings are missing
    if 'use_display' not in server_details.keys():
        server_details['use_display'] = False
        server_details['display_name'] = '---'

    # --------------------------

    # Load the tunnel if needed
    if server_details['use_tunnel']:
        tunnel = openServer(server_details['tunnel_selection'], use_name=True)
    else:
        tunnel = None

    # Set the identification method
    id_method = {
    'type':'password',
    'key':server_details['path_key']
    }
    if server_details['use_key']:
        id_method['type'] = 'publickey'

    # Set the job commands
    job_commands = {
    'get_jobs':server_details['get_jobs'],
    'kill_jobs':server_details['kill_jobs']
    }

    # Set the custom display
    display_details = {
    'use_display':server_details['use_display'],
    'display_name':server_details['display_name']
    }

    # Generate the server instance
    new_server_class = Server(
    server_details['name'],
    server_details['address'],
    server_details['username'],
    port=int(server_details['port']),
    identification=id_method,
    tunnel=tunnel,
    read=server_details['read_jobs'],
    commands=job_commands,
    queryname=server_details['queryname'],
    kill_col=server_details['kill_col'],
    display=display_details
    )

    return new_server_class

# -----------------------------------------
# Open a server class from the setting file
def openServer(server_identification, use_name=True):

    """ Check if the server is already in the database.
    Argument(s):
        - server_identification { str } - Identification to find the server in the config file.
        - use_name { bool } - (Opt.) Use the name of the server instead of the address.
                              Default is False.
    Output(s):
        - server_class { Server class } - Instance of the Server class to send the commands to.
    """

    # Get the dictionary
    server_dict = loadServer(server_identification, use_name=use_name)

    # Format the dictionary
    server_details = _format_dictionary(server_dict)

    # Get the tunnel from the details
    server_class = generateServer(server_details)

    return server_class

# --------------------------
# Send command to the server
def sendCommands(server_class, *commands, output=True):

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

    # Connect directly
    if server_class.tunnel is None:

        # Connect with a public key
        if server_class.identification['type'] == 'publickey':
            identification = server_class.identification

        # Connect with a password
        else:
            identification = {
            'type': server_class.identification['type'],
            'key': server_class.getPassword( server_class.identification['key'] )
            }

        outputs = _connect_and_execute(server_class.ip, server_class.port, server_class.username, identification, *commands, output=output)


    # Tunnel through other servers
    else:
        outputs = _get_tunnel_chain(server_class, *commands, output=True)

    return outputs

# --------------------------------
# Check if the server is connected
def checkConnection(server_class):

    """ Send a list of commands in a server
    Argument(s):
        - server_class { Server class } - Instance of the server class to send the commands to.
    """

    # Check the connection
    try:
        sendCommands(server_class, 'ls', output=True)
        return True

    # Return false if failed
    except:
        return False
