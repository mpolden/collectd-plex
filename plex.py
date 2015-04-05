#!/usr/bin/env python

from __future__ import print_function

import sys
import requests

CONFIGS = []


def configure_callback(conf):
    host = None
    port = None
    section = None
    sum_leaf = False
    instance = None

    for node in conf.children:
        key = node.key.lower()
        val = node.values[0]

        if key == 'host':
            host = val
        elif key == 'port':
            port = int(val)
        elif key == 'section':
            section = int(val)
        elif key == 'sumleaf':
            sum_leaf = val
        elif key == 'instance':
            instance = val
        else:
            collectd.warning('plex plugin: Unknown config key: %s.' % key)
            continue

    config = {
        'host': host,
        'port': port,
        'section': section,
        'sum_leaf': sum_leaf,
        'instance': instance
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
    url = 'http://{host}:{port}/library/sections/{section}/all'.format(
        host=conf['host'],
        port=conf['port'],
        section=conf['section']
    )
    data = get_json(url)
    count = sum_videos(data, conf['sum_leaf'])
    plugin_instance = get_plugin_instance(conf)
    type_instance = get_type_instance(data, conf)

    if callback is None:
        dispatch_value(type_instance, plugin_instance, count)
    else:
        callback(type_instance, plugin_instance, count)


def get_plugin_instance(conf):
    return '{host}-section_{section}'.format(host=conf['host'],
                                             section=conf['section'])


def get_type_instance(data, conf):
    instance = conf['instance']
    if instance is None:
        instance = data['title1'].lower().replace(' ', '_')
    return instance


def get_json(url):
    headers = {'Accept': 'application/json'}
    r = requests.get(url, headers=headers)
    return r.json()


def sum_videos(data, sum_leaf=False):
    if sum_leaf:
        return sum(c['leafCount'] for c in data['_children'])
    return len(data['_children'])


def main():
    if len(sys.argv) < 6:
        print('{} <host> <port> <section> <sum_leaf> <instance>'.format(
            sys.argv[0]))
        sys.exit(1)
    instance = sys.argv[5] if sys.argv[5] != 'auto' else None
    conf = {
        'host': sys.argv[1],
        'port': sys.argv[2],
        'section': sys.argv[3],
        'sum_leaf': sys.argv[4].lower() == 'true',
        'instance': instance
    }

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
