#!/usr/bin/env python
import private


def update(config):
    config['authenticate'] = True
    config['channel'] = '##legoktm-bots'
    config['chatter-channel'] = '##legoktm-bots-chatter'
    config['ns_username'] = 'legobot'
    config['ns_pw'] = private.ns_pw
    config['authenticate'] = True
    config['memory']['aiv'] = '600M',
    config['memory']['ufaa'] = '256M'
    config['memory']['rfpp'] = '256M'
    return config
