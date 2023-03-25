import sys
import datetime
from datetime import timezone

import hashlib
import logging
import logging.config
from jsonschema import validate, ValidationError, SchemaError

from server import dir_path

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.FileHandler(
    f"{dir_path}/server.log", "a", encoding="utf-8")
handler2 = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)
logger.addHandler(handler2)


def genearte_md5(str):
    hl = hashlib.md5()
    hl.update(str.encode(encoding="utf-8"))
    return hl.hexdigest()


def logid_pro(projectName, logid, split=False):
    logid_pre = "_".join(projectName.split("luoge_")[-1].split("_")[::-1])
    if logid_pre not in logid:
        logid = logid_pre + "_" + logid
    elif split:
        logid = logid.split(logid_pre + "_")[-1]
    return logid


def dt_str(days_ago=30):
    now = datetime.datetime.now()
    ago = now - datetime.timedelta(days=days_ago)
    return ago.strftime("%Y-%m-%d"), now.strftime("%Y-%m-%d")


def ts_strf(ts):
    if isinstance(ts, str):
        ts = int(ts)
    elif ts >= 10 ** 10:
        ts = ts / (10 ** 3)
    return datetime.datetime.fromtimestamp(
        ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def yesterday(n=1):
    return (datetime.date.today() - datetime.timedelta(n)
    ).strftime("%Y-%m-%d")


def cube_list_pro(cubes_l):
    cube_j = {cube["name"]: list() for cube in cubes_l}
    [cube_j[cube["name"]].append([
        ts_strf(seg["date_range_start"]), ts_strf(seg["date_range_end"])
    ]) for cube in cubes_l for seg in cube["segments"]]
    for cube_name, seg_l in cube_j.items():
        if len(seg_l) <= 1:
            continue
        seg_l.sort(key=lambda x: x[0])
        _seg_l = list()
        for interval in seg_l:
            # 区间合并
            if _seg_l and _seg_l[-1][1] >= interval[0]:
                _seg_l[-1][1] = max(_seg_l[-1][1], interval[1])
            else:
                _seg_l.append(interval)
        cube_j[cube_name] = _seg_l
    return cube_j


class Validate(object):
    def type_validate(self, value, ty):
        if not isinstance(value, ty):
            raise TypeError("{} is {}, but should be {}".format(value, type(value), ty))

    def schema_validate(self, body, schema):
        try:
            if isinstance(body, list):
                [validate(item, schema) for item in body]
            else:
                validate(body, schema)
        except Exception as e:
            if isinstance(e, ValidationError):
                raise TypeError("content is in valid, error: {}".format(e.message))
            elif isinstance(e, SchemaError):
                raise TypeError("configmap_schema is in valid, error: {}".format(e.message))
            else:
                raise TypeError("error: {}".format(e))
