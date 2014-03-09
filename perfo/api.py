import datetime
import flask
from perfo.models import db, App, Group, Event

bp = flask.Blueprint('api', __name__)

@bp.route('/apps/<app_id>/events', methods=['POST'])
def create_event(app_id):
    app = App.query.get_or_404(app_id)
    auth = flask.request.authorization
    if (not auth or
        not (app.api_key == auth.username and app.api_secret == auth.password)):
        flask.abort(401)
    data = flask.request.get_json()
    try:
        key = data['key']
        start_time, end_time = [datetime.datetime.utcfromtimestamp(int(t) / 1000.0) for t in data['t']]
    except:
        flask.abort(400)
    group = Group.query.filter_by(key=key).first()
    if not group:
        group = Group(app=app, key=key)
        db.session.add(group)
    group.events.append(Event(
        start_time=start_time,
        end_time=end_time,
    ))
    db.session.commit()
    return 'OK'
