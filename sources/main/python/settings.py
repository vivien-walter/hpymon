from appdirs import AppDirs
import configparser
import os

##-\-\-\-\-\-\-\-\-\
## PRIVATE FUNCTIONS
##-/-/-/-/-/-/-/-/-/

# ---------------------------------------
# Return the default folder of the system
def _return_default_folder():

    # Search the default directory of the system
    default_directory = AppDirs('HPyMon', 'configs', version="1.0")
    default_directory = default_directory.user_data_dir

    return default_directory

# ----------------------------------
# Return the path to the config file
def _return_config_path(file_name='config.ini'):

    # Get the path to the config file
    default_directory = _return_default_folder()
    file_path = os.path.join(default_directory, file_name)

    return file_path

# -------------------------
# Create the default folder
def _init_folder(file_path):

    # Create all the directories if needed
    try:
        os.makedirs(os.path.dirname(file_path))

    # Guard against race condition
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise

# -----------------------------------------------
# Initialise the config file if it does not exist
def _init_default_config(file_path, add_default_user=True):

    # Initialise the init parser
    config = configparser.RawConfigParser()

    # Get the first information in the init file
    if add_default_user:
        config['USER'] = {
        'username':'default',
        'use_key':True,
        'path_key':'~/.ssh/id_rsa',
        'dark_theme':False,
        'autostart':True,
        'autorefresh':True,
        'refresh_time':30,
        'get_jobs':'squeue -o %all -u',
        'kill_jobs':'scancel',
        'kill_col': 'JOBID'
        }

    # Check if the folders exist
    if not os.path.exists(os.path.dirname(file_path)):
        _init_folder(file_path)

    # Save the file
    with open(file_path, 'w') as configfile:
        config.write(configfile)

# --------------------
# Open the config file
def _open_config_file(file_name='config.ini', add_default_user=True):

    # Get the path to the config file
    file_path = _return_config_path(file_name=file_name)

    # Initialise the config file if it does not exist
    if not os.path.exists(file_path):
        _init_default_config(file_path=file_path, add_default_user=add_default_user)

    # Load the content of the file
    config = configparser.RawConfigParser()
    config.read(file_path)

    return config

# ------------------------------------------
# Convert a config content into a dictionary
def _config2dict(configs):

    # Process all sections
    conf_dict = {}
    for section in configs.sections():

        # Initialise the section dictionary
        conf_dict[section] = {}

        # Process all subsections
        for subsection in configs[section]:
            conf_dict[section][subsection] = configs[section][subsection]

    return conf_dict

# --------------------------------------------
# Check if the server is already in the config
def _is_server_in_file(server_name, config):

    # Check if it exists
    if server_name in config.sections():
        return True, config[server_name]['address']
    else:
        return False, None

# ---------------------------------------------
# Add the information of the server in the file
def _add_server(server, config, file_name='config.ini'):

    # Check the tunnel
    if server.tunnel is None:
        tunnel_text = 'None'
    else:
        tunnel_text = str(server.tunnel.name)

    # Add the server
    config[server.name] = {
    'address':server.ip,
    'port':server.port,
    'user':server.username,
    'id_type':server.identification['type'],
    'id_key':server.identification['key'],
    'use_display':server.use_display,
    'display_name':server.display_name,
    'tunnel':tunnel_text,
    'read_jobs':server.read,
    'query_name':server.queryname,
    'get_jobs':server.get_jobs,
    'kill_jobs':server.kill_jobs,
    'kill_col': server.kill_col
    }

    # Get the path to the config file
    file_path = _return_config_path(file_name=file_name)

    # Save the file
    with open(file_path, 'w') as configfile:
        config.write(configfile)

# -------------------------------------
# Replace the user settings in the file
def _replace_settings(settings, config, file_name='config.ini'):

    # Replace
    config['USER'] = {
    'username':settings['username'],
    'use_key':settings['use_key'],
    'path_key':settings['path_key'],
    'dark_theme':settings['dark_theme'],
    'autostart':settings['autostart'],
    'autorefresh':settings['autorefresh'],
    'refresh_time':settings['refresh_time'],
    'get_jobs':settings['get_jobs'],
    'kill_jobs':settings['kill_jobs'],
    'kill_col': 'JOBID'
    }

    # Get the path to the config file
    file_path = _return_config_path(file_name=file_name)

    # Save the file
    with open(file_path, 'w') as configfile:
        config.write(configfile)

# --------------------------------------------
# Check if the server is already in the config
def _is_display_in_file(display_name, config):
    return display_name in config.sections()

