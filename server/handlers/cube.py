import json
import copy
from flask import request, abort

from .base import BaseHandle, query_decorator
from server.util.rest_api import KylinOpenApi
from server.util.utils import Validate, cube_list_pro
from server.util.json_schema import cube_desc, cube_col, cube_list


class CubeList(BaseHandle, KylinOpenApi, Validate):
    def __init__(self):
        super(CubeList, self).__init__(request)
        KylinOpenApi.__init__(self)

    def get(self):
        """List cubes"""
        params = self.args()
        self.schema_validate(params, cube_list)

        req = self.req(
            url="/kylin/api/cubes", method="GET", params=params)
        if req.status_code != 200:
            abort(req.status_code)
        return cube_list_pro(json.loads(req.text))


class CubeDescriptor(BaseHandle, KylinOpenApi, Validate):
    def __init__(self):
        super(CubeDescriptor, self).__init__(request)
        KylinOpenApi.__init__(self)

    def dimen_measure(self, cube):
        cube_d = {col: list() for col in ["dimensions", "measures"]}
        for item in cube["dimensions"]:
            cube_d["dimensions"].append(item["column"])
        for item in cube["measures"]:
            # default agg
            if item["name"] == "_COUNT_":
                continue
            cube_d["measures"].append(
                item["function"]["parameter"]["value"].split(".")[-1])
        cube_d["measures"] = list(set(cube_d["measures"]))
        return cube_d

    def get(self):
        params = self.args()
        self.schema_validate(params, cube_desc)

        req = self.req(
            url=f"/kylin/api/cube_desc/{params.get('logid')}", method="GET")
        if req.status_code != 200:
            abort(req.status_code)
        if len(json.loads(req.text)) == 0:
            abort(404, f"{params.get('logid')} not exist")
        cube_d = self.dimen_measure(json.loads(req.text)[0])
        return cube_d


class CubeCol(BaseHandle, KylinOpenApi, Validate):
    def __init__(self):
        super(CubeCol, self).__init__(request)
        KylinOpenApi.__init__(self)
        self.query_d = {
            "engin": "spark",
            "kylin_status_code": 200,
            "error_msg": None
        }

    @query_decorator
    def get(self):
        params = self.args()
        self.schema_validate(params, cube_col)
        query_s = copy.deepcopy(self.query_d)
        query_s.update({
            "sql": params.get("sql"),
            "projectName": params.get("projectName")
        })

        sql = f"""
            select {params['colName']} from {params['logid']}
            group by {params['colName']}"""
        params.update({"sql": sql})
        req, _ = self.kylin_query(body=params)
        print(sql, req, query_s)
        return req, query_s
