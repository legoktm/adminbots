#!/usr/bin/env python
from __future__ import unicode_literals
import cache
import mwparserfromhell
import pywikibot
import settings
import Queue
import re

import bot

config = settings.config
config['nick'] = 'UfAA'
config['debug'] = True
config['cache_file'] = 'ufaa'

pages = ['Wikipedia:Usernames for administrator attention',
         'Wikipedia:Usernames for administrator attention/Bot',
         #'User:Legoktm/test',
         ]
AIVbots = ['HBC AIV helperbot7',
           ]

mc = cache.Cache(config)
mc.set('uaa', [])
site = pywikibot.Site('en', 'wikipedia')
#template = re.compile('\{\{(?P<template>([Ii][Pp])?[Vv]andal)\|(?P<user>.*?)\}\}')
templates = ['user-uaa']


def parse(page, rcv):
    #page: page that got updated
    #push: push queue to send a message
    pg = pywikibot.Page(site, page)
    text = pg.get()
    code = mwparserfromhell.parse(text)
    s = set()
    for t in code.filter_templates():
        if t.name.strip().lower() in templates:
            s.add(unicode(t.get(1).value))
    s = list(s)
    return s

def parse_all(rcv):
    l = []
    for page in pages:
        l += parse(page, rcv)
    l = list(set(l))
    mc.set('uaa', l)
    rcv.debug(l)


class RcvThread(bot.ReceiveThread):
    def parse(self, channel, text, sender):
        if channel == '#en.wikipedia':
            self.rc_hit(bot.parse_edit(text), text)
        else:
            self.on_msg(channel, text, sender)

    def rc_hit(self, diff, raw):
        if 'page' in diff and diff['page'] in pages:
            if not diff['user'] in AIVbots:
                self.pull.put((None, raw))
            parse_all(self)
        elif 'log' in diff and diff['log'] == 'block':
            #self.pull.put((None, raw))
            for user in mc.get('uaa'):
                if diff['summary'].startswith('blocked User:{0}'.format(user)):
                    self.pull.put((None, raw))
        elif diff['user'] in mc.get('uaa'):
            self.pull.put((None, raw))
            #print repr(diff['summary'])

    def on_msg(self, channel, text, sender):
        print text
        if text.startswith('!ping'):
            self.pull.put((channel, 'pong'))
        elif text.startswith('!parse'):
            parse_all(self)
        elif channel == config['nick']:
            #pm'ing with bot
            if sender.host == 'wikipedia/Legoktm':
                chan = text.split(' ')[0]
                real_text = ' '.join(text.split(' ')[1:])
                self.pull.put((chan, real_text))
        elif text.startswith('!clear'):
            mc.set('uaa', [])

push = Queue.Queue()
pull = Queue.Queue()
pull.put((None, 'Hello, I am a bot tracking https://en.wikipedia.org/wiki/Wikipedia:UAA'))
b = bot.Bot(push, pull, RcvThread, config)
b.run()
