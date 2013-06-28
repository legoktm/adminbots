#!/usr/bin/env python
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

from mtirc import bot
from mtirc import settings
from mtirc import cache

# We need a persistent cache here,
# so lets set up a new instance

config = dict(settings.config)
config['use_memcache'] = False
config['cache_file'] = 'stalker'

CACHE = cache.Cache(config)
CACHE['loaded'] = False
if not 'stalk_these' in CACHE:
    CACHE['stalk_these'] = {}
if not 'channels' in CACHE:
    CACHE['channels'] = []


def run(**kw):
    #first lets check if we need to run the initalization sequence
    if not CACHE['loaded']:
        for c in CACHE['channels']:
            kw['bot'].servers[kw['server']].join(c)
    if kw['server'] == 'card.freenode.net':
        if kw['text'].startswith(kw['bot'].config['nick'] + ': !join'):
            if kw['sender'].host == 'wikipedia/Legoktm':
                channel = kw['text'].split(' ')[1]
                kw['bot'].servers[kw['server']].join(channel)
                t = list(CACHE['channels'])
                t.append(channel)
                CACHE['channels'] = t
                kw['bot'].queue_msg(kw['channel'], 'If you say so.')
        elif kw['text'].startswith(kw['bot'].config['nick'] + ': !part'):
            if kw['sender'].host == 'wikipedia/Legoktm':
                channel = kw['text'].split(' ')[1]
                if channel in CACHE['channels']:
                    t = list(CACHE['channels'])
                    t.remove(channel)
                    CACHE['channels'] = t
                    kw['bot'].send_msg(kw['channel'], 'Byeeee!')  # Jump the queue so the message gets sent
                    kw['bot'].servers[kw['server']].part(channel)
                else:
                    kw['bot'].queue_msg(kw['channel'], 'I\'m currently not in that channel.')

        elif kw['text'].startswith(kw['bot'].config['nick'] + ': !stalk'):
            username = ' '.join(kw['text'].split(' ')[1:])
            d = dict(CACHE['stalk_these'])
            if username in d:
                d[username].append(kw['channel'])
            else:
                d[username] = [kw['channel']]
            CACHE['stalk_these'] = d
            kw['bot'].queue_msg(kw['channel'], 'Added to stalk list.')
        elif kw['text'].startswith(kw['bot'].config['nick'] + ': !unstalk'):
            username = ' '.join(kw['text'].split(' ')[1:])
            d = dict(CACHE['stalk_these'])
            if username in d:
                del d[username]
                kw['bot'].queue_msg(kw['channel'], 'Removed from stalk list.')
            else:
                kw['bot'].queue_msg(kw['channel'], 'User was not on stalk list.')
            CACHE['stalk_these'] = d
    elif kw['server'] == 'irc.wikimedia.org':
        edit = bot.parse_edit(kw['text'])
        if edit['user'] in CACHE['stalk_these']:
            for c in CACHE['stalk_these'][edit['user']]:
                kw['bot'].queue_msg(c, kw['text'])
    return True