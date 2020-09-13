import os
import pathlib
import json
from datetime import datetime
from plugins.basics import State


class cd:
    '''Context manager for changing the current working directory.

    copied from https://stackoverflow.com/a/13197763

    Usage:
    with cd(path):
        do_something()
    '''

    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


def get_json_or_empty_dict(json_path):
    ''' Returns the content of a json file as dict if it exists. Returns an
        empty dict if the file does not exist.
    '''
    if not pathlib.Path(json_path).is_file():
        return {}
    with open(json_path) as json_file:
        file_content = json.load(json_file)
    return file_content


def get_oldest_timestamp(timestamps):
    ''' Returns the lowest value from a list of timestamps '''
    return str((min([datetime.fromtimestamp(float(i)) for i in timestamps])).timestamp())


def get_newest_timestamp(timestamps):
    ''' Returns the highest value from a list of timestamps '''
    return str((max([datetime.fromtimestamp(float(i)) for i in timestamps])).timestamp())


def get_last_ok(plugin_data):
    ''' Returns the latest data with Status.OK '''
    last_ok = datetime.fromtimestamp(0)
    for timestamp, data in plugin_data.items():
        if datetime.fromtimestamp(float(timestamp)) > last_ok and data['state'] == State.OK.value:
            last_ok = datetime.fromtimestamp(float(timestamp))
    return str(last_ok.timestamp())
