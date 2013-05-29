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

import irc.client as irclib
import re
import threading
import time
import Queue

# The following regexes are from bjweeks' & MZMcBride's snitch.py
# which is public domain
COLOR_RE = re.compile(r'(?:\x02|\x03(?:\d{1,2}(?:,\d{1,2})?)?)')
ACTION_RE = re.compile(r'\[\[(.+)\]\] (?P<log>.+)  \* (?P<user>.+) \*  (?P<summary>.+)')
DIFF_RE = re.compile(r'''
    \[\[(?P<page>.*)\]\]\        # page title
    (?P<patrolled>!|)            # patrolled
    (?P<new>N|)                  # new page
    (?P<minor>M|)                # minor edit
    (?P<bot>B|)\                 # bot edit
    (?P<url>.*)\                 # diff url
    \*\ (?P<user>.*?)\ \*\       # user
    \((?P<diff>(\+|-)\d*)\)\     # diff size
    ?(?P<summary>.*)             # edit summary
''', re.VERBOSE)


def parse_edit(msg):
    msg = COLOR_RE.sub('', msg)
    edit_match = DIFF_RE.match(msg)
    action_match = ACTION_RE.match(msg)
    match = edit_match or action_match
    if not match:
        return
    diff = match.groupdict()
    if not diff['summary']:
        diff['summary'] = '[none]'
    return diff


class ReceiveThread(threading.Thread):
    def __init__(self, queue, pull, config):
        threading.Thread.__init__(self)
        self.queue = queue
        self.pull = pull
        self.config = config

    def parse(self, channel, text, sender):
        #This should be sub-classed
        pass

    def debug(self, msg):
        if self.config['debug']:
            msg = unicode(msg)
            self.pull.put((None, u'DEBUG: ' + msg))

    def run(self):
        while True:
            channel, text, sender = self.queue.get()
            self.parse(channel, text, sender)
            self.queue.task_done()


class Bot:
    def __init__(self, push, pull, rcv, config, use_rc=True):
        self.irc = irclib.IRC()
        self.push = push  # Queue for incoming messages
        self.pull = pull  # Queue for outgoing messages
        self.rcv = rcv  # Thread class to parse incoming messages
        self.delay = 0  # When the last message was sent to the server
        self.delayTime = 1  # How long to wait in between sending
        self.use_rc = use_rc  # Whether to connect to the RC feed.
        self.config = config

    def on_msg(self, c, e):
        #print e.type
        #print e.arguments
        #print e.source
        #print e.target
        self.msg(e.target, e.arguments[0], e.source)

    def msg(self, channel, text, sender):
        #this is mainly a placeholder for other things
        self.push.put((channel, text, sender))

    def send_msg(self, channel, text):
        if not channel:
            channel = self.config['channel']
        d = time.time()
        if d - self.delay < self.delayTime:
            time.sleep(self.delayTime - (d - self.delay))
        self.delay = d
        if not isinstance(text, basestring):
            text = unicode(text)
        self.freenode.privmsg(channel, text)

    def get_version(self):
        # This should be improved
        return "IRCbotthing v0.1"

    def on_ctcp(self, c, e):
        """Default handler for ctcp events.

        Replies to VERSION and PING requests and relays DCC requests
        to the on_dccchat method.
        """
        nick = e.source.nick
        if e.arguments[0] == "VERSION":
            c.ctcp_reply(nick, "VERSION " + self.get_version())
        elif e.arguments[0] == "PING":
            if len(e.arguments) > 1:
                c.ctcp_reply(nick, "PING " + e.arguments[1])

    def auth(self):
        self.send_msg('nickserv', 'identify {0} {1}'.format(self.config['ns_username'], self.config['ns_pw']))

    def run(self):
        for i in range(0, self.config['threads']):
            t = self.rcv(self.push, self.pull, self.config)
            t.setDaemon(True)
            t.start()

        self.irc.add_global_handler('privmsg', self.on_msg)
        self.irc.add_global_handler('pubmsg', self.on_msg)
        self.irc.add_global_handler('ctcp', self.on_ctcp)


        self.freenode = self.irc.server()
        self.freenode.connect(self.config['network'], self.config['port'], self.config['nick'], self.config['name'])
        self.auth()
        self.freenode.join(self.config['chatter-channel'])
        self.freenode.join(self.config['channel'])

        if self.use_rc:
            self.rcfeed = self.irc.server()
            self.rcfeed.connect(self.config['rc_network'], self.config['port'], self.config['nick'], self.config['name'])
            self.rcfeed.join(self.config['rc_channel'])

        while True:
            self.irc.process_once(timeout=0.1)
            try:
                channel, text = self.pull.get(block=False)
                self.send_msg(channel, text)
            except Queue.Empty:
                pass
