#!/usr/bin/python3
from datetime import datetime
import jinja2
from utils import get_json_or_empty_dict
from utils import get_newest_timestamp
from utils import get_last_ok
from plugins.basics import State
from plugins.basics import SummaryType
from plugins.basics import ago


def timestamp_to_formated_time(value):
    ''' Jinja2 filter for getting a datetimeobject from a timestamp-string '''
    if value==0:
        return 'never'
    else:
        datetime_pretty_string = datetime.fromtimestamp(float(value)).strftime('%c')
        datetime_string = datetime.fromtimestamp(float(value)).strftime('%Y-%m-%dT%H:%M:%S')
        return '<time datetime={datetime_string} title={datetime_string}>{datetime_pretty_string}</time>'.format(datetime_string=datetime_string, datetime_pretty_string=datetime_pretty_string)


def prepare_html_data(config):
    ''' Makes data from json file easily accessible from the jinja2 template '''
    result_data_plugins = {}
    json_plugins = get_json_or_empty_dict(config['plugins_config_path'])
    json_data = get_json_or_empty_dict(config['data_path'])
    now = datetime.now().timestamp()
    for plugin_index, plugin_config in json_plugins.items():
        result_data_plugins[plugin_index] = {}
        result_data_plugins[plugin_index]['data'] = {}
        # if there is valid data, use it. keep the empty dict otherwise
        if plugin_index in json_data and 'state' in json_data[plugin_index]['data']:
            result_data_plugins[plugin_index] = json_data[plugin_index]
            # if the data is older than stale_age, change state to "STALE"
            if 'stale_age' in plugin_config and 'last_checked' in json_data[plugin_index]:
                last_checked_age = now - float(json_data[plugin_index]['last_checked'])
                if  last_checked_age > float(plugin_config['stale_age']):
                    result_data_plugins[plugin_index]['data']['state'] = State.STALE.value
            # if a short_text_type is defined, parse the short text accordingly
            if 'short_text' in json_data[plugin_index]['data'] and 'short_text_type' in json_data[plugin_index]['data']:
                short_text_type = json_data[plugin_index]['data']['short_text_type']
                if short_text_type == SummaryType.TIMESTAMP_FOR_AGE.value:
                    result_data_plugins[plugin_index]['data']['short_text'] = timestamp_to_formated_time(json_data[plugin_index]['data']['short_text'])
        # if no data for a configured plugin can be found, set default values
        else:
            print('No data found for plugin {}'.format(plugin_index))
            result_data_plugins[plugin_index]['data']['state'] = State.UNDEF.value
            result_data_plugins[plugin_index]['data']['text'] = 'No data yet.'
        result_data_plugins[plugin_index]['data']['name'] = plugin_config['name']
    result_data = {}
    result_data['time_now'] = now
    result_data['plugins'] = result_data_plugins
    return result_data


def render_html(config):
    ''' Create an HTML file from a template and json data. '''
    # Initiate jinja2 template loader for current path
    templateLoader = jinja2.FileSystemLoader(searchpath='./')
    templateEnv = jinja2.Environment(loader=templateLoader)
    # Add python functions as custom jinja2 filters
    templateEnv.filters['timestamp_to_formated_time'] = timestamp_to_formated_time
    # load template
    template = templateEnv.get_template(config['template_path'])
    # start rendering with data from json data
    rendered_html = template.render(all_data=prepare_html_data(config))
    # write html file
    with open(config['output_path'], 'w') as html_output_file:
        html_output_file.write(rendered_html)
