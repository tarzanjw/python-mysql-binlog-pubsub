# -*- coding: utf-8 -*-
import logging
import pymysqlblinker
import pymysqlblinker.signals


__author__ = 'tarzan'
_logger = logging.getLogger(__name__)

@pymysqlblinker.signals.on_binlog_write
@pymysqlblinker.signals.on_binlog_update
@pymysqlblinker.signals.on_binlog_delete
def on_binlog_event(event, schema, table):
    data = event_filter.make_event_data(event)
    if data:
        meta, rows = data
        pubsub.publish_rows(rows, meta)


def start_publishing():
    from mysqlbinlog2gpubsub import config
    pymysqlblinker.start_replication(
        config.MASTER_MYSQL_DSN,
        binlog_pos_storage_filename=config.BINLOG_POS_FILENAME,
        only_schemas=config.REPLICATION_ONLY_SCHEMAS or None,
        only_tables=config.REPLICATION_ONLY_TABLES or None,
        connect_timeout=config.MASTER_CONNECT_TIMEOUT,
    )