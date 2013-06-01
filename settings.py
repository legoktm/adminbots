import sys
import private

config = {

    # Connection info
    'network': 'card.freenode.net',
    'port': 6667,  # For both networks
    'channel': '##legoktm-bots',  # On freenode
    'chatter-channel': '##legoktm-bots-chatter',

    # RC feed info
    'rc_network': 'irc.wikimedia.org',  # RC feed network
    'rc_channel': ['#en.wikipedia'],

    # Identification info
    'nick': 'AIV',  # Both networks
    'name': 'Legoktm\'s tracker bot',  # Both networks

    # How many processing threads to start
    'threads': 5,

    # Cache file
    'cache_file': 'cache',

    # Whether to use memcache if possible
    'use_memcache': True,

    # How many seconds to wait in between reconnection attempts
    'reconnection_interval': 5,

    # NickServ information
    'authenticate': False,
    'ns_username': 'legobot',
    'ns_pw': private.ns_pw,

    # Whether to send debug information to the channel
    'debug': True,
}

# Change config via commandline
if '--debug' in sys.argv:
    config['debug'] = True
if '--file-cache' in sys.argv:
    config['use_memcache'] = False
if '--memcache' in sys.argv:
    config['use_memcache'] = True

