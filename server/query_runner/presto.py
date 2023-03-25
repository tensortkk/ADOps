from server.util import json_dumps, json_loads
from server.query_runner import (
    TYPE_INTEGER,
    TYPE_FLOAT,
    TYPE_BOOLEAN,
    TYPE_STRING,
    TYPE_DATE,
    BaseQueryRunner,
    register,
    InterruptException
)

try:
    import prestodb.dbapi as presto
    from pyhive.exc import DatabaseError

    enabled = True

except ImportError:
    enabled = False

PRESTO_TYPES_MAPPING = {
    "integer": TYPE_INTEGER,
    "tinyint": TYPE_INTEGER,
    "smallint": TYPE_INTEGER,
    "long": TYPE_INTEGER,
    "bigint": TYPE_INTEGER,
    "float": TYPE_FLOAT,
    "double": TYPE_FLOAT,
    "boolean": TYPE_BOOLEAN,
    "string": TYPE_STRING,
    "varchar": TYPE_STRING,
    "date": TYPE_DATE,
}


class Presto(BaseQueryRunner):
    noop_query = "SHOW TABLES"

    @classmethod
    def configuration_schema(cls):
        return {
            "type": "object",
            "properties": {
                "host": {"type": "string"},
                "protocol": {"type": "string", "default": "http"},
                "port": {"type": "number"},
                "schema": {"type": "string"},
                "catalog": {"type": "string"},
                "username": {"type": "string"},
                "password": {"type": "string"},
            },
            "order": [
                "host",
                "protocol",
                "port",
                "username",
                "password",
                "schema",
                "catalog",
            ],
            "required": ["host"],
        }

    @classmethod
    def enabled(cls):
        return enabled

    @classmethod
    def type(cls):
        return "presto"

    def get_schema(self, get_stats=False):
        schema = {}
        query = """
        SELECT table_schema, table_name, column_name
        FROM information_schema.columns
        WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
        """

        results, error = self.run_query(query, None)

        if error is not None:
            raise Exception("Failed getting schema.")

        results = json_loads(results)

        for row in results["rows"]:
            table_name = "{}.{}".format(row["table_schema"], row["table_name"])

            if table_name not in schema:
                schema[table_name] = {"name": table_name, "columns": []}

            schema[table_name]["columns"].append(row["column_name"])

        return list(schema.values())

    def run_query(self, query, project=None):
        connection = presto.connect(**self.configuration)
        cursor = connection.cursor()

        try:
            query = query.replace(project, f"hive.{project}")
            cursor.execute(query)
            rows = cursor.fetchall()
            column_tuples = [
                (i[0], PRESTO_TYPES_MAPPING.get(i[1], None)) for i in cursor.description
            ]
            data = {"results": rows, "columns": column_tuples}
            json_data = json_dumps(data)
            error = None
        except DatabaseError as db:
            json_data = None
            default_message = "Unspecified DatabaseError: {0}".format(str(db))
            if isinstance(db.args[0], dict):
                message = db.args[0].get("failureInfo", {"message", None}).get(
                    "message"
                )
            else:
                message = None
            error = default_message if message is None else message
        except (KeyboardInterrupt, InterruptException):
            cursor.cancel()
            raise
        except Exception:
            cursor.cancel()
            raise

        return json_data, error


register(Presto)
