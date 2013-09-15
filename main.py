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

import private
from mtirc import bot
from mtirc import settings

import action_count
import aiv
import channel_manager
import debug
import IPdata
import newpages
import rfpp
#import spi
import stalker
import ufaa

config = settings.config

config['nick'] = 'legobot'
config['disable_on_errors'] = False  # aiv.py has issues
config['connections']['card.freenode.net']['channels'] = ['##legoktm-bots', '##legoktm-bots-chatter']
config['connections']['irc.wikimedia.org'] = {'channels': ['#en.wikipedia',
                                                           ],
                                              'authenticate': False,
                                              }
config['default_channel'] = '##legoktm-bots'
config['modules']['ufaa'] = ufaa.run
config['modules']['aiv'] = aiv.run
config['modules']['debug'] = debug.run
config['modules']['ipdata'] = IPdata.run
config['modules']['newpages'] = newpages.run
#config['modules']['spi'] = spi.run
config['modules']['stalker'] = stalker.run
config['modules']['rfpp'] = rfpp.parse
config['authenticate'] = True
config['ns_username'] = 'legobot'
config['ns_pw'] = private.ns_pw

#Cache
config['cache']['type'] = settings.CACHE_REDIS
config['cache']['host'] = 'tools-redis'

b = bot.Bot(config)
b.cache.set('uaa', [])
b.cache.set('aiv', [])
b.cache.set('rfpp', [])
b.run()
