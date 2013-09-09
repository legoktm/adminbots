# -*- coding: utf-8 -*-
"""
This is a rewrite of snitch.

Originally written by MZMcBride and bjweeks.

Released into the public domain by Legoktm

Rules are stored in a json file at ~/rules.json

Format is: (in nice and pretty yaml :P)

"#en.wikipedia":
    - stalk:
        - user:
            - "user"
                - "##legoktm"
        - page:
            - "page"
        - summary:
            - "summary"
        - log:
            - "block"
    - ignore:
        - [same format as above]
"""

blank = {
    'stalk': {
        'user': {},
        'page': {},
        'summary': {},
        'log': {},
    },
    'ignore': {
        'user': {},
        'page': {},
        'summary': {},
        'log': {},
    },
}


help_msg = '!(stalk|ignore|unstalk|unignore)'

import json
import threading
import time
import os
import re

from mtirc import bot
from mtirc import hooks
from mtirc import lib
from mtirc import settings


class SnitchBot:

    def __init__(self):
        self.filename = os.path.expanduser('~/rules.json')
        self._cache = None
        self._cache_time = 0
        self.cache_expiry = 5 * 60
        self.lock = threading.Lock()  # For write operations

    def read_from_cache(self):
        """
        Attempt to read from the cache,
        if it hasn't expired yet
        """
        if time.time() - self._cache_time > self.cache_expiry:
            self.read()
        return self._cache

    def read(self):
        """
        Read from the source file, and update
        our cache since we loaded the data.
        """
        print 'Reading file.'
        with open(self.filename) as f:
            data = json.load(f)

        # Update our cache
        self._cache = data
        self._cache_time = time.time()

        return data

    def write(self, data):
        """
        Save the file to disk.
        Also reset our cache
        """
        print 'Saving to disk'
        self._cache = data
        self._cache_time = time.time()

        with open(self.filename, 'w') as f:
            #dump = yaml.dump(data, default_flow_style=False)
            #f.write(dump)
            json.dump(data, f, sort_keys=True, indent=4, separators=(',', ': '))

    def matches_rulset(self, ruleset, hit):
        """
        hit is a dict, returned by mtirc.lib.parse_edit
        returns a list of channels to notify
        """
        notify = set()
        for user in ruleset['user']:
            if re.match(user, hit['user']):
                notify = notify.union(set(ruleset['user'][user]))
        for summary in ruleset['summary']:
            if re.match(summary, hit['summary']):
                notify = notify.union(set(ruleset['page'][summary]))
        if 'page' in hit:
            for page in ruleset['page']:
                if re.match(page, hit['page']):
                    notify = notify.union(set(ruleset['page'][page]))
        if 'log' in hit:
            for log in ruleset['log']:
                if re.match(log, hit['log']):
                    notify = notify.union(set(ruleset['log'][log]))
        return notify

    def add_rule(self, rc_channel, action, subtype, regex, channel):
        """
        @param rc_channel: en.wikipedia
        @param action: stalk/ignore
        @param subtype: user/page/summary/log
        @param regex: .*
        @param channel: channel to notify
        @return: bool True if added, False if a dupe
        """
        self.lock.acquire()
        data = self.read()  # Want fresh stuff.
        if not rc_channel in data:
            data[rc_channel] = blank
        if regex in data[rc_channel][action][subtype]:
            if channel in data[rc_channel][action][subtype][regex]:
                self.lock.release()
                return False
            data[rc_channel][action][subtype][regex].append(channel)
        else:
            data[rc_channel][action][subtype][regex] = [channel]

        self.write(data)
        self.lock.release()
        return True

    def delete_rule(self, rc_channel, action, subtype, regex, channel):
        """
        @param rc_channel: en.wikipedia
        @param action: stalk/ignore
        @param subtype: user/page/summary/log
        @param regex: .*
        @param channel: channel to notify
        @return: bool True if removed, False if never existed
        """
        self.lock.acquire()
        data = self.read()
        if not rc_channel in data:
            self.lock.release()
            return False
        if regex in data[rc_channel][action][subtype]:
            if channel in data[rc_channel][action][subtype][regex]:
                data[rc_channel][action][subtype][regex].remove(channel)
                if not data[rc_channel][action][subtype][regex]:
                    # Remove empty rules
                    data[rc_channel][action][subtype].remove(regex)
            else:
                self.lock.release()
                return False
        else:
            self.lock.release()
            return False

        self.write(data)
        self.lock.release()
        return True

    def parse_hit(self, rc_channel, hit):
        notify = set()
        data = self.read_from_cache()
        if not rc_channel in data:
            return notify
        data = data[rc_channel]
        notify = notify.union(self.matches_rulset(data['stalk'], hit))
        ignore = self.matches_rulset(data['ignore'], hit)
        for chan in ignore:
            if chan in notify:
                notify.remove(chan)

        return notify

    def on_msg(self, **kw):
        if kw['server'] == 'irc.wikimedia.org':
            return self.on_rc_msg(kw['channel'], kw['text'], kw['bot'])
        if not kw['text'].startswith(('!stalk', '!ignore', '!unstalk', '!unignore', '!list')):
            return
        sp = kw['text'].split(' ')
        if len(sp) < 4:
            kw['bot'].queue_msg(kw['channel'], help_msg)
            return True
        do = sp[0][1:]
        rc_channel = sp[1]
        action = sp[2]
        regex = ' '.join(sp[3:])
        if do in ['stalk', 'ignore']:
            print 'Adding rule...'
            if self.add_rule(rc_channel, do, action, regex, kw['channel']):
                kw['bot'].queue_msg(kw['channel'], 'Rule added.')
            else:
                kw['bot'].queue_msg(kw['channel'], 'Rule already exists.')
        elif do in ['unstalk', 'unignore']:
            print 'Removing rule...'
            if self.delete_rule(rc_channel, do[2:], action, regex, kw['channel']):
                kw['bot'].queue_msg(kw['channel'], 'Rule deleted.')
            else:
                kw['bot'].queue_msg(kw['channel'], 'No rule found.')

    def on_rc_msg(self, rc_channel, text, bot):
        if not rc_channel in self.read_from_cache():
            return
        hit = lib.parse_edit(text)
        channels = self.parse_hit(rc_channel, hit)
        for chan in channels:
            bot.queue_msg(chan, text)
        return True


instance = SnitchBot()

hooks.add_hook('on_msg', 'snitch', instance.on_msg)

if __name__ == '__main__':
    import channel_manager  # Loads hooks
    config = dict(settings.config)
    config['nick'] = 'deepthroat'
    config['connections']['card.freenode.net']['channels'] = ['##legoktm-bots', '##legoktm-bots-chatter']
    config['connections']['irc.wikimedia.org'] = {
        'channels': [
            '#en.wikipedia',
        ],
        'authenticate': False,
    }

    config['default_channel'] = '##legoktm-bots-chatter'
    config['ns_username'] = 'legobot'
    import private
    config['ns_pw'] = private.ns_pw
    b = bot.Bot(config)
    print 'Running'
    b.run()
