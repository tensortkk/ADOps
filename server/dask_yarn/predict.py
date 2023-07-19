import os, sys, json, requests
import time
import datetime

from dask.distributed import Client, LocalCluster
from kafka import KafkaConsumer

from sqlalchemy import create_engine
import pandas as pd

with open("/work/adops/kafka/client_id") as f:
    client_id = f.read()

adops_mysql_url = f"mysql+pymysql://root:adops2023@{os.environ.get('HOST')}:3337/adops?charset=utf8"
engine = create_engine(adops_mysql_url, connect_args={'ssl': {'ssl-mode': 'disable'}})
create_sql = f"""
    CREATE TABLE IF NOT EXISTS `model`(
        `alias` VARCHAR(64) NOT NULL,
        `extra_info` JSON NOT NULL,
        `ts` datetime NOT NULL
    )ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
with engine.begin() as conn:
    conn.execute(create_sql)

def mysql_data(sql):
    return pd.read_sql(sql, engine)

class ModelYarnDeploy(object):
    def __init__(self, alias, topic, url):
        self.alias, self.topic, self.url = alias, topic, url
        lct_sql = f"""
            select consume_ts from dask_application
            where alias = '{self.alias}' limit 1"""
        if mysql_data(lct_sql).shape[0] == 0:
            self.consume_ts = (
                datetime.date.today() - datetime.timedelta(1)
            ).strftime("%Y-%m-%d 00:00:00")
        else:
            self.consume_ts = mysql_data(lct_sql).values.tolist()[0][0]
        
        engine.execute(f"""
            delete from stream where alias = '{self.alias}'
            and ts >= '{self.consume_ts}'""")

        self.consumer = KafkaConsumer(
            self.topic,
            bootstrap_servers=["localhost:9092"],
            client_id=client_id,
            group_id=f"adops_{int(time.time())}",
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        )

        self.cluster = LocalCluster()
        self.cluster.scale(3)
        self.client = Client(self.cluster)
    
    def deploy(self):
        while True:
            try:
                for msg in self.consumer:
                    response = requests.post(self.url, json=msg.value)
                    print(response.text)
                    if response.text == '1':
                        engine.execute(f"""
                        insert into model (alias, extra_info, ts) VALUES
                        ('{self.alias}', '{json.dumps(msg.value)}', '{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}')""")
            except Exception as e:
                print(e)
                self.close()
    
    def close(self):
        self.client.shutdown()

def main():
    alias, topic, url =sys.argv[1], sys.argv[2], sys.argv[3]
    if ":" not in url:
        url = f"http://127.0.0.1:{url}/predict"
    model = ModelYarnDeploy(alias, topic, url)
    model.deploy()

if __name__ == "__main__":
    main()
  

    