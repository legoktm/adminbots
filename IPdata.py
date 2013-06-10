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

import hashlib
import requests
import sh


def _hash(a):
    return hashlib.md5(a).hexdigest()

commands = ('!info', '!rdns', '!geolocation')


def run(**kw):
    if not kw['text'].startswith(commands):
        return True
    sp = kw['text'].split(' ')
    command = sp[0]
    ip = sp[1]
    # TODO: Some kind of IP address validation should be here
    data = get_data(ip, kw['bot'])
    f = []
    if command in ['!info', '!rdns']:
        f += rDNS(data)
    if command in ['!info', '!geolocation']:
        f += geolocate(data)
    for line in f:
        kw['bot'].queue_msg(None, line)
    return True




def get_data(ip, bot):
    h = _hash(ip)
    if not h in bot.cache:
        data = fetch_info(ip)
        bot.cache.set(h, data)
    else:
        data = bot.cache.get(h)
    return data



def old_rDNS(ip):
    data = sh.dig('-x' , ip)
    return ['rDNS: ' + data.splitlines()[11].split('\t')[-1][:-1]]

#http://ip-api.com/json/122.111.244.202
#{"status":"success",
# "country":"Australia",
# "countryCode":"AU",
# "region":"08",
# "regionName":"Western Australia",
# "city":"Perth",
# "zip":"",
# "lat":"-31.9522","lon":"115.8614",
# "timezone":"Australia\/Perth",
# "isp":"Optus",
# "org":"Optus",
# "as":"AS4804 Microplex PTY LTD",
# "reverse":"d122-111-244-202.per801.wa.optusnet.com.au",
# "query":"122.111.244.202"}


def fetch_info(ip):
    r = requests.get('http://ip-api.com/json/' + ip)
    return r.json()


def rDNS(data):
    return ['rDNS: {reverse}'.format(**data)]

def geolocate(data):
    return ['Location: {city}, {regionName}, {country}. ISP: {isp}.'.format(**data)]