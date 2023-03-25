import time
import datetime

import json
from flask import Blueprint, abort, jsonify
from flask_restful import Resource

from server import settings
from server.settings import helpers
from server.models.query_history import QueryHistory
from server.models import session_scope


routes = Blueprint(
    "kylin", __name__,
    template_folder=helpers.fix_assets_path("templates")
)


def query_decorator(func):
    def wrapper(*args, **kw):
        st = time.time()
        req, query_s = func(*args, **kw)

        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        run_time = time.time() - st
        query_s.update({
            "ts": ts,
            "runtime": round(run_time, 4)
        })
        qh = QueryHistory(**query_s)
        with session_scope() as session:
            session.add(qh)
            session.commit()
        if query_s.get("error_msg") is not None:
            return jsonify({"error_msg": query_s.get("error_msg")}), 500
        return req

    return wrapper


class BaseHandle(Resource):
    def __init__(self, request, *args):
        self.request = request

    def args(self):
        return dict(self.request.args.items())

    def files(self):
        return self.request.files

    def form(self):
        return dict(self.request.form.items())

    def data(self):
        return json.loads(self.request.data)

    def json(self):
        return self.request.get_json(True)


def require_fields(req, fields):
    for f in fields:
        if f not in req:
            abort(400, f"{f} required")


def org_scoped_rule(rule):
    if settings.MULTI_ORG:
        return "/<org_slug>{}".format(rule)

    return rule
