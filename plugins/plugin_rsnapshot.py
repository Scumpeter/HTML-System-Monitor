#!/usr/bin/python3

import json     # for reading the settings and storing the data
import re       # for matching strings in rsnapshot config and log files
import pathlib  # for checking if data file exists
import datetime  # for parsing log time stamps
import os       # to get path to this script for the config
import sys      # to get command line arguments
from basics import State
from basics import SummaryType
from basics import ago


def run(config):
    ''' Gather rsnapshot log information according to config

    The log will contain lines like
    [2020-08-01T12:31:33] /usr/bin/rsync -aWx --delete --numeric-ids --relative --delete-excluded /mnt/data/ /mnt/backup/snapshots/daily.0/localhost/
    for every started backup.

    If the backup fails, it will also have something like this later in the log
    [2020-08-01T12:36:00] /usr/bin/rsnapshot daily: ERROR: /usr/bin/rsync returned 255 while processing /mnt/data/

    This function checks the last line for a backup path in the log and checks
    if it looks like the former example.
    '''
    re_backup_rsync_started = r"^\[(.*)\] /usr/bin/rsync .* {} .*$".format(
        config['path'])
    re_timestamp = r"^\[(.*)\].*"
    with open(config["log_file"], 'r') as log_file:
        log_lines = log_file.read().splitlines()
        log_lines.reverse()
    state = State.UNDEF
    short_text = "-"
    last_log_msg = None
    for search_line in log_lines:
        log_match = re.search(config['path'], search_line)
        if log_match != None:
            last_log_msg = search_line
            break
    if last_log_msg != None:
        log_match = re.search(re_backup_rsync_started, last_log_msg)
        if log_match != None:
            state = State.OK
        else:
            state = State.CRITICAL
        timestamp_match = re.search(re_timestamp, last_log_msg)
        if timestamp_match != None:
            timestring = timestamp_match.group(1)
            log_time = datetime.datetime.strptime(timestring, '%Y-%m-%dT%H:%M:%S')
            short_text = log_time.timestamp()
    else:
        last_log_msg = 'Path {} not found in log file {}.'.format(
            config['path'], config['log_file'])
    if(short_text == "-"):
        return {"state": state.value, "text": last_log_msg, "short_text": short_text}
    else:
        return {"state": state.value, "text": last_log_msg, "short_text": short_text, "short_text_type": SummaryType.TIMESTAMP_FOR_AGE.value}


def get_default_config(config_file_path='/etc/rsnapshot.conf'):
    ''' Returns a dict with the default config for every path listed in config file 

    Backup locations in the config file are stored like this:
    [Keyword: backup][TABS][Source path][TABS][Target path]
    e.g:
    backup	/mnt/data/	localhost/
    We only care about the [Source path] part.

    If config_file_path is no file, this function will return an empty dict.
    '''
    backups = {}
    if(os.path.isfile(config_file_path)):
        re_backup_location = r"^\s*backup\s*(\S*)\s*(\S*)\s*$"
        re_log_location = r"^\s*logfile\s*(\S*)\s*$"
        log_path = "/var/log/rsnapshot.log"
        with open(config_file_path, 'r') as config_file:
            config_file_lines = config_file.readlines()
            # find path to log file
            for config_line in config_file_lines:
                log_match = re.search(re_log_location, config_line)
                if log_match != None:
                    log_path = log_match.group(1)
            # find backup locations
            for config_line in config_file_lines:
                config_match = re.search(re_backup_location, config_line)
                if config_match != None:
                    backup_path = config_match.group(1)
                    index = "rsnapshot_{}".format(backup_path)
                    backups[index] = {
                        "name": "Backup: {}".format(backup_path),
                        "command": os.path.abspath(__file__),
                        "arguments": [log_path, backup_path]
                    }
    return backups


if __name__ == "__main__":
    config = {}
    if len(sys.argv) < 2:
        sys.exit("Missing paramters.")
    if len(sys.argv) >= 2:
        if (sys.argv[1] == "--print_config"):
            if len(sys.argv) >= 3:
                print(json.dumps(get_default_config(sys.argv[2])))
            else:
                print(json.dumps(get_default_config()))
        elif len(sys.argv) >= 3:
            config["log_file"] = sys.argv[1]
            config["path"] = sys.argv[2]
            result = run(config)
            print(json.dumps(result))
            if(result["state"] == "ERROR"):
                exit(1)
