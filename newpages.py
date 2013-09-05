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
#Aka legobot4
from __future__ import unicode_literals

from mtirc import lib
from mtirc import hooks

#TODO: Pull this list automatically
namespaces = ('Talk', 'User', 'User talk', 'Wikipedia', 'Wikipedia talk',
              'File', 'File talk', 'MediaWiki', 'MediaWiki talk', 'Template',
              'Template talk', 'Help', 'Help talk', 'Category', 'Category talk',
              'Portal', 'Portal talk', 'Book', 'Book talk', 'Education Program',
              'Education Program talk', 'TimedText', 'TimedText talk')

joined = False
channel = '##legoktm-newpages'


def run(**kw):
    if (kw['server'] != 'irc.wikimedia.org') or (kw['channel'] != '#en.wikipedia'):
        return
    edit = lib.parse_edit(kw['text'])
    if 'log' in edit:
        return
    if edit['new'] == 'N' and edit['patrolled'] == '!':
        if ':' in edit['page']:
            if edit['page'].split(':', 1)[0] in namespaces:
                #not mainspace
                return
        kw['bot'].queue_msg(channel, kw['text'])

def join(**kw):
    kw['bot'].servers['card.freenode.net'].join(channel)

hooks.add_hook('connected', 'newpages', join)
