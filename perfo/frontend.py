import datetime
import flask
from perfo.models import db, App, Group, aggregate_events

bp = flask.Blueprint('frontend', __name__)

@bp.before_request
def load_apps():
    flask.g.apps = App.query

@bp.route('/')
def index():
    return flask.render_template('index.html')

@bp.route('/apps/new')
def apps_new():
    return flask.render_template('apps/new.html')

@bp.route('/apps', methods=['POST'])
def apps_create():
    app = App(
        name=flask.request.form['name'],
    )
    app.generate_key()
    db.session.add(app)
    db.session.commit()
    return flask.redirect(flask.url_for('.app_index', app_id=app.id))

@bp.route('/apps/<app_id>')
def app_index(app_id):
    app = App.query.get_or_404(app_id)
    dsn = 'http://%s:%s@%s%s/api/apps/%d' % (app.api_key, app.api_secret, flask.request.host, flask.request.script_root, app.id)
    return flask.render_template('app/index.html',
        app=app,
        app_dsn=dsn,
    )

@bp.route('/apps/<app_id>/groups')
def app_groups(app_id):
    app = App.query.get_or_404(app_id)
    sort = flask.request.args.get('sort', 'duration_sum')
    limit = flask.request.args.get('limit', type=int, default=30)
    start_time = datetime.datetime.utcnow() - datetime.timedelta(minutes=limit)
    groups = aggregate_events(app, sort, start_time)
    return flask.render_template('app/groups.html',
        app=app,
        sort=sort,
        groups=groups,
    )

@bp.route('/apps/<int:app_id>/groups/<group_id>')
def app_group(app_id, group_id):
    group = Group.query.get_or_404(group_id)
    if group.app_id != app_id:
        flask.abort(404)
    return flask.render_template('app/group.html',
        app=group.app,
        group=group,
    )
