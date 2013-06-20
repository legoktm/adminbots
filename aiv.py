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

import mwparserfromhell
import pywikibot
from pywikibot.data import api
import sh
import urllib

from mtirc import bot


pages = ['Wikipedia:Administrator intervention against vandalism',
         'Wikipedia:Administrator intervention against vandalism/TB2',
         #'User:Legoktm/test',
         ]
AIVbots = ['HBC AIV helperbot7',
           'HBC AIV helperbot5',
           ]

site = pywikibot.Site('en', 'wikipedia')
#template = re.compile('\{\{(?P<template>([Ii][Pp])?[Vv]andal)\|(?P<user>.*?)\}\}')
templates = ['ipvandal', 'vandal']


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


def parse_all(boot, by_bot=False):
    l = []
    for page in pages:
        l += parse(page)
    l = list(set(l))
    old = boot.cache.get('aiv')
    for c in l:
        if not c in old:
            info = all_info(c)
            for m in info:
                boot.queue_msg(None, m)

    boot.cache.set('aiv', l)
    if by_bot and l:
        boot.queue_msg(None, 'There are {0} requests on AIV.'.format(len(l)))
    print l


def all_info(username):
    return user_info(username) + block_info(username) + af_info(username)


def block_info(username):
    text = []
    #list=logevents&letype=block&lelimit=100&format=jsonfm&letitle=User:Legobot
    params = {'action': 'query',
              'list': 'logevents',
              'letype': 'block',
              'lelimit': 'max',
              'letitle': 'User:' + username,
              }
    req = api.Request(**params)
    data = req.submit()
    data = data['query']['logevents']
    if not data:
        text.append('blockinfo: user has not been blocked before')
        return text
    last = data[0]
    if last['action'] == 'unblock':
        text.append('last unblocked by {user} with comment: {comment}'.format(**last))
    elif last['action'] in ['block', 'reblock']:
        text.append('last {action}ed by {user} for {duration} with comment: {comment}'.format(
            duration=last['block']['duration'], **last
        ))
    else:
        # ???
        pass
    return text


def user_info(username):
    text = ['[[User:{0}]]: https://en.wikipedia.org/wiki/Special:Contributions/{1}'.format(
        username, urllib.quote_plus(username.replace(' ', '_').encode('utf-8')))]
    #&list=users&ususers=Legoktm&usprop=blockinfo|groups|editcount|registration&format=jsonfm
    params = {'action': 'query',
              'list': 'users',
              'ususers': username,
              'usprop': 'blockinfo|groups|editcount|registration',
              }
    req = api.Request(**params)
    data = req.submit()
    data = data['query']['users'][0]
    print data
    if 'missing' in data:
        return text
    elif 'invalid' in data:  # IP address
        return text + rDNS(username)
    text.append('editcount: {0}'.format(data['editcount']))
    text.append('userrights: {0}'.format(', '.join(data['groups'])))
    if 'blockid' in data:
        text.append('{0} is currently blocked'.format(username))
    return text


def af_info(username):
    l = []
    #action=query&list=abuselog&afluser=Lichj&format=jsonfm
    params = {'action': 'query',
              'list': 'abuselog',
              'afluser': username,
              'afllimit': 50,
              }
    req = api.Request(**params)
    data = req.submit()
    count = len(data['query']['abuselog'])
    if count:
        l.append('af hits: {0}'.format(count))
    return l


def rDNS(ip):
    data = sh.dig('-x' , ip)
    return ['rDNS: ' + data.splitlines()[11].split('\t')[-1][:-1]]


def run(**kw):
    if kw['channel'] == '#en.wikipedia':
        rc_hit(bot.parse_edit(kw['text']), kw['text'], kw['bot'])
    else:
        on_msg(kw['channel'], kw['text'], kw['sender'], kw['bot'])
    return True

def rc_hit(diff, raw, boot):
    if 'page' in diff and diff['page'] in pages:
        by_bot = diff['user'] in AIVbots
        if not by_bot:
            boot.queue_msg(None, raw)
        parse_all(boot, by_bot)
    elif 'log' in diff and diff['log'] == 'block':
        #self.pull.put((None, raw))
        for user in boot.cache.get('aiv'):
            if diff['summary'].startswith('blocked User:{0}'.format(user)):
                boot.queue_msg(None, raw)
    elif diff['user'] in boot.cache.get('aiv'):
        boot.queue_msg(None, raw)
        #print repr(diff['summary'])


def on_msg(channel, text, sender, boot):
    print text
    if text.startswith('!ping'):
        boot.queue_msg(channel, 'pong')
    elif text.startswith('!parse'):
        parse_all(boot)
    elif channel == boot.config['nick']:
        #pm'ing with bot
        if sender.host == 'wikipedia/Legoktm':
            chan = text.split(' ')[0]
            real_text = ' '.join(text.split(' ')[1:])
            boot.queue_msg(chan, real_text)
    elif text.startswith('!clear'):
        boot.cache.set('aiv', [])
    elif text.startswith('!info'):
        username = ' '.join(text.split(' ')[1:])
        for line in all_info(username):
            boot.queue_msg(channel, line)
