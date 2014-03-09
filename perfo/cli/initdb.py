# -*- coding: utf-8 -*-
import datetime
import random
from perfo.cli import main, parser
from perfo.models import db, App, Group, Event

parser.add_argument('--test', action='store_true')

def run(app, args):
    if args.test:
        db.drop_all()
        db.create_all()
        generate_test_data()
    else:
        db.create_all()

def generate_test_data():
    a = App(name='perfo')
    a.generate_key()
    db.session.add(a)
    for key in 'app_index', 'apps_group':
        g1 = Group(key='perfo.frontend.' + key, app=a)
        db.session.add(g1)
        now = datetime.datetime.utcnow()
        for x in xrange(10000):
            now -= datetime.timedelta(milliseconds=random.randrange(30 * 60 * 1000))
            delta = datetime.timedelta(milliseconds=random.randrange(10000))
            e = Event(group=g1, start_time=now, end_time=now + delta)
            db.session.add(e)
    db.session.commit()

if __name__ == '__main__':
    main(run)
