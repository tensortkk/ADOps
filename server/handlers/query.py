import copy
from flask import request

from .base import BaseHandle, query_decorator
from server.util.json_schema import query_schema
from server.util.rest_api import KylinOpenApi
from server.util.utils import Validate


class Query(BaseHandle, KylinOpenApi, Validate):
    def __init__(self, engin="trino"):
        super(Query, self).__init__(request)
        KylinOpenApi.__init__(self)
        self.engin = engin
        self.query_d = {
            "engin": "spark",
            "kylin_status_code": 200,
            "error_msg": None
        }

    @query_decorator
    def post(self):
        params = self.json()
        query_s = copy.deepcopy(self.query_d)
        query_s.update({
            "sql": params.get("sql"),
            "projectName": params.get("projectName")
        })
        try:
            self.schema_validate(params, query_schema)
        except Exception:
            query_s.update({
                "kylin_status_code": 400,
                "error_msg": "Kylin Authorization Failed"
            })
            return dict(), query_s

        req, _ = self.kylin_query(body=params)
        return req, query_s
