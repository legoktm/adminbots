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

# A quick debugging module

import json


def run(**kw):
    if kw['text'].startswith('!connections'):
        # lets clone it
        connections = dict(kw['bot'].config['connections'])
        for c in connections:
            if 'ns_pw' in connections[c]:
                del connections[c]['ns_pw']
        kw['bot'].queue_msg(kw['channel'], json.dumps(connections))
    elif kw['text'].startswith('!modules'):
        kw['bot'].queue_msg(kw['channel'], 'The following modules '
                                  'are loaded: ' +
                                  ', '.join(kw['bot'].config['modules'].keys()
                                            )
        )
    return True
