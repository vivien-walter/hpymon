from paramiko import SSHClient, AutoAddPolicy
from sshtunnel import SSHTunnelForwarder

##-\-\-\-\-\-\
## SERVER CLASS
##-/-/-/-/-/-/

# Define the server class
class Server:
    def __init__(self, ip_address, username, identification={'type':'publickey', 'key':'~/.ssh/id_rsa'}, port=22, tunnel=None):

        # Get the server info
        self.ip = ip_address
        self.port = port

        # Get the authentification info
        self.username = username
        self.identification = identification

        # Get the tunnel if required
        self.tunnel = tunnel

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
                outputs = _connect_and_execute(next_ip, 10022, next_tunnel.username, next_tunnel.identification, *commands, output=output)

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

##-\-\-\-\-\-\-\-\
## PUBLIC FUNCTIONS
##-/-/-/-/-/-/-/-/

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
        outputs = _connect_and_execute(server_class.ip, server_class.port, server_class.username, server_class.identification, *commands, output=output)

    # Tunnel through other servers
    else:
        outputs = _get_tunnel_chain(server_class, *commands, output=True)

    return outputs
