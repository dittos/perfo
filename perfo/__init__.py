import os
import flask
from perfo import frontend, api
from perfo.models import db

def create_app(config=None):
    app = flask.Flask(__name__)
    if isinstance(config, basestring):
        app.config.from_pyfile(os.path.abspath(config))
    else:
        if config is None:
            config = {}
        app.config.from_object(config)
    db.init_app(app)
    app.register_blueprint(frontend.bp)
    app.register_blueprint(api.bp, url_prefix='/api')
    return app
