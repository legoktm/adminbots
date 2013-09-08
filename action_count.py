# -*- coding: utf-8 -*-
# (C) Legoktm, 2013
# Licensed under the MIT License

from mtirc import hooks
from wmflabs import db


def on_msg(**kw):
    text = kw['text']
    if not text.startswith(('!a', '!l')):
        return True
    sp = text.split(' ')
    if len(sp) < 3:
        kw['bot'].queue_msg(kw['channel'], '!(a|l) log_action username[@dbname]')
    type_ = sp[0][1]
    action = sp[1]
    username = sp[2]
    if '@' in username:
        dbname = username.split('@', 1)[1]
        username = username.split('@', 1)[0]
    else:
        dbname = 'enwiki'

    query = """
SELECT COUNT(*)
FROM logging_userindex
JOIN user
ON user_id=log_user
WHERE """
    if type_ == 'a':
        human = 'log actions'
        query += 'log_action = ?'
    else:
        human = 'log entries'
        query += 'log_type = ?'
    query += '\nAND user_name = ?;'

    with db.connect(dbname) as conn:
        with conn.cursor() as cur:
            cur.execute(query, (action, username))
            count = cur.fetchone()[0]

    kw['bot'].queue_msg(kw['channel'], '{0}@{1} has {2} {3} of type {4}'.format(
        username, dbname, count, human, type_
    ))
    return True

hooks.add_hook('on_msg', 'action_count', on_msg)