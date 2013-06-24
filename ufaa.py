#!/usr/bin/env python
from __future__ import unicode_literals
import mwparserfromhell
import pywikibot

from mtirc import bot

pages = ['Wikipedia:Usernames for administrator attention',
         'Wikipedia:Usernames for administrator attention/Bot',
         #'User:Legoktm/test',
         ]
AIVbots = ['HBC AIV helperbot7',
           'HBC AIV helperbot5',
           ]

site = pywikibot.Site('en', 'wikipedia')
#template = re.compile('\{\{(?P<template>([Ii][Pp])?[Vv]andal)\|(?P<user>.*?)\}\}')
templates = ['user-uaa']


def run(**kw):
    if kw['server'] == 'irc.wikimedia.org':
        rc_hit(bot.parse_edit(kw['text']), kw['text'], kw['bot'])
    else:
        on_msg(kw['channel'], kw['text'], kw['sender'], kw['bot'])

    return True


def parse(page):
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


def parse_all(boot):
    l = []
    for page in pages:
        l += parse(page)
    l = list(set(l))
    boot.cache.set('uaa', l)


def rc_hit(diff, raw, boot):
    if 'page' in diff and diff['page'] in pages:
        if not diff['user'] in AIVbots:
            boot.queue_msg(None, raw)
        parse_all(boot)
    elif 'log' in diff and diff['log'] == 'block':
        #self.pull.put((None, raw))
        for user in boot.cache.get('uaa'):
            if diff['summary'].startswith('blocked User:{0}'.format(user)):
                boot.queue_msg(None, raw)
    elif diff['user'] in boot.cache.get('uaa'):
        boot.queue_msg(None, raw)
        #print repr(diff['summary'])


def on_msg(channel, text, sender, boot):
    if text.startswith('!parse'):
        parse_all(boot)
    elif channel == boot.config['nick']:
        #pm'ing with bot
        if sender.host == 'wikipedia/Legoktm':
            chan = text.split(' ')[0]
            real_text = ' '.join(text.split(' ')[1:])
            boot.queue_msg(chan, real_text)
    elif text.startswith('!clear'):
        boot.cache.set('uaa', [])
