#!/usr/bin/python
import glob
import json
import threading
import time

from mtirc import hooks


class SpamBot:
    def __init__(self):
        self.lastrun = time.time()
        self.interval = 60  # Check every minute
        self.lock = threading.Lock()
        self.chan = '##legoktm-bots-chatter'

    def on_hit(self, **kw):
        if self.interval + self.lastrun > time.time():
            return True
        got = self.lock.acquire(False)
        if not got:
            return True
        files = glob.glob('/data/project/legobot/*.err')
        with open('/data/project/legobot/errorstates.json') as f:
            data = json.load(f)
        for filename in files:
            with open(filename) as f:
                text = f.read()
            if filename in data:
                count = data[filename]
            else:
                count = -1  # Because indexes start at 0
            if len(text.splitlines()) <= count:
                continue
            for i, line in enumerate(text.splitlines()):
                if i > count:
                    kw['bot'].queue_msg(self.chan, line)
            data[filename] = count
        with open('/data/project/legobot/errorstates.json', 'w') as f:
            json.dump(data, f)
        self.lock.release()
        return True

instance = SpamBot()
hooks.add_hook('on_msg', 'spambot', instance.on_hit)

if __name__ == '__main__':
    # Populate errorstates.json so on start up we don't spam the shit out of ourselves
    files = glob.glob('/data/project/legobot/*.err')
    d = {}
    for filename in files:
        with open(filename) as f:
            d[filename] = len(f.read().splitlines())
    with open('/data/project/legobot/errorstates.json', 'w') as f:
        json.dump(d, f)
