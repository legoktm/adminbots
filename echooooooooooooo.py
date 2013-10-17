#!/usr/bin/python

from mtirc import bot
from mtirc import hooks
from mtirc import settings
import pywikibot
from pywikibot.data import api
import time

channel = '##legoktm'

INIT = False
LOCAL_CACHE = {}
USERS = [u'Legobot', u'Legoktm']
LAST = 0

def init(**kw):
    global INIT
    if 'card.freenode.net' in kw['bot'].servers:
        kw['bot'].servers['card.freenode.net'].join(channel)
        INIT = True

hooks.add_hook('connected', 'echo', init)


def on_msg(**kw):
    global LAST, LOCAL_CACHE, INIT
    if not INIT:
        return True
    force = '!notifycount' in kw['text']
    if time.time() - LAST < 60 and not force:
        return True
    LAST = time.time()
    for username in USERS:
        site = pywikibot.Site('en', 'wikipedia', username)
        site.login()
        print username
        print 'Logged in as: {0}'.format(site.username())
        req = api.Request(site=site,
                          action='query',
                          meta='notifications',
                          notprop='list|count')
        data = req.submit()
        count = int(data['query']['notifications']['count'])
        print count
        if not (username in LOCAL_CACHE):
            LOCAL_CACHE[username] = -10
        if LOCAL_CACHE[username] < count or force:
            print 'queue msg'
            kw['bot'].queue_msg(channel, '{0}: You have {1} unread notifications '
                                         '(https://en.wikipedia.org/wiki/Special:Notifications)'.format(username, count))

        LOCAL_CACHE[username] = count
    return True

hooks.add_hook('on_msg', 'echo', on_msg)

if __name__ == '__main__':
    import channel_manager  # Loads hooks
    config = dict(settings.config)
    config['nick'] = 'echooo'
    config['connections']['card.freenode.net']['channels'] = ['##legoktm', '##legoktm-bots', '##legoktm-bots-chatter']
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
