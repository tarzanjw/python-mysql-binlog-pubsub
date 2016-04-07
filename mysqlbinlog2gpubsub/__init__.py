# -*- coding: utf-8 -*-
import logging

import mysqlbinlog2blinker
import mysqlbinlog2blinker.signals


__author__ = 'tarzan'
_logger = logging.getLogger(__name__)


def start_publishing():
    from mysqlbinlog2gpubsub import config
    from mysqlbinlog2gpubsub import publishers

    publishers.init_publishers()
    mysqlbinlog2blinker.start_replication(
        mysql_settings=config.mysql_settings,
        binlog_pos_memory=config.binlog_position_memory,
        only_schemas=config.only_schemas,
        only_tables=config.only_tables,
    )