#!/usr/bin/env python
from __future__ import unicode_literals
"""
Copyright (C) 2013 Legoktm

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
IN THE SOFTWARE.
"""

import cache
import mwparserfromhell
import pywikibot
import settings
import Queue
import re

import bot

config = settings.config
config['debug'] = False
config['cache_file'] = 'aiv'


pages = ['Wikipedia:Administrator intervention against vandalism',
         'Wikipedia:Administrator intervention against vandalism/TB2',
         #'User:Legoktm/test',
         ]
AIVbots = ['HBC AIV helperbot7',
           ]

mc = cache.Cache(config)
mc.set('aiv', [])
site = pywikibot.Site('en', 'wikipedia')
#template = re.compile('\{\{(?P<template>([Ii][Pp])?[Vv]andal)\|(?P<user>.*?)\}\}')
templates = ['ipvandal', 'vandal']


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
    mc.set('aiv', l)
    rcv.debug(l)
    print l



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
            for user in mc.get('aiv'):
                if diff['summary'].startswith('blocked User:{0}'.format(user)):
                    self.pull.put((None, raw))
        elif diff['user'] in mc.get('aiv'):
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
            mc.set('aiv', [])

push = Queue.Queue()
pull = Queue.Queue()
pull.put((None, 'Hello, I am a bot tracking https://en.wikipedia.org/wiki/Wikipedia:AIV'))
b = bot.Bot(push, pull, RcvThread, config)
b.run()
