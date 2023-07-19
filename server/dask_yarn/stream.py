import os, json, sys
from queue import Queue

import time
import datetime

# from dask_yarn import YarnCluster
# from dask.distributed import Client
from dask.distributed import Client, LocalCluster
from kafka import KafkaConsumer

from sqlalchemy import create_engine
import pandas as pd


with open("/work/adops/kafka/client_id") as f:
    client_id = f.read()

adops_mysql_url = f"mysql+pymysql://root:adops2023@{os.environ.get('HOST')}:3337/adops?charset=utf8"
engine = create_engine(adops_mysql_url, connect_args={'ssl': {'ssl-mode': 'disable'}})
create_sql = f"""
    CREATE TABLE IF NOT EXISTS `stream`(
        `alias` VARCHAR(64) NOT NULL,
        `extra_info` JSON NOT NULL,
        `ts` datetime NOT NULL
    )ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
with engine.begin() as conn:
    conn.execute(create_sql)


def mysql_data(sql):
    return pd.read_sql(sql, engine)


class DaskYarnDeploy(object):
    def __init__(self, setting):
        self.setting, self.res_d = setting, dict()
        lct_sql = f"""
            select consume_ts from dask_application
            where alias = '{sys.argv[1]}' limit 1"""
        if mysql_data(lct_sql).shape[0] == 0:
            self.consume_ts = (
                datetime.date.today() - datetime.timedelta(1)
            ).strftime("%Y-%m-%d 00:00:00")
        else:
            self.consume_ts = mysql_data(lct_sql).values.tolist()[0][0]

        engine.execute(f"""
            delete from stream where alias = '{sys.argv[1]}'
            and ts >= '{self.consume_ts}'""")

        # self.cluster = YarnCluster.from_current()
        # self.cluster.adapt(minimum=2, maximum=3)
        # self.client = Client(self.cluster)
        self.cluster = LocalCluster()
        self.cluster.scale(3)
        self.client = Client(self.cluster)

        # settings 配置
        self.consumer = KafkaConsumer(
            'adops',
            group_id=f"adops_{int(time.time())}",
            bootstrap_servers=["localhost:9092"],
            client_id=client_id,
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        )

    @staticmethod
    def ts_format(ts):
        return datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def min_format(ts):
        return datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M")

    @staticmethod
    def time_diff(st_ts, ed_ts):
        return (DaskYarnDeploy.min_format(ed_ts) - DaskYarnDeploy.min_format(st_ts)
        ).total_seconds()

    @staticmethod
    def compare(num0, num1, op):
        dict = {
            "greater": ">",
            "greater_equal": ">=",
            "less": "<",
            "less_equal": "<=",
        }
        if op in dict:
            op = dict[op]
        if op != "in" and op != "not in":
            if isinstance(num1, str):
                num1 = int(num1)
        if num0 >= num1 and op == ">=":
            return True
        if num0 > num1 and op == ">":
            return True
        if num0 <= num1 and op == "<=":
            return True
        if num0 < num1 and op == "<":
            return True
        if num0 == num1 and op == "=":
            return True
        if op != "in" and op != "not in":
            return False
        if num0 in list(eval(num1)) and op == "in":
            return True
        if num0 not in list(eval(num1)) and op == "not in":
            return True
        return False

    def cumulative_sum(self, data_j):
        print(data_j)
        delta, role_id, ts = [data_j[i] for i in [self.setting["montior"].lower(), "role_id", "minute"]]
        if role_id not in self.res_d:
            self.res_d[role_id] = {
                "total_delta": 0,
                "delta": Queue(maxsize=0),
                "ts": Queue(maxsize=0)
            }
        self.res_d[role_id]["total_delta"] += delta
        self.res_d[role_id]["delta"].put(delta)
        self.res_d[role_id]["ts"].put(ts)

        ts_diff = DaskYarnDeploy.time_diff(self.res_d[role_id]["ts"].queue[0], ts)
        total_delta = self.res_d[role_id]["total_delta"]
        if ts_diff <= self.setting["ts_thd"] * 60 and DaskYarnDeploy.compare(
            total_delta, self.setting["value_thd"], self.setting["op"]):
            engine.execute(f"""
                insert into stream (alias, extra_info, ts) VALUES 
                ('{self.setting['alias']}', '{json.dumps(data_j)}', '{ts}')""")

            # total_delta update
            earliest_delta = self.res_d[role_id]["delta"].get()
            self.res_d[role_id]["total_delta"] -= earliest_delta
        if ts_diff > self.setting["ts_thd"] * 60:
            earliest_delta = self.res_d[role_id]["delta"].get()
            ts = self.res_d[role_id]["ts"].get()
            self.res_d[role_id]["total_delta"] -= earliest_delta
            print(self.res_d[role_id]["total_delta"])
    
    def process(self, cr):
        filter_l = self.setting["filter"]
        for _data in cr:
            tmp = self.lower_case(_data)
            filter_judge = [
                DaskYarnDeploy.compare(tmp.get(item[0]), item[-1], item[1])
                for item in filter_l]
            if sum(filter_judge) != len(filter_judge):
                continue
            self.cumulative_sum(tmp)

    def lower_case(self, info):
        info_l = dict()
        for key, item in info.items():
            info_l[key.lower()] = item
        return info_l

    def deploy(self):
        while True:
            try:
                for message in self.consumer:
                    self.consume_ts = self.process([message.value])
            except Exception as e:
                print(e)
                self.consume_ts = (DaskYarnDeploy.ts_format(self.consume_ts) - datetime.timedelta(
                    minutes=self.setting["ts_thd"])).strftime("%Y-%m-%d %H:%M:%S")
                stop_sql = f"""
                    UPDATE dask_application SET consume_ts='{self.consume_ts}'
                    WHERE alias='{sys.argv[1]}';"""
                with engine.begin() as conn:
                    conn.execute(stop_sql)
                self.close()
                break

    def close(self):
        self.client.shutdown()


def main(alias):
    setting_sql = f"select setting from ad_setting where alias = '{alias}' limit 1"
    setting = eval(mysql_data(setting_sql).values.tolist()[0][0])
    setting["alias"] = alias

    dyd = DaskYarnDeploy(setting)
    dyd.deploy()


if __name__ == "__main__":
    alias = sys.argv[1]
    main(alias)
