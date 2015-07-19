#!/usr/bin/env python

from __future__ import print_function

import sys
import requests

CONFIGS = []


def configure_callback(conf):
    host = None
    port = None
    metric = None
    section = None
    instance = None
    authtoken = None

    for node in conf.children:
        key = node.key.lower()
        val = node.values[0]

        if key == 'host':
            host = val
        elif key == 'port':
            port = int(val)
        elif key == 'metric':
          metric_parts = val.split(':')
          if len(metric_parts) > 2:
              collectd.error('Invalid metric format: {0}'.format(sys.argv[4]))
          elif len(metric_parts) > 1:
              section = metric_parts[1]
          metric = metric_parts[0]
        elif key == 'instance':
            instance = val
        elif key == 'authtoken':
            authtoken = val
        else:
            collectd.warning('plex plugin: Unknown config key: %s.' % key)
            continue

    config = {
        'host': host,
        'port': port,
        'metric': metric,
        'section': section,
        'instance': instance,
        'authtoken': authtoken
    }

    collectd.info('plex plugin: Configured with {}'.format(config))
    CONFIGS.append(config)


def read_callback():
    for conf in CONFIGS:
        get_metrics(conf)


def dispatch_value(type_instance, plugin_instance, value):
    val = collectd.Values(plugin='plex')
    val.type = 'gauge'
    val.type_instance = type_instance
    val.plugin_instance = plugin_instance
    val.values = [value]
    val.dispatch()


def get_metrics(conf, callback=None):

    if conf['metric'] in ['movies', 'shows', 'episodes']:
        if conf['section'] is None:
            print('Must provide section number to find media count!')
            sys.exit(1)
        (value, data) = get_media_count(conf)
    else:
        print('Unknown metric type: {0}'.format(conf['metric']))
        sys.exit(1)

    plugin_instance = get_plugin_instance(conf)
    type_instance = get_type_instance(data, conf)

    if callback is None:
        dispatch_value(type_instance, plugin_instance, value)
    else:
        callback(type_instance, plugin_instance, value)

def get_media_count(conf):

    url = 'http://{host}:{port}/library/sections/{section}/all'.format(
        host=conf['host'],
        port=conf['port'],
        section=conf['section']
    )

    data = get_json(url, conf['authtoken'])
    validate_media_type(conf['section'], data['librarySectionTitle'], conf['metric'], data['viewGroup'])

    if conf['metric'] in ['movies', 'shows']:
    	count = sum_videos(data, False)
    elif conf['metric'] in ['episodes']:
        count = sum_videos(data, True)

    return (count, data)

def validate_media_type(section, title, metric, media):

    mapping = {'movies': 'movie',
               'shows': 'show',
               'episodes': 'show'}

    if mapping[metric] != media:
        print('Section #{0} ({1}) contains {2}s. Does not match metric, {3}!'.format(section,
                                                                                     title,
                                                                                     media,
                                                                                     metric))
        sys.exit(1)
    else:
        return True

def get_plugin_instance(conf):
    return '{host}-section_{section}'.format(host=conf['host'],
                                             section=conf['section'])


def get_type_instance(data, conf):
    instance = conf['instance']
    if instance is None:
        instance = data['title1'].lower().replace(' ', '_')
    return instance


def get_json(url, authtoken):
    headers = {
               'Accept': 'application/json',
               'X-Plex-Token': authtoken
              }
    r = requests.get(url, headers=headers)
    return r.json()


def sum_videos(data, sum_leaf=False):
    if sum_leaf:
        return sum(c['leafCount'] for c in data['_children'])
    return len(data['_children'])


def main():
    if len(sys.argv) < 6:
        print('{} <host> <port> <authtoken> <metric> <instance>'.format(
            sys.argv[0]))
        print('Metrics:')
        print ('- movies:<Section#>')
        print ('- shows:<Section#>')
        print ('- episodes:<Section#>')
        print ('- sessions')
        sys.exit(1)
    instance = sys.argv[5] if sys.argv[5] != 'auto' else None
    conf = {
        'host': sys.argv[1],
        'port': sys.argv[2],
        'authtoken': sys.argv[3],
        'instance': instance
    }
    metric_parts = sys.argv[4].split(':')
    if len(metric_parts) > 2:
        print('Invalid metric format: {0}'.format(sys.argv[4]))
        sys.exit(1)
    if len(metric_parts) > 1:
        conf['section'] = metric_parts[1]
    else:
        conf['section'] = None
    conf['metric'] = metric_parts[0]

    def callback(type_instance, plugin_instance, value):
        print({
            'value': value,
            'type_instance': type_instance,
            'plugin_instance': plugin_instance,
            'full_name': 'plex-{}.gauge-{}.value'.format(plugin_instance,
                                                         type_instance)
        })
    get_metrics(conf, callback)


if __name__ == '__main__':
    main()
else:
    import collectd
    collectd.register_config(configure_callback)
    collectd.register_read(read_callback)
