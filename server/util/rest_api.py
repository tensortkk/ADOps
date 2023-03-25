import json
import requests

from server.util.req_encode import KylinEncoder
from server.settings import (
    kylin_server_address,
    kylin_authorization
)


class KylinOpenApi(KylinEncoder):
    def __init__(self):
        super(KylinOpenApi, self).__init__()
        self.url = f"{kylin_server_address}/kylin/api/query"
        self.headers = {
            "Authorization": kylin_authorization,
            "Content-Type": "application/json;charset=utf-8"
        }

    def __name__(self):
        return self.__class__.__name__.lower()

    def __parse__(self, req):
        sc = req.status_code
        if sc == 204 and req.method == "delete":
            return
        elif sc == 200:
            req = req.json()
            req["columns"] = [
                [
                    item.get("label").lower(),
                    self.types_mapping.get(item.get("columnTypeName").lower(), None)
                ] for item in req["columnMetas"]
            ]
            req = {k: v for k, v in req.items() if k in ["results", "columns"]}
            req = self.encode(req)
        return req, sc

    def kylin_query(self, method="POST", params={}, body=None):
        project = body["projectName"] = body.get("projectName").lower()
        body["project"] = project
        body["sql"] = body["sql"].replace(project, f"{project}_view")

        response = requests.request(
            method, url=self.url, headers=self.headers,
            params=params, data=json.dumps(body) if isinstance(body, dict) else body
        )
        return self.__parse__(response)

    def req(self, url, method, params={}, body=None):
        return requests.request(
            method, url=f"{kylin_server_address}/{url}", headers=self.headers,
            params=params, data=json.dumps(body) if isinstance(body, dict) else body
        )
