# -*- coding: utf-8 -*-
import random
import os
import importlib.machinery

__author__ = 'tarzan'

MASTER_MYSQL_DSN = None
MASTER_CONNECT_TIMEOUT = 5

BINLOG_POS_FILENAME = None
BINLOG_POS_INTERVAL = 2.0

REPLICATION_ONLY_SCHEMAS = None
REPLICATION_ONLY_TABLES = None

SLAVE_SERVER_ID = random.randint(1000000000, 4294967295)
REPLICATION_BLOCKING = True
#
# SCHEMA_NAME_MAPPINGS = dict()
# TABLE_NAME_MAPPINGS = dict()
#
# TABLE_PREFIX = dict()
# TABLE_PRIMARY_KEYS = dict()
# TABLE_IGNORED_UPDATE_FIELDS = dict()
#
# PUBSUB_PROJECT_NAME = 'vnpapis'


def import_from_dict(conf_dict):
    """ Import settings from a dictionary
    Args:
        conf_dict (dict): settings to be imported
    """
    globals().update(conf_dict)


def import_from_python_file(file):
    """ parse a python file and import its properties as settings
    Args:
        file (str): path to python file

    Returns:

    """
    _conf_mod_loader = importlib.machinery.SourceFileLoader(
        __package__ + '_conf_module',
        file)
    _conf_mod = _conf_mod_loader.load_module()
    import_from_dict({
        k: getattr(_conf_mod, k)
        for k in dir(_conf_mod) if not k.startswith('_')
    })
