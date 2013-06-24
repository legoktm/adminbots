#!/usr/bin/env python
from __future__ import unicode_literals
import cache
import mwparserfromhell
import pywikibot
import Queue
import re

pywikibot.config.maxlag = 9999


from mtirc import bot
from mtirc import settings

config = settings.config
config['nick'] = 'RfPP'
config['debug'] = True
config['cache_file'] = 'rfpp'


pages = ['Wikipedia:Requests for page protection',
         #'User:Legoktm/test',
]
AIVbots = ['Snotbot',
           ]

mc = cache.Cache(config)
mc.set('rfpp', [])
site = pywikibot.Site('en', 'wikipedia')
#template = re.compile('\{\{(?P<template>([Ii][Pp])?[Vv]andal)\|(?P<user>.*?)\}\}')
templates = ['ln', 'la', 'lt', 'lw', 'lu', 'lc', 'lf', 'lp', 'lh', 'lb']
for t in templates[:]:
    templates.append(t + 't')
templates.append('lmt')

def advance_parse(code):
    for t in code.get_sections()[1:]:
        if '{{' in t.filter()[0].title:
            if not '{{RFPP' in t:
                yield unicode(t.filter()[0].title.filter_templates()[0].get(1).value)

def parse(page, rcv):
    #page: page that got updated
    #push: push queue to send a message
    pg = pywikibot.Page(site, page)
    text = pg.get()
    code = mwparserfromhell.parse(text)
    s = set()
    for c in advance_parse(code):
        s.add(c)
    #for t in code.get_sections()[1:]:
    #    if '{{'in t.filter()[0].title:
    #        s.add(t.filter()[0].title.filter_templates()[0].get(1).value)
    s = list(s)
    mc.set('rfpp', s)
    rcv.debug(s)
    print s


def parse_all(rcv):
    for page in pages:
        parse(page, rcv)


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
            parse(diff['page'], self)
        elif 'log' in diff and diff['log'] == 'protect':
            #self.pull.put((None, raw))
            #print repr(diff['summary'])
            for title in mc.get('rfpp'):
                if diff['summary'].startswith('protected {0}'.format(title)):
                    self.pull.put((None, raw))
        elif 'page' in diff and diff['page'] in mc.get('rfpp'):
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
            mc.set('rfpp', [])

push = Queue.Queue()
pull = Queue.Queue()
pull.put((None, 'Hello, I am a bot tracking https://en.wikipedia.org/wiki/Wikipedia:RfPP'))
b = bot.Bot(push, pull, RcvThread, config)
b.run()
