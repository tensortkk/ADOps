import os
from .helpers import parse_boolean


app_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROXIES_COUNT = int(os.environ.get("KYLIN_PROXIES_COUNT", "1"))
MULTI_ORG = parse_boolean(os.environ.get("KYLIN_MULTI_ORG", "false"))

kylin_server_address = f"http://{os.environ.get('HOST')}:7070"
kylin_authorization = "Basic QURNSU46S1lMSU4="
adops_mysql_url = f"mysql+pymysql://root:adops2023@{os.environ.get('HOST')}:3306/adops?charset=utf8"
