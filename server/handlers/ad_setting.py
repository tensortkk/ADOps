from flask import request, abort
import datetime
import copy

from .base import BaseHandle, query_decorator
from server.util.json_schema import ad_setting, setting_project
from server.util.rest_api import KylinOpenApi
from server.util.utils import Validate

from server.models import ADSetting, session_scope, DaskApplication


class KylinRecomd(BaseHandle, KylinOpenApi, Validate):
    def __init__(self):
        super(KylinRecomd, self).__init__(request)
        KylinOpenApi.__init__(self)
        self.query_d = {
            "engin": "spark",
            "kylin_status_code": 200,
            "error_msg": None
        }

    def sql_assemble(self, mode, params):
        logid = params['logid']
        if params["op"] in ["greater_equal", "greater"]:
            column = f"percentile({params['montior']}, 0.99865)"
        else:
            column = f"percentile({params['montior']}, 0.00135)"

        filter = list()
        for item in params['filter']:
            filter.append(" ".join(item))
        filter =  "where " + " and ".join(filter) if len(filter) != 0 else ""
        if mode == "single":
            sql = f"""select {column} as kylin_recomd
                from {logid} {filter}"""
        elif mode == "stream":
            sql = f"""select {column} as kylin_recomd
                from {logid} {filter}"""
        else:
            sql = f"""select {column} as kylin_recomd
                from (
                    select sum({params['montior']}) as {params['montior']}, role_id
                    from {logid} {filter}
                    group by role_id
                )t"""
        return sql

    @query_decorator
    def post(self, mode):
        params = self.json()
        assert mode in ad_setting
        self.schema_validate(params, ad_setting[mode])
        query_s = copy.deepcopy(self.query_d)
        query_s.update({
            "sql": params.get("sql"),
            "projectName": params.get("projectName")
        })

        sql = self.sql_assemble(mode, params)
        params.update({"sql": sql})
        req, _ = self.kylin_query(body=params)

        params.update({"value_thd": req["results"][0][0]})
        return req, query_s


class SettingSave(BaseHandle, KylinOpenApi, Validate):
    def __init__(self):
        super(SettingSave, self).__init__(request)
        KylinOpenApi.__init__(self)

    def post(self, mode):
        params = self.json()
        assert mode in ad_setting
        self.schema_validate(params, ad_setting[mode])

        if "value_thd" not in params:
            abort(404, "value_thd not in params")
        if ADSetting.name_exist(params["name"]):
            abort(405, f"Already exists {params['name']}")

        alias = "_".join(["dask"] + [
            params[col] if isinstance(params[col], str) else str(params[col])
            for col in ["logid", "montior", "value_thd"]])
        if ADSetting.alias_exist(alias):
            alias += "_" + datetime.date.today().strftime("%Y-%m-%d %H:%M:%S")

        ad_s = ADSetting(
            projectName=params["projectName"],
            mode=mode,
            name=params["name"],
            alias=alias,
            setting=params
        )
        with session_scope() as session:
            session.add(ad_s)
            session.commit()
        return ad_s.to_dict()


class SettingProject(BaseHandle, KylinOpenApi, Validate):
    def __init__(self):
        super(SettingProject, self).__init__(request)
        KylinOpenApi.__init__(self)

    def get(self):
        params = self.args()
        self.schema_validate(params, setting_project)

        page = 1 if "page" not in params else params["page"]
        page_size = 10 if "page_size" not in params else params["page_size"]
        ad_ss = ADSetting.get_by_project(
            params.get("projectName"), page, page_size)
        return [ad_s.to_dict() for ad_s in ad_ss]


class SettingID(BaseHandle, KylinOpenApi, Validate):
    def __init__(self):
        super(SettingID, self).__init__(request)
        KylinOpenApi.__init__(self)

    def get(self, mode, id):
        ad_s = ADSetting.get_by_id(id)
        return ad_s.to_dict()

    def post(self, mode, id):
        """stop and delete yarn application if exist and update setting"""
        params = self.json()
        assert mode in ad_setting
        self.schema_validate(params, ad_setting[mode])

        if DaskApplication.id_exist(id):
            da = DaskApplication.get_by_id(id).to_dict()
            # delete
            with session_scope() as session:
                session.delete(da)

        ad_s = ADSetting.get_by_id(id)
        ad_s.name = params["name"]
        ad_s.setting = params
        ad_s.update_time = datetime.datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S")
        ad_s.online_time = None
        with session_scope() as session:
            session.add(ad_s)
            session.commit()
        return ad_s.to_dict()

    def delete(self, mode, id):
        """stop and delete yarn application if exist and delete setting"""
        ad_s = ADSetting.get_by_id(id)
        params = ad_s.to_dict()
        if DaskApplication.alias_exist(params["alias"]):
            da = DaskApplication.get_by_alias(params["alias"])
            # delete
            with session_scope() as session:
                session.delete(da)
        with session_scope() as session:
            session.delete(ad_s)
