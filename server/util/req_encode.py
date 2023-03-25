import datetime
import numpy as np

from server.query_runner import SUPPORTED_COLUMN_TYPES
from server.query_runner.presto import PRESTO_TYPES_MAPPING
from server.query_runner.trino import TRINO_TYPES_MAPPING


class KylinEncoder(object):
    def __init__(self):
        self.types_mapping = {**PRESTO_TYPES_MAPPING, **TRINO_TYPES_MAPPING}

    def default(self, o, _type):
        if _type == "integer" and not isinstance(o, np.int):
            return int(o)
        elif _type == "float" and not isinstance(o, np.float):
            return float(o)
        elif _type == "boolean" and not isinstance(o, np.bool):
            return bool(o)
        elif _type == "string" and not isinstance(o, str):
            return str(o)
        elif _type == "date" and not isinstance(o, datetime.date):
            result = o.isoformat()
        elif _type == "datetime" and not isinstance(o, datetime.datetime):
            result = o.isoformat()
            if o.microsecond:
                result = result[:23] + result[26:]
            if result.endswith("+00:00"):
                result = result[:-6] + "Z"
            return result
        return o

    def encode(self, req):
        for index in range(len(req["columns"])):
            if req["columns"][index][-1] not in SUPPORTED_COLUMN_TYPES:
                continue
            for item in req["results"]:
                item[index] = self.default(item[index], req["columns"][index][-1])
        return req
