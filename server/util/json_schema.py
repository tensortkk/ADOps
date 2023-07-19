cube_build = {
    "type": "object",
    "properties": {
        "projectName":  {"type": "string"},
        "startTime": {"type": "string"},
        "endTime": {"type": "string"},
        "buildType": {"type": "string"}
    },
    "required": ["projectName", "startTime", "endTime", "buildType"],
    "additionalProperties": False
}

query_schema = {
    "type": "object",
    "properties": {
        "sql":  {"type": "string"},
        "projectName": {"type": "string"}
    },
    "required": ["sql", "projectName"],
    "additionalProperties": False
}

cube_list = {
    "type": "object",
    "properties": {
        "projectName":  {"type": "string"},
        "mode": {"enum": ["single", "stream", "bounded_stream"]},
        "offset": {"type": "integer"},
        "limit": {"type": "integer"},
        "logid": {"type": "string"}
    },
    "required": ["projectName"],
    "additionalProperties": False
}

cube_desc = {
    "type": "object",
    "properties": {
        "projectName":  {"type": "string"},
        "logid": {"type": "string"},
        "mode": {"enum": ["single", "stream", "bounded_stream"]}
    },
    "required": ["projectName", "logid"],
    "additionalProperties": False
}

cube_col = {
    "type": "object",
    "properties": {
        "projectName":  {"type": "string"},
        "logid": {"type": "string"},
        "colName": {"type": "string"},
        "mode": {"enum": ["single", "stream", "bounded_stream"]}
    },
    "required": ["projectName", "logid", "colName"],
    "additionalProperties": False
}

ad_setting = {
    "single": {
        "type": "object",
        "properties": {
            "projectName": {"type": "string"},
            "logid":  {"type": "string"},
            "montior": {"type": "string"},
            "auxiliary_field": {"type": "array"},
            "value_thd": {"type": "number"},
            "op": {"enum": ["greater_equal", "greater", "less_equal", "less"]},
            "filter": {"type": "array"},
            "name": {"type": "string"},
        },
        "required": ["projectName", "logid", "montior", "op", "name"],
        "additionalProperties": False
    },
    "stream": {
        "type": "object",
        "properties": {
            "projectName": {"type": "string"},
            "logid":  {"type": "string"},
            "montior": {"type": "string"},
            "auxiliary_field": {"type": "array"},
            "ts_thd":  {"type": "number"},
            "value_thd": {"type": "number"},
            "aggregation": {"enum": ["sum"] },
            "op": {"enum": ["greater_equal", "greater", "less_equal", "less"]},
            "filter": {"type": "array"},
            "name": {"type": "string"},
        },
        "required": ["projectName", "logid", "montior", "op", "name"],
        "additionalProperties": False
    },
    "bounded_stream": {
        "type": "object",
        "properties": {
            "projectName": {"type": "string"},
            "logid":  {"type": "string"},
            "montior": {"type": "string"},
            "auxiliary_field": {"type": "array"},
            "period": {"enum": ["day"] },
            "st_ts": {"type": "string"},
            "value_thd": {"type": "number"},
            "aggregation": {"enum": ["sum"] },
            "op": {"enum": ["greater_equal", "greater", "less_equal", "less"]},
            "filter": {"type": "array"},
            "name": {"type": "string"},
        },
        "required": ["projectName", "logid", "montior", "period", "op", "name"],
        "additionalProperties": False
    }
}

setting_project = {
    "type": "object",
    "properties": {
        "projectName":  {"type": "string"},
        "mode": {"enum": ["single", "stream", "bounded_stream"]},
        "id":  {"type": "integer"},
        "page": {"type": "integer"},
        "page_size": {"type": "integer"}
    },
    "required": ["projectName"],
    "additionalProperties": False
}

model_setting = {
    "type": "object",
    "properties": {
        "endpoint":  {"type": "string"},
        "model_path": {"type": "string"},
        "model_type": {"enum": ["keras", "xgboost"]},
        "database": {"type": "string"},
        "deployment": {"type": "string"},
        "port": {"type": "string"},
        "schema": {"type": "array"},
    },
    "required": ["endpoint", "model_path", "model_type", "database", "deployment", "schema"],
    "additionalProperties": False
}