# ----------------------------------------------
# Add the information of the display in the file
def _add_display(display, config, file_name='display_config.ini'):

    # Add the display
    config[display.name] = {
    'display_type':display.display_type,
    'subdisplay_name':'---'
    }

    # Add information on a column selection
    if 'column' in display.display_type:
        config[display.name]['column_names'] = str(display.columns)

    # Add information on a custom display
    if 'selection' in display.display_type:

        # Add the name of the column
        config[display.name]['column_selection'] = display.selection.column
        config[display.name]['use_path'] = str(display.selection.use_path)
        config[display.name]['separator'] = str(display.selection.separator)

        # Add all the selection conditions
        if len(display.selection.conditions) == 0:
            config[display.name]['conditions'] = 'None'
        else:
            for index, condition_list in display.selection.conditions:
                config[display.name]['conditions_'+str(index)] = str(condition_list)

        # Add all the selection sorting conditions
        if len(display.selection.sorting['columns']) == 0:
            config[display.name]['sorting'] = 'None'
        else:
            for position, (index, condition_list) in enumerate( zip(display.selection.sorting['columns'], display.selection.sorting['names']) ):
                config[display.name]['sorting_'+str(index)] = str([position, condition_list])

        # Add column selection
        if 'selection_column' in display.display_type:
            config[display.name]['subdisplay_name'] = display.subdisplay_name

    # Get the path to the config file
    file_path = _return_config_path(file_name=file_name)

    # Save the file
    with open(file_path, 'w') as configfile:
        config.write(configfile)

##-\-\-\-\-\-\-\-\
## SERVER FUNCTIONS
##-/-/-/-/-/-/-/-/

# --------------------------------------------------
# Check if it is the first time the software is used
def checkFirstUse(file_name='config.ini'):

    """ Check if the software is being used for the first time.
    Argument(s):
        - file_name { str } - (Opt.) Name of the config file to edit.
                              Default is config.ini.
    """

    # Get the path to the config file
    file_path = _return_config_path(file_name=file_name)

    # Return whether it is the first time or not
    return not os.path.exists(file_path)

# ---------------------------
# Load the configuration file
def loadConfig(file_name='config.ini'):

    """ Load the content of the configuration file.
    Argument(s):
        - file_name { str } - (Opt.) Name of the config file to edit.
                              Default is config.ini.
    """

    # Get the content
    config = _open_config_file(file_name=file_name)

    # Convert the content into a dict
    conf_dict = _config2dict(config)

    # UPDATE -------------------
    # --------------------------

    # Check if new settings are missing
    if 'autostart' not in conf_dict['USER'].keys():
        conf_dict['USER']['autostart'] = 'False'
        conf_dict['USER']['autorefresh'] = 'False'
        conf_dict['USER']['refresh_time'] = '30'

    # --------------------------

    return conf_dict

# -----------------------------------------
# Edit the user settings in the config file
def editUser(settings, file_name='config.ini'):

    """ Edit the user settings in the config file.
    Argument(s):
        - settings { dict } - Settings to save in the file.
        - file_name { str } - (Opt.) Name of the config file to edit.
                              Default is config.ini.
    """

    # Get the content
    config = _open_config_file(file_name=file_name)

    # Replace the settings in the file
    _replace_settings(settings, config, file_name=file_name)

# -------------------------------
# Add a server to the config file
def addServer(server, file_name='config.ini', replace=True):

    """ Add a server in the config file.
    Argument(s):
        - server { Server class } - Instance of the server class to save in the config file.
        - file_name { str } - (Opt.) Name of the config file to edit.
                              Default is config.ini.
        - replace { bool } - (Opt.) Replace the existing server in the config file if it exists.
                             Default is True.
    """

    # Get the content
    config = _open_config_file(file_name=file_name)

    # Check if the server is already in the config
    in_file, prev_name = _is_server_in_file(server.ip, config)

    # Add only if the conditions are met
    if not in_file or replace:
        _add_server(server, config, file_name=file_name)

# --------------------------------------------
# Check if the server is already in the config
def serverExists(server, file_name='config.ini'):

    """ Check if the server is already in the database.
    Argument(s):
        - server { Server class } - Instance of the server class to check in the config file.
        - file_name { str } - (Opt.) Name of the config file to edit.
                              Default is config.ini.
    Output(s):
        - in_file { bool } - Is the server in the file?
        - prev_ip { str } - Address of the previous server if already exists in the file
    """

    # Get the content
    config = _open_config_file(file_name=file_name)

    # Check if the server is already in the config
    in_file, prev_ip = _is_server_in_file(server.name, config)

    return in_file, prev_ip

# ------------------------------------
# Load the server from the config file
def loadServer(server_identification, use_name=False, file_name='config.ini'):

    """ Load the server from the database.
    Argument(s):
        - server_identification { str } - Identification to load the server from the config file.
        - use_name { bool } - (Opt.) Use the name of the server instead of the address.
                              Default is False.
        - file_name { str } - (Opt.) Name of the config file to edit.
                              Default is config.ini.
    Output(s):
        - opened_server { dict } - Dictionary of the selected server.
    """

    # Get the content
    config = loadConfig(file_name=file_name)
    del config['USER']

    # Get the server from name
    opened_server = {}
    for server_name in config.keys():

        # Get from name
        if not use_name and config[server_name]['address'] == server_identification:
            opened_server = config[server_name]
            opened_server['name'] = server_name

        elif use_name and server_name == server_identification:
            opened_server = config[server_name]
            opened_server['name'] = server_name

    # UPDATE -------------------
    # --------------------------

    # Check if new settings are missing
    if 'use_display' not in opened_server.keys():
        opened_server['use_display'] = False
        opened_server['display_name'] = '---'

    # --------------------------

    return opened_server

