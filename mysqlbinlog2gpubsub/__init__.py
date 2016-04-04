# -*- coding: utf-8 -*-
import logging

import mysqlbinlog2blinker
import mysqlbinlog2blinker.signals
from mysqlbinlog2gpubsub import filters

__author__ = 'tarzan'
_logger = logging.getLogger(__name__)


def start_publishing():
    from mysqlbinlog2gpubsub import config
    mysqlbinlog2blinker.start_replication(
        mysql_settings=config.mysql_settings,
        binlog_pos_memory=config.binlog_position_memory,
        only_schemas=config.only_schemas,
        only_tables=config.only_tables,
    )


i = 0
@mysqlbinlog2blinker.signals.on_binlog
def limitor(event, stream):
    global i
    i += 1
    if i >= 2:
        raise SystemExit()


@mysqlbinlog2blinker.signals.on_rows_inserted
def on_rows_inserted(table_name, rows, meta):
    filters.apply_filters(rows, meta)


@mysqlbinlog2blinker.signals.on_rows_deleted
def on_rows_deleted(table_name, rows, meta):
    filters.apply_filters(rows, meta)


@mysqlbinlog2blinker.signals.on_rows_updated
def on_rows_updated(table_name, rows, meta):
    filters.apply_filters(rows, meta)