#!/usr/bin/env python
import sys

import private


def update(config):
    config['channel'] = '##legoktm-bots'
    config['chatter-channel'] = '##legoktm-bots-chatter'
    config['ns_username'] = 'legobot'
    config['ns_pw'] = private.ns_pw
    config['authenticate'] = not ('--labs' in sys.argv)
    config['memory']['aiv'] = '600M'
    config['memory']['ufaa'] = '256M'
    config['memory']['rfpp'] = '256M'
    if '--labs' in sys.argv:
        config['threads'] = 1
    else:
        config['threads'] = 5
    return config
