#!/usr/bin/env python
from __future__ import unicode_literals
import mwparserfromhell
import pywikibot
import Queue

pywikibot.config.maxlag = 9999


from mtirc import lib

pages = ['Wikipedia:Requests for page protection',
         #'User:Legoktm/test',
]
AIVbots = ['Snotbot',
           ]

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


def parse_hit(page, boot):
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
    boot.cache.set('rfpp', s)
    boot.debug(s)


def parse_all(boot):
    for page in pages:
        parse_hit(page, boot)


def parse(**kw):
    if kw['channel'] == '#en.wikipedia':
        rc_hit(kw['bot'], lib.parse_edit(kw['text']), kw['text'])
    else:
        on_msg(kw['bot'], kw['channel'], kw['text'], kw['sender'])


def rc_hit(boot, diff, raw):
    if 'page' in diff and diff['page'] in pages:
        if not diff['user'] in AIVbots:
            boot.queue_msg(None, raw)
        parse_hit(diff['page'], boot)
    elif 'log' in diff and diff['log'] == 'protect':
        #self.pull.put((None, raw))
        #print repr(diff['summary'])
        for title in boot.cache.get('rfpp'):
            if diff['summary'].startswith('protected {0}'.format(title)):
                boot.queue_msg(None, raw)
    elif 'page' in diff and diff['page'] in boot.cache.get('rfpp'):
        boot.queue_msg(None, raw)
        #print repr(diff['summary'])


def on_msg(boot, channel, text, sender):
    if text.startswith('!parse'):
        parse_all(boot)
    elif channel == boot.config['nick']:
        #pm'ing with bot
        if sender.host == 'wikipedia/Legoktm':
            chan = text.split(' ')[0]
            real_text = ' '.join(text.split(' ')[1:])
            boot.queue_msg(chan, real_text)
    elif text.startswith('!clear'):
        boot.cache.set('rfpp', [])
