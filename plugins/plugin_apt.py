#!/usr/bin/python3
import sys
import os
import json
from basics import State
import subprocess


def run(config):
    ''' Gathers update information according to config '''
    if(config['refresh']):
        # i am not sure if -d will make this useless.
        subprocess.run(['apt-get', 'update', '-qqd'])
    apt_result = subprocess.run(
        ['apt-get', '-s', 'dist-upgrade', '--quiet=2'], stdout=subprocess.PIPE)
    # This will return the updateable packages, each in one line. It has a topic
    # line So we have to subtract 1 from the number of lines.
    packages = len(str(apt_result.stdout).split('Inst ')) - 1
    # If no updateable packages are present, there is no topic line. So
    # 'packages' will be -1.
    if packages < 0:
        packages = 0
    state = State.UNDEF
    if packages > config['limit_critical']:
        state = State.CRITICAL
    elif packages > config['limit_warn']:
        state = State.WARNING
    else:
        state = State.OK
    if packages == 1:
        text = '{} update available'.format(packages)
    else:
        text = '{} updates available'.format(packages)
    return ({"state": state.value, "text": text})


def get_default_config():
    ''' Returns a dict with the default config '''
    config = {}
    config["apt"] = {
        "name": "Updates",
        "command": os.path.abspath(__file__),
        "arguments": ["False", "1", "10"]
    }
    return config


if __name__ == "__main__":
    config = {}
    if len(sys.argv) < 2:
        sys.exit("Missing paramters.")
    if len(sys.argv) >= 2:
        if (sys.argv[1] == "--print_config"):
            print(json.dumps(get_default_config()))
        else:
            if len(sys.argv) >= 4:
                config["refresh"] = ("True" == sys.argv[1])
                config["limit_warn"] = int(sys.argv[2])
                config["limit_critical"] = int(sys.argv[3])
                result = run(config)
                print(json.dumps(result))
                if(result["state"] == "ERROR"):
                    exit(1)
