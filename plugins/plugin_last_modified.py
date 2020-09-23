#!/usr/bin/python3
import sys
import json
from basics import State
from basics import ago
import os
import time


def run(config):
    ''' Gather last modified data of a file or directory according to config '''
    try:
        last_modified = os.path.getmtime(config['path'])
        now = time.time()
        state = State.UNDEF
        if 'limit_critical' in config and config['limit_critical'] != '0' and float(config['limit_critical']) <= (now-last_modified):
            state = State.CRITICAL
        elif 'limit_warn' in config and config['limit_warn'] != '0' and float(config['limit_warn']) <= (now-last_modified):
            state = State.WARNING
        else:
            state = State.OK
        if 'timeformat' in config:
            timeformat = config['timeformat']
        else:
            timeformat = '%Y-%m-%dT%H:%M:%S'
        return {"state": state.value, "text": "Last modified on {}".format(time.strftime(timeformat, time.localtime(last_modified))), "short_text": ago(now-last_modified)}
    except OSError:
        return {"state": State.ERROR.value, "text": "Can't get last modified time of {}".format(config['path'])}


if __name__ == "__main__":
    config = {}
    if len(sys.argv) < 2:
        sys.exit("Missing paramters.")
    if len(sys.argv) >= 2:
        if (sys.argv[1] == "--print_config"):
            print("{}")
            exit()
        else:
            config["path"] = sys.argv[1]
            if len(sys.argv) >= 3:
                config["limit_warn"] = sys.argv[2]
            if len(sys.argv) >= 4:
                config["limit_critical"] = sys.argv[3]
            if len(sys.argv) >= 5:
                config["timeformat"] = sys.argv[4]
            result = run(config)
            print(json.dumps(result))
            if(result["state"] == "ERROR"):
                exit(1)
