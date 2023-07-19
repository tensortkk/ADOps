import argparse
import json
import numpy as np
import requests
import tornado.ioloop
import tornado.web
from xgboost.sklearn import XGBClassifier
import logging

logging.basicConfig(encoding="utf-8", level=logging.INFO, format="%(asctime)s-%(name)s-%(levelname)s-%(message)s")

arg_keys = ["endpoint", "database", "deployment", "model_path"]
bst = XGBClassifier()
# schema column type, ref hybridse::sdk::DataTypeName
table_schema = []
url = ""

table_schema = [
    ("ip", "int"),
    ("app", "int"), 
    ("device", "int"), 
    ("os", "int"), 
    ("channel", "int"), 
    ("click_time", "timestamp"), 
    ("attributed_time", "timestamp"), 
    ("is_attribute", "int"),
]

url = ""


def get_schema():
    dict_schema_tmp = {}
    for i in table_schema:
        dict_schema_tmp[i[0]] = i[1]
    return dict_schema_tmp


dict_schema = get_schema()
json_schema = json.dumps(dict_schema)

def build_feature(res):
    """
    The first value in list is the label column, it's dummy.
    Real-time feature has it, cuz the history data in OpenMLDB is the training data too.
    It'll have this column, but no effect to feature extraction.

    :param res: an OpenMLDB reqeust response
    :return: real feature
    """
    # col label is dummy, so start from 1
    return np.array([res[1:]])


class SchemaHandler(tornado.web.RequestHandler):
    def get(self):
        json_schema = json.dumps(table_schema)
        self.write(json_schema)


def request_row_cvt(json_row):
    """
    convert json to array, using table schema
    APIServer request format only has array now
    :param json_row: row in json format
    :return: array
    """
    row_data = []
    for col in table_schema:
        if col[1] == "string":
            row_data.append(json_row.get(col[0], ""))
        elif col[1] == "int" or col[1] == "double" or col[1] == "timestamp" or col[1] == "bigint":
            row_data.append(json_row.get(col[0], 0))
    logging.info("request row: %s", row_data)
    return row_data


def get_result(response):
    result = json.loads(response.text)
    logging.info("request result: %s", result)
    return result["data"]["data"]


class PredictHandler(tornado.web.RequestHandler):
    """Class PredictHandler."""
    def post(self):
        # only one row
        row = json.loads(self.request.body)
        data = {"input": [request_row_cvt(row)]}
        # request to OpenMLDB
        response = requests.post(url, json=data)

        # result is a list, even we just do a single request
        for res in get_result(response):
            ins = build_feature(res)
            logging.info(f"feature: {res}")
            # self.write("real-time feature:\n" + str(res) + "\n")
            prediction = bst.predict(ins)
            # self.write(
            #    "---------------predict whether is attributed -------------\n")
            self.write(f"{str(prediction[0])}")
            logging.info(f"prediction: {prediction}")


class MainHandler(tornado.web.RequestHandler):
    """Class of MainHandler."""
    def get(self):
        self.write("real time fe request demo\n")



def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/schema", SchemaHandler),
        (r"/predict", PredictHandler),
    ])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--endpoint", help="specify the endpoint of apiserver", default="localhost:9080")
    parser.add_argument("-m", "--model_path", help="specify the model path", default="/work/adops/saved_models/xgbmodel.json")
                            
    args = parser.parse_args()
    url = f"http://{args.endpoint}/dbs/adops/deployments/d1"
    bst.load_model(fname=args.model_path)
    global_args = vars(args)
    print(global_args)
    logging.info("init args: %s", global_args)

    app = make_app()
    app.listen(8881)
    tornado.ioloop.IOLoop.current().start()