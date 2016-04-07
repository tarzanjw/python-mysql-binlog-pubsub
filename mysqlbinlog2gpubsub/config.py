# -*- coding: utf-8 -*-
import random
import gcloud._helpers
import yaml

__author__ = 'tarzan'


pubsub_project_name = None

mysql_settings = dict()

binlog_position_memory = (None, 2)

only_schemas = None
only_tables = None

schema_rename = dict()
table_rename = dict()

publishers = {}


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