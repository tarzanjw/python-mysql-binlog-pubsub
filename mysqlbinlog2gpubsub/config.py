# -*- coding: utf-8 -*-
import random
import gcloud._helpers
import yaml

__author__ = 'tarzan'


mysql_settings = {
    'host': 'localhost',
    'port': 33060,
    'user': 'binlog_publisher',
    'passwd': 'EWwjGWf9U346',
    'connect_timeout': 5,
}

binlog_position_memory = ('test.binlog.pos', 2)

only_schemas = None
only_tables = None

schema_rename = dict()
table_rename = dict()

filters = dict()


def _import_from_dict(conf_dict):
    """ Import settings from a dictionary
    Args:
        conf_dict (dict): settings to be imported
    """
    globals().update(conf_dict)


def _import_from_yaml_file(yaml_file):
    with open(yaml_file) as f:
        conf = yaml.safe_load(f)
    return _import_from_dict(conf)


def _load_config_from_environment():
    import os

    conf_file = os.environ['BINLOG2GPUBSUB_CONF_FILE']
    _import_from_yaml_file(conf_file)


_load_config_from_environment()