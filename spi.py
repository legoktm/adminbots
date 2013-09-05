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
from mtirc import hooks

channel = '#wikipedia-en-spi'


def init(**kw):
    kw['bot'].servers['card.freenode.net'].join(channel)

hooks.add_hook('connected', 'stalker', init)

pages = [
    'Wikipedia:Sockpuppet investigations',
    'Wikipedia talk:Sockpuppet investigations'
]

ignoreuser = [
    'Amalthea (bot)',
]

ignorepages = [
    'Wikipedia:Sockpuppet investigations/Cases/Overview',
]

def run(**kw):
    if kw['server'] == 'irc.wikimedia.org':
        edit = bot.parse_edit(kw['text'])
        if edit['page'].startswith(tuple(pages)) and \
                not (edit['page'] in ignorepages) and \
                not (edit['user'] in ignoreuser):
                kw['bot'].queue_msg(channel, kw['text'])
    return True
