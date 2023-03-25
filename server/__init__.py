from __future__ import absolute_import

import os
from . import settings
from .app import create_app


__version__ = "v0.1.0"
__app__ = "kylin"
__import__("server.query_runner.presto", "server.query_runner.trino")
dir_path = os.path.dirname(os.path.realpath(__file__))
