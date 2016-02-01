# -*- coding: utf-8 -*-
import logging

__author__ = 'tarzan'
_logger = logging.getLogger(__name__)


def test_python_config_loading():
    import os
    import sys
    from mysqlbinlog2gpubsub import config

    conf_file = os.path.join(
        os.path.dirname(__file__),
        'conf_file_test.py',
    )

    config.import_from_python_file(conf_file)

    assert 'mysqlbinlog2gpubsub_conf_module' in sys.modules
    assert config.TEST_CONFIG_ARG == 'something special'
    assert config.MASTER_MYSQL_DSN == 'mysql://localhost?ab=cd'
