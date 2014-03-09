import datetime
import hashlib
import os
import shortuuid
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class App(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.UnicodeText, unique=True)
    api_key = db.Column(db.Text)
    api_secret = db.Column(db.Text)

    __table_args__ = (db.UniqueConstraint(api_key, api_secret), )

    def generate_key(self):
        self.api_key = shortuuid.uuid()
        self.api_secret = hashlib.sha256(os.urandom(20)).hexdigest()

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    app_id = db.Column(db.ForeignKey(App.id), nullable=False)
    key = db.Column(db.String, nullable=False, index=True)

    app = db.relationship(App, backref=db.backref('groups', lazy='dynamic'))

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.ForeignKey(Group.id), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, index=True)
    end_time = db.Column(db.DateTime, nullable=False)
    duration_ms = db.Column(db.Integer, nullable=False)

    group = db.relationship(Group, backref=db.backref('events', lazy='dynamic'))

    @db.validates('start_time', 'end_time')
    def validate_interval(self, key, value):
        start_time = value if key == 'start_time' else self.start_time
        end_time = value if key == 'end_time' else self.end_time
        if start_time and end_time:
            assert start_time <= end_time
            self.duration_ms = int((end_time - start_time).total_seconds() * 1000)
        return value

def aggregate_events(app, type, start_time, end_time=None):
    if end_time is None:
        end_time = datetime.datetime.utcnow()

    if type == 'duration_avg':
        aggregate = db.func.avg(Event.duration_ms)
    elif type == 'duration_sum':
        aggregate = db.func.sum(Event.duration_ms)
    elif type == 'throughput':
        aggregate = db.func.count(Event.id)

    group = Event.group_id
    raw_stat = aggregate.label('raw_stat')
    stats = (db.session.query(Group, raw_stat)
            .select_from(Event)
            .join(Group)
            .filter(Event.end_time >= start_time, Event.start_time <= end_time)
            .filter(Event.group.has(app=app))
            .group_by(group)
            .order_by(raw_stat.desc())
            .all())

    if type == 'duration_avg':
        for row in stats:
            row.raw_stat = int(row.raw_stat)
            if row.raw_stat < 1000:
                fmt = '{} ms'
            else:
                fmt = '{:.1f} s'
                row.raw_stat /= 1000.0
            row.stat = fmt.format(row.raw_stat)
    elif type == 'duration_sum':
        total = float(sum(row.raw_stat for row in stats))
        for row in stats:
            row.raw_stat = row.raw_stat / total
            row.stat = '{:.1%}'.format(row.raw_stat)
    elif type == 'throughput':
        length = float((end_time - start_time).total_seconds())
        for row in stats:
            row.raw_stat = round(row.raw_stat / length)
            row.stat = '{} RPS'.format(row.raw_stat)
    return stats
