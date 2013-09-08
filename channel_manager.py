# -*- coding: utf-8 -*-
# (C) Legoktm, 2013
# Licensed under the MIT License

# Assists with joining/parting channels

import os
import yaml
from mtirc import hooks
filename = os.path.expanduser('~/channels.yml')


def get_channel_list():
    with open(filename) as f:
        raw = f.read()
    data = yaml.load(raw)
    return data


def on_connect(**kw):
    data = get_channel_list()
    if kw['server'] in data:
        for channel in data[kw['server']]:
            kw['bot'].servers[kw['server']].join(channel)


def on_msg(**kw):
    if kw['text'] == '!reload channels':
        data = get_channel_list()
        for server in data:
            if server in kw['bot'].servers:
                for channel in data[server]:
                    kw['bot'].servers[server].join(channel)


hooks.add_hook('connected', 'channel_joiner', on_connect)
hooks.add_hook('on_msg', 'channel_reloader', on_msg)