# ------------------------------------
# Remove a server from the config file
def removeServer(server_ip, file_name='config.ini'):

    """ Remove a server from the config file.
    Argument(s):
        - server { Server class } - Instance of the server class to save in the config file.
        - file_name { str } - (Opt.) Name of the config file to edit.
                              Default is config.ini.
    """

    # Get the content
    config = _open_config_file(file_name=file_name)

    # Check if the server is already in the config
    in_file, prev_name = _is_server_in_file(server_ip, config)

    if in_file:

        # Remove the server if it exists
        config.remove_section(server_ip)

        # Get the path to the config file
        file_path = _return_config_path(file_name=file_name)

        # Save the file
        with open(file_path, 'w') as configfile:
            config.write(configfile)

##-\-\-\-\-\-\-\-\-\-\-\-\
## CUSTOM DISPLAY FUNCTIONS
##-/-/-/-/-/-/-/-/-/-/-/-/

# --------------------------------
# Add a display to the config file
def addDisplay(display, file_name='display_config.ini', replace=True):

    """ Add a custom display setting in the config file.
    Argument(s):
        - display { CustomDisplay class } - Instance of the class to save in the config file.
        - file_name { str } - (Opt.) Name of the config file to edit.
                              Default is display_config.ini.
        - replace { bool } - (Opt.) Replace the existing display in the config file if it exists.
                             Default is True.
    """

    # Get the content
    config = _open_config_file(file_name=file_name, add_default_user=False)

    # Check if the server is already in the config
    in_file = _is_display_in_file(display.name, config)

    # Add only if the conditions are met
    if not in_file or replace:
        _add_display(display, config, file_name=file_name)

# ---------------------------------------------
# Check if the display is already in the config
def displayExists(display, file_name='display_config.ini'):

    """ Check if the display is already in the database.
    Argument(s):
        - display { CustomDisplay class } - Instance of the CustomDisplay class to check in the config file.
        - file_name { str } - (Opt.) Name of the config file to edit.
                              Default is display_config.ini.
    Output(s):
        - in_file { bool } - Is the server in the file?
    """

    # Get the content
    config = _open_config_file(file_name=file_name)

    # Check if the server is already in the config
    in_file = _is_display_in_file(display.name, config)

    return in_file

# -------------------------------
# Get the list of custom displays
def getDisplayList(file_name='display_config.ini', column_only=False):

    """ Get the list of custom displays
    Argument(s):
        - file_name { str } - (Opt.) Name of the config file to edit.
                              Default is display_config.ini.
        - column_only { bool } - (Opt.) Only return custom column selections.
                                 Default is False.
    Output(s):
        - display_list { list of str } - List of the custom displays.
    """

    # Get the content
    config = _open_config_file(file_name=file_name)

    # Convert in a directory
    display_dict = _config2dict(config)

    # Get the display list
    display_list = [x for x in list(display_dict.keys()) if x != "USER"]

    # Refine the list
    if column_only:
        display_list = [x for x in display_list if display_dict[x]['display_type'] == "column"]

    return display_list

# -------------------------------
# Get the list of custom displays
def getDisplayNameTypeList(file_name='display_config.ini'):

    """ Get the list of custom displays
    Argument(s):
        - file_name { str } - (Opt.) Name of the config file to edit.
                              Default is display_config.ini.
    Output(s):
        - display_list { list of str } - List of the custom displays names.
        - display_types { list of str } - List of the custom displays types.
    """

    # Get the content
    config = _open_config_file(file_name=file_name)

    # Convert in a directory
    display_dict = _config2dict(config)

    # Get the display list
    display_list = [x for x in list(display_dict.keys()) if x != "USER"]

    # Get the types
    display_types = [display_dict[x]['display_type'] for x in display_list]

    return display_list, display_types

# -------------------------------------
# Load the custom display from the file
def loadDisplay(display_name, file_name='display_config.ini'):

    """ Load the display from the database.
    Argument(s):
        - display_name { str } - Name of the display to load from the config file.
        - file_name { str } - (Opt.) Name of the config file to load.
                              Default is display_config.ini.
    Output(s):
        - loaded_display { dict } - Dictionary of the selected display.
    """

    # Get the content
    config = loadConfig(file_name=file_name)

    # Get the display
    loaded_display = config[display_name]

    # Add the name
    loaded_display['name'] = display_name

    return loaded_display

# -------------------------------------
# Remove a display from the config file
def removeDisplay(display_name, file_name='display_config.ini'):

    """ Remove a custom display from the config file.
    Argument(s):
        - display_name { str } - Name of the display to remove from the file.
        - file_name { str } - (Opt.) Name of the config file to edit.
                              Default is display_config.ini.
    """

    # Get the content
    config = _open_config_file(file_name=file_name)

    # Check if the display is already in the config
    if _is_display_in_file(display_name, config):

        # Remove the server if it exists
        config.remove_section(display_name)

        # Get the path to the config file
        file_path = _return_config_path(file_name=file_name)

        # Save the file
        with open(file_path, 'w') as configfile:
            config.write(configfile)
