#!/usr/bin/python3
import glob
import subprocess
import json
import sys
import os
from datetime import datetime
from plugins.basics import State
from utils import get_json_or_empty_dict
from utils import get_oldest_timestamp
from utils import cd
from render_html import render_html


def collect_default_configs(plugins_config_path, plugins_path):
    """ Runs every file plugin_* in plugins_path with parameter --print_config 
        and stores the result in the json file plugins_config_path.

        Existing configs will not be overwritten.
    """
    # get existing config
    full_plugin_config = get_json_or_empty_dict(plugins_config_path)
    # iterate through plugins
    for plugin_path in glob.glob('{}/plugin_*'.format(plugins_path)):
        print('Collecting config from: {}'.format(plugin_path))
        # run plugins with --print_config
        plugins_config_string = subprocess.run(
            [plugin_path, '--print_config'], stdout=subprocess.PIPE).stdout.decode('utf-8')
        plugin_config = json.loads(plugins_config_string)
        # each plugin may yield multiple configs - iterate through them
        for config_line in plugin_config:
            if not config_line in full_plugin_config:
                full_plugin_config[config_line] = plugin_config[config_line]
    # save to plugin config file
    with open(plugins_config_path, 'w') as plugins_config_file:
        json.dump(full_plugin_config, plugins_config_file, indent=4)


def collect_data(plugins_config_path, data_path):
    """ Runs every plugin in the plugin config and saves the results in the data
        json file.

        Json files will be deleted after data was read from them. This is to 
        recognize new data.
    """
    full_plugin_config = get_json_or_empty_dict(plugins_config_path)
    all_data = get_json_or_empty_dict(data_path)
    time_now = datetime.now().timestamp()
    # iterate through all configured plugins
    for plugin_index, plugin_config in full_plugin_config.items():
        # if a plugin is configured but has no data, start with an empty dict
        if not plugin_index in all_data:
            all_data[plugin_index] = {}
        # if no sub dict 'data' exists, create one
        if not 'data' in all_data[plugin_index]:
            all_data[plugin_index]['data'] = {}
        # read from json file for manual_path plugins
        if 'manual_path' in plugin_config:
            print('Reading from {}'.format(plugin_config['manual_path']))
            data_dict = get_json_or_empty_dict(plugin_config['manual_path'])
            if(bool(data_dict)):
                all_data[plugin_index]['data'] = data_dict
                all_data[plugin_index]['last_check'] = time_now
                # delete file after reading, so new data will be recognized as new
                os.remove(plugin_config['manual_path'])
            else:
                print('File {} does not exist or is empty.'.format(
                    plugin_config['manual_path']))
        # read directly from output for normal plugin execution
        else:
            print('Calling {} {}'.format(
                plugin_config['command'], plugin_config['arguments']))
            data_string = subprocess.run(
                [plugin_config['command'], *plugin_config['arguments']], stdout=subprocess.PIPE).stdout.decode('utf-8')
            all_data[plugin_index]['data'] = json.loads(data_string)
            all_data[plugin_index]['last_check'] = time_now
        if 'state' in all_data[plugin_index]['data'] and all_data[plugin_index]['data']['state'] == State.OK.value:
            all_data[plugin_index]['last_ok'] = all_data[plugin_index]['last_check']
    # write data file
    with open(data_path, 'w') as data_file:
        json.dump(all_data, data_file, indent=4)


if __name__ == "__main__":
    # go to this directory, so we can use relative path names in config files
    with cd(os.path.dirname(sys.argv[0])):
        with open('config/config.json', 'r') as config_file:
            config = json.load(config_file)
        if "--configure_plugins" in sys.argv:
            collect_default_configs(
                config['plugins_config_path'], config['plugins_path'])
            exit(0)
        else:
            collect_data(config['plugins_config_path'],
                         config['data_path'])
            if not "--no_html" in sys.argv:
                render_html(config)
