from flask import request, abort
import datetime
import subprocess
import psutil

from .base import BaseHandle
from server import dir_path
from server.util.rest_api import KylinOpenApi
from server.util.utils import Validate, yesterday

from server.models import ADSetting, session_scope, DaskApplication


class DaskYarn(BaseHandle, KylinOpenApi, Validate):
    def __init__(self):
        super(DaskYarn, self).__init__(request)
        KylinOpenApi.__init__(self)

    def post(self, id):
        """start yarn application if not exist, or restart from stop time, online"""
        ad_s = ADSetting.get_by_id(id)
        params = ad_s.to_dict()
        if not DaskApplication.alias_exist(params["alias"]):
            summit_cmd = f"nohup python3 {dir_path}/dask_yarn/stream.py {params['alias']} &"
            subprocess.call(summit_cmd, shell=True)

            # pid_cmd = f"pgrep -f {params['alias']}"
            for proc in psutil.process_iter():
                if params["alias"] in proc.cmdline():
                    pid = proc.pid

            da = DaskApplication(
                alias=params["alias"],
                pid=pid,
                consume_ts=yesterday() + " 00:00:00")
        else:
            abort(404, f"{params['alias']} already exist")
        ad_s.online_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with session_scope() as session:
            session.add(da)
            session.add(ad_s)
            session.commit()
        return ad_s.to_dict()

    def delete(self, id):
        """stop and delete yarn application if exist, offline"""
        ad_s = ADSetting.get_by_id(id)
        params = ad_s.to_dict()
        if DaskApplication.alias_exist(params["alias"]):
            da = DaskApplication.get_by_alias(params["alias"])
            da_d = da.to_dict()
            subprocess.run(["kill", "-9", da_d["pid"]])
            with session_scope() as session:
                session.delete(da)
        ad_s.online_time = None
        with session_scope() as session:
            session.add(ad_s)
            session.commit()
        return ad_s.to_dict()
