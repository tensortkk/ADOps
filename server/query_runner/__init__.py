import logging
from server.util import json_loads

logger = logging.getLogger(__name__)

TYPE_INTEGER = "integer"
TYPE_FLOAT = "float"
TYPE_BOOLEAN = "boolean"
TYPE_STRING = "string"
TYPE_DATETIME = "datetime"
TYPE_DATE = "date"

SUPPORTED_COLUMN_TYPES = set(
    [TYPE_INTEGER, TYPE_FLOAT, TYPE_BOOLEAN, TYPE_STRING, TYPE_DATETIME, TYPE_DATE]
)

__all__ = [
    "BaseQueryRunner",
    "InterruptException",
    "TYPE_DATETIME",
    "TYPE_BOOLEAN",
    "TYPE_INTEGER",
    "TYPE_STRING",
    "TYPE_DATE",
    "TYPE_FLOAT",
    "register"
]

query_runners = {}


def register(query_runner_class):
    global query_runners

    logger.debug(
        "Registering %s (%s) query runner.",
        query_runner_class.name(),
        query_runner_class.type(),
    )
    query_runners[query_runner_class.type()] = query_runner_class


class BaseQueryRunner(object):
    deprecated = False
    should_annotate_query = True
    noop_query = None
    limit_query = " LIMIT 1000"
    limit_keywords = ["LIMIT", "OFFSET"]

    def __init__(self, configuration):
        self.syntax = "sql"
        self.configuration = configuration

    @classmethod
    def name(cls):
        return cls.__name__

    @classmethod
    def type(cls):
        return cls.__name__.lower()

    @classmethod
    def enabled(cls):
        return True

    @property
    def host(self):
        """Returns this query runner's configured host.
        This is used primarily for temporarily swapping endpoints when using SSH tunnels to connect to a data source.
        `BaseQueryRunner`'s naïve implementation supports query runner implementations that store endpoints using `host` and `port`
        configuration values. If your query runner uses a different schema (e.g. a web address), you should override this function.
        """
        if "host" in self.configuration:
            return self.configuration["host"]
        else:
            raise NotImplementedError()

    @host.setter
    def host(self, host):
        """Sets this query runner's configured host.
        This is used primarily for temporarily swapping endpoints when using SSH tunnels to connect to a data source.
        `BaseQueryRunner`'s naïve implementation supports query runner implementations that store endpoints using `host` and `port`
        configuration values. If your query runner uses a different schema (e.g. a web address), you should override this function.
        """
        if "host" in self.configuration:
            self.configuration["host"] = host
        else:
            raise NotImplementedError()

    @property
    def port(self):
        """Returns this query runner's configured port.
        This is used primarily for temporarily swapping endpoints when using SSH tunnels to connect to a data source.
        `BaseQueryRunner`'s naïve implementation supports query runner implementations that store endpoints using `host` and `port`
        configuration values. If your query runner uses a different schema (e.g. a web address), you should override this function.
        """
        if "port" in self.configuration:
            return self.configuration["port"]
        else:
            raise NotImplementedError()

    @port.setter
    def port(self, port):
        """Sets this query runner's configured port.
        This is used primarily for temporarily swapping endpoints when using SSH tunnels to connect to a data source.
        `BaseQueryRunner`'s naïve implementation supports query runner implementations that store endpoints using `host` and `port`
        configuration values. If your query runner uses a different schema (e.g. a web address), you should override this function.
        """
        if "port" in self.configuration:
            self.configuration["port"] = port
        else:
            raise NotImplementedError()

    @classmethod
    def configuration_schema(cls):
        return {}

    def annotate_query(self, query, metadata):
        if not self.should_annotate_query:
            return query

        annotation = ", ".join(["{}: {}".format(k, v) for k, v in metadata.items()])
        annotated_query = "/* {} */ {}".format(annotation, query)
        return annotated_query

    def test_connection(self):
        if self.noop_query is None:
            raise NotImplementedError()
        data, error = self.run_query(self.noop_query, None)

        if error is not None:
            raise Exception(error)

    def run_query(self, query, user):
        raise NotImplementedError()

    def fetch_columns(self, columns):
        column_names = []
        duplicates_counter = 1
        new_columns = []

        for col in columns:
            column_name = col[0]
            if column_name in column_names:
                column_name = "{}{}".format(column_name, duplicates_counter)
                duplicates_counter += 1

            column_names.append(column_name)
            new_columns.append(
                {"name": column_name, "friendly_name": column_name, "type": col[1]}
            )

        return new_columns

    def get_schema(self, get_stats=False):
        raise NotSupported()

    def _run_query_internal(self, query):
        results, error = self.run_query(query, None)

        if error is not None:
            raise Exception("Failed running query [%s]." % query)
        return json_loads(results)["rows"]

    @classmethod
    def to_dict(cls):
        return {
            "name": cls.name(),
            "type": cls.type(),
            "configuration_schema": cls.configuration_schema(),
            **({"deprecated": True} if cls.deprecated else {}),
        }

    @property
    def supports_auto_limit(self):
        return False

    def apply_auto_limit(self, query_text, should_apply_auto_limit):
        return query_text


class NotSupported(Exception):
    pass


class InterruptException(Exception):
    pass
