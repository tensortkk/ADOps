import logging

from flask import make_response
from flask_restful import Api
from werkzeug.wrappers import Response

from .query import Query
from .base import org_scoped_rule
from .cube import CubeDescriptor, CubeCol, CubeList
from .ad_setting import SettingSave, KylinRecomd, SettingProject, SettingID, ModelSave, ModelID
from .dask_yarn import DaskYarn, ModelDeploy, MonitorYarn

from server.util import json_dumps


logger = logging.getLogger(__name__)


class ApiExt(Api):
    def add_org_resource(self, resource, *urls, **kwargs):
        urls = [org_scoped_rule(url) for url in urls]
        return self.add_resource(resource, *urls, **kwargs)


api = ApiExt()


@api.representation("application/json")
def json_representation(data, code, headers=None):
    if isinstance(data, Response):
        return data
    resp = make_response(json_dumps(data), code)
    resp.headers.extend(headers or {})
    return resp


# query
api.add_org_resource(
    Query, "/kylin/api/query", endpoint="query"
)

# cube list
api.add_org_resource(
    CubeList, "/kylin/api/cubes", endpoint="cube_list"
)

# cube descriptor
api.add_org_resource(
    CubeDescriptor, "/kylin/api/cube_desc", endpoint="cube_desc"
)

# cube col enum
api.add_org_resource(
    CubeCol, "/kylin/api/cube_enum", endpoint="cube_enum"
)

# kylin recomd
api.add_org_resource(
    KylinRecomd, "/kylin/api/kylin_recomd/<mode>", endpoint="kylin_recomd"
)

# ad setting get by project
api.add_org_resource(
    SettingProject, "/kylin/api/ad_setting", endpoint="ad_setting_project"
)

# C ad setting
api.add_org_resource(
    SettingSave, "/kylin/api/ad_setting/<mode>", endpoint="ad_setting"
)

# RUD ad setting get by id
api.add_org_resource(
    SettingID, "/kylin/api/ad_setting/<mode>/<id>", endpoint="ad_setting_id"
)

# model setting
api.add_org_resource(
    ModelSave, "/kylin/api/model_setting", endpoint="model_setting"
)

# model setting get by id
api.add_org_resource(
    ModelID, "/kylin/api/model_setting/<id>", endpoint="model_setting_id"
)

# online/offline dask application
api.add_org_resource(
    DaskYarn, "/kylin/api/dask/<id>", endpoint="dask_yarn"
)

# model deployment
api.add_org_resource(
    ModelDeploy, "/kylin/api/model/<id>", endpoint="model_deploy"
)

# Intelligent Detection
api.add_org_resource(
    MonitorYarn, "/kylin/api/monitor/<id>", endpoint="monitor_yarn"
)