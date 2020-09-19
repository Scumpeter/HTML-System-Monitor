#!/usr/bin/python3
import sys
import json
from basics import State
import os

def run(config):
    ''' Gather raspberry pi temperature according to config '''
    temperature_file_path = '/sys/class/thermal/thermal_zone0/temp'
    if(os.path.isfile(temperature_file_path)):
        with open(temperature_file_path, 'r') as temperature_file:
            temperature = float(temperature_file.read()) / 1000.0
            state = State.UNDEF
            if 'limit_critical' in config and config['limit_critical'] != '0' and float(config['limit_critical']) >= temperature:
                state = State.CRITICAL
            elif 'limit_warn' in config and config['limit_warn'] != '0'  and float(config['limit_warn']) >= temperature:
                state = State.WARNING
            else:
                state = State.OK
            return({"state": state.value, "text": "{:0.2f}°C".format(temperature)})
    else:
        return({"state": State.ERROR.value, "text": "File not found {}".format(temperature_file_path)})

def get_default_config():
    ''' Returns a dict with the default config if 
        /sys/class/thermal/thermal_zone0/temp is a file
    '''
    config = {}
    temperature_file_path = '/sys/class/thermal/thermal_zone0/temp'
    if(os.path.isfile(temperature_file_path)):
        config["pitemp"] = {
            "name": "CPU Temperature",
            "command": os.path.abspath(__file__),
            "arguments": ["75", "85"]
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
            if len(sys.argv) >= 2:
                config["limit_warn"] = sys.argv[1]
            if len(sys.argv) >= 3:
                config["limit_critical"] = sys.argv[2]
            result = run(config)
            print(json.dumps(result))
            if(result["state"] == "ERROR"):
                exit(1)