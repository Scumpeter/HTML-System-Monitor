# HTML System Monitor

Generate an html file that shows the current system status.

## Getting started

### Installation

Just clone the repository to a folder of your choice (e.g. /opt/html_system_monitor)

### Configuration

To get a basic configuration, run `./static_html_monitor.py --configure_plugins`.
This will create the file config/plugins.json. Edit this file to your needs.

There is also a file called config/config.json. This file configures some internally used paths.

### Run the script

This script is meant to be run as a cron job. E.g.: To update the site every 5 minutes, create a file in `/etc/cron.d/` and add something like this:
```
*/5  *   * * *       root    /opt/html_system_monitor/html_system_monitor.py
```

### Configure web server

The resulting html file can be served by any web server capable of serving static websites. A basic configuration for nginx may look like this:
```Nginx
server {
	listen 80 default_server;
	listen [::]:80 default_server;

	root /opt/html_system_monitor/www;
	index index.html;
	server_name my_monitored_device;

	location / {
		try_files $uri $uri/ =404;
	}
}
```

## Plugins

This script uses plugins to gather information about the system. These plugins are scripts that take some command line parameters and return some bit of system information in json format. 
The json must at least contain a **state** (allowed values are "UNDEF", "ERR", "OK", "WARN", "CRIT" and "STALE") and a **text** (may be any string). Additionally it can contain a **percentage** (some numeric value between 0 and 100).

The command to run the plugin and its command line arguments are configured in config/plugins.json. 

### Run plugins externally

Alternatively any plugin can be called outside of the script and its output piped into a file. The script can then collect the outputs. **Be aware that the collected files will be deleted after collection!**

For example, to execute the df plugin externally, crate the folder /opt/html_system_monitor/data/ and use this command:
`/opt/html_system_monitor/plugins/plugin_df.py /mnt/data 80 90 > /opt/html_system_monitor/data/df_data.json`

You can then add this to your config/plugins.json to collect the data:
```JSON
"df_data": {
    "name": "data",
    "manual_path": "/opt/html_system_monitor/data/df_data.json",
    "stale_age": 86400
}
```

**stale_age** is the age of the data in seconds after which the data is considered stale (i.e.: not up-to-date).