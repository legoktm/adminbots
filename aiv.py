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
from pywikibot.data import api
import Queue
import sh
import urllib

import bot
import settings

config = settings.config
config['nick'] = 'AIV'
config['debug'] = False
config['cache_file'] = 'aiv'


pages = ['Wikipedia:Administrator intervention against vandalism',
         'Wikipedia:Administrator intervention against vandalism/TB2',
         #'User:Legoktm/test',
         ]
AIVbots = ['HBC AIV helperbot7',
           'HBC AIV helperbot5',
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


def parse_all(rcv, bot=False):
    l = []
    for page in pages:
        l += parse(page, rcv)
    l = list(set(l))
    old = mc.get('aiv')
    for c in l:
        if not c in old:
            info = all_info(c)
            for m in info:
                rcv.pull.put((None, m))

    mc.set('aiv', l)
    if bot and l:
        rcv.pull.put((None, 'There are {0} requests on AIV.'.format(len(l))))
    rcv.debug(l)
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


class RcvThread(bot.ReceiveThread):
    def parse(self, channel, text, sender):
        if channel == '#en.wikipedia':
            self.rc_hit(bot.parse_edit(text), text)
        else:
            self.on_msg(channel, text, sender)

    def rc_hit(self, diff, raw):
        if 'page' in diff and diff['page'] in pages:
            bot = diff['user'] in AIVbots
            if not bot:
                self.pull.put((None, raw))
            parse_all(self, bot)
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
        elif text.startswith('!info'):
            username = ' '.join(text.split(' ')[1:])
            for line in all_info(username):
                self.pull.put((None, line))

push = Queue.Queue()
pull = Queue.Queue()
pull.put((None, 'Hello, I am a bot tracking https://en.wikipedia.org/wiki/Wikipedia:AIV'))
b = bot.Bot(push, pull, RcvThread, config)
b.run()
