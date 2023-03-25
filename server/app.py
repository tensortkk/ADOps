from flask import Flask
from werkzeug.contrib.fixers import ProxyFix

from . import settings


class Kylin(Flask):
    """A custom Flask app for portal"""

    def __init__(self, *args, **kwargs):
        super(Kylin, self).__init__(__name__, *args, **kwargs)
        # Make sure we get the right referral address even behind proxies like nginx.
        self.wsgi_app = ProxyFix(self.wsgi_app, settings.PROXIES_COUNT)
        # Configure portal using our settings
        self.config.from_object("server.settings")


def create_app():
    from . import handlers
    from .metrics import request as request_metrics
    from .models.base import get_engine, init_db
    from .models import init_db as start_db

    app = Kylin()
    init_db(get_engine())
    start_db(app)
    request_metrics.init_app(app)
    handlers.init_app(app)
    return app
