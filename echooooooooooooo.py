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
SITES = [
    ('en', 'wikipedia'),
    ('mediawiki', 'mediawiki'),
    ('wikidata', 'wikidata'),
    ('meta', 'meta')
]
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
        for langproj in SITES:
            site = pywikibot.Site(langproj[0], langproj[1], username)
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
            if not (langproj in LOCAL_CACHE):
                LOCAL_CACHE[langproj] = {}
            if not (username in LOCAL_CACHE[langproj]):
                LOCAL_CACHE[langproj][username] = -10
            if LOCAL_CACHE[langproj][username] < count or force:
                print 'queue msg'
                link = 'https://' + site.hostname() + site.nice_get_address('Special:Notifications')
                kw['bot'].queue_msg(channel, '{0}@{1}: You have {2} unread notifications '
                                             '({3})'.format(username, site.dbName(), count, link))

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
