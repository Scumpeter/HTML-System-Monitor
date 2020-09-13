#!/usr/bin/python3

import shutil   # for getting file system usage data
import pathlib  # to check if a path exists and is a mount point
import sys      # to get command line arguments
import os       # to get path to this script for the config
import json     # for printing correctly formated json output
from basics import State
from basics import sizeof_fmt


def run(config):
    ''' Gather file system usage data according to config '''
    # Check config
    if "path" in config:
        path = config["path"]
    else:
        return ({"state": State.ERROR.value, "text": "Config error: Path for DF is missing."})
    if "limit_warn" in config:
        limit_warn = int(config["limit_warn"])
    else:
        limit_warn = 80
    if "limit_critical" in config:
        limit_critical = int(config["limit_critical"])
    else:
        limit_critical = 90
    # Check if path exists and is the root of a mounted file system
    if not pathlib.Path(path).is_dir():
        return ({"state": State.ERROR.value, "text": "Path {} does not exist".format(path)})
    if not pathlib.Path(path).is_mount():
        return ({"state": State.ERROR.value, "text": "{} is not mounted.".format(path)})
    # Get usage data
    (size_bytes, used_bytes, free_bytes) = shutil.disk_usage(path)
    # Make data human readable
    size = sizeof_fmt(size_bytes)
    used = sizeof_fmt(used_bytes)
    avail = sizeof_fmt(free_bytes)
    # Add percentage
    if(free_bytes > 0):
        percentage = round(used_bytes/size_bytes * 100.0, 1)
    else:
        percentage = 100.0
    # Add state
    if(percentage > limit_critical):
        state = State.CRITICAL
    elif(percentage > limit_warn):
        state = State.WARNING
    else:
        state = State.OK
    return ({"state": state.value, "text": "Size: {}; Used: {}; Avail: {}".format(size, used, avail), "percentage": percentage})


def get_default_config():
    ''' Returns a dict with the default config for every filesystem listed in /etc/mtab '''
    # Some filesystems that should usually be ignored (e.g.: virtual filesystems):
    ignore_fstypes = [
        "tmpfs",
        "squashfs",
        "cgroup",
        "cgroup2",
        "sysfs",
        "proc",
        "devtmpfs",
        "devpts",
        "securityfs",
        "pstore",
        "efivarfs",
        "bpf",
        "autofs",
        "mqueue",
        "hugetlbfs",
        "debugfs",
        "tracefs",
        "fusectl",
        "configfs",
        "binfmt_misc",
        "fuse.gvfsd-fuse",
        "nsfs"]
    # get mounts from /etc mtab
    mtab_columns = ["device", "path", "type"]
    mounts = [dict(zip(mtab_columns, line.split()[0:3]))
              for line in open("/etc/mtab")]
    # fill data for each mtab entry
    config = {}
    for mount in mounts:
        if not mount["type"] in ignore_fstypes:
            config["df_{}".format(mount["path"])] = {
                "name": "{}".format(mount["path"]),
                "command": os.path.abspath(__file__),
                "arguments": [mount["path"].replace("\\040", " "), "80", "90"]
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
            config["path"] = sys.argv[1]
            if len(sys.argv) >= 3:
                config["limit_warn"] = sys.argv[2]
            if len(sys.argv) >= 4:
                config["limit_critical"] = sys.argv[3]
            result = run(config)
            print(json.dumps(result))
            if(result["state"] == "ERROR"):
                exit(1)
