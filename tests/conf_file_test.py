# -*- coding: utf-8 -*-

TEST_CONFIG_ARG = 'something special'

MASTER_MYSQL_DSN = 'mysql://localhost?ab=cd'
MASTER_CONNECT_TIMEOUT = 5

BINLOG_POS_FILENAME = None
BINLOG_POS_INTERVAL = 2.0

REPLICATION_ONLY_SCHEMAS = None
REPLICATION_ONLY_TABLES = None

SLAVE_SERVER_ID = 1102
REPLICATION_BLOCKING = True

SCHEMA_NAME_MAPPINGS = {
    'test_db0': 'db0',
}
TABLE_NAME_MAPPINGS = {
    'tbl0_shard_a': 'tbl0',
}

TABLE_PREFIX = {
    'tbl0': 'tbl_',
}
TABLE_PRIMARY_KEYS = {
    'tbl0': ['id', ]
}
TABLE_IGNORED_UPDATE_FIELDS = {
    'tbl0': [
        'desc',
    ]
}
