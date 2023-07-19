from flask import request, abort
import datetime
import subprocess
import psutil
import json

from .base import BaseHandle
from server import dir_path
from server.util.rest_api import KylinOpenApi
from server.util.utils import Validate, yesterday

from server.models import ADSetting, session_scope, DaskApplication, ModelSetting


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


class ModelDeploy(BaseHandle, KylinOpenApi, Validate):
    def __init__(self):
        super(ModelDeploy, self).__init__(request)
        KylinOpenApi.__init__(self)
    
    def post(self, id):
        ad_s = ModelSetting.get_by_id(id)
        params = ad_s.to_dict()
        if not DaskApplication.alias_exist(params["alias"]):
            schema = params["schema"]
            for i in range(len(schema)):
                schema[i]= ":".join(schema[i])
            schema = ",".join(schema)
            summit_cmd = f"nohup python3 {dir_path}/dask_yarn/predict_server.py -e {params['endpoint']} \
                -db {params['database']} -dp {params['deployment']} -m {params['model_path']} -t {params['model_type']} \
                -s {schema} -p {params['port']} -n {params['alias']}&"
            print(summit_cmd)
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
        ad_s = ModelSetting.get_by_id(id)
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
    
class MonitorYarn(BaseHandle, KylinOpenApi, Validate):
    def __init__(self):
        super(MonitorYarn, self).__init__(request)
        KylinOpenApi.__init__(self)
    
    def post(self, id):
        ad_s = ModelSetting.get_by_id(id)
        params = ad_s.to_dict()
        input = self.json()
        if not DaskApplication.alias_exist("m"+params["alias"]):
            summit_cmd = f"nohup python3 {dir_path}/dask_yarn/predict.py m{params['alias']} \
                {input['topic']} {params['port']} &"
            subprocess.call(summit_cmd, shell=True)
            
            # pid_cmd = f"pgrep -f {params['alias']}"
            for proc in psutil.process_iter():
                if ("m"+params["alias"]) in proc.cmdline():
                    pid = proc.pid
            
            da = DaskApplication(
                alias="m"+params["alias"],
                pid=pid,
                consume_ts=yesterday() + " 00:00:00")
        else:
            abort(404, f"m{params['alias']} already exist")
        ad_s.online_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with session_scope() as session:
            session.add(da)
            session.add(ad_s)
            session.commit()
        return ad_s.to_dict()
    
    def delete(self, id):
        ad_s = ModelSetting.get_by_id(id)
        params = ad_s.to_dict()
        if DaskApplication.alias_exist("m"+params["alias"]):
            da = DaskApplication.get_by_alias("m"+params["alias"])
            da_d = da.to_dict()
            subprocess.run(["kill", "-9", da_d["pid"]])
            with session_scope() as session:
                session.delete(da)
        return ad_s.to_dict()