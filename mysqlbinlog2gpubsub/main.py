#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""MySQL binlog to Google Pub/Sub entry point"""
from __future__ import print_function
import logging
import logging.config
import argparse
import sys
import os


__author__ = 'tarzan'
_logger = logging.getLogger(__name__)


def _setup_arg_parser(argv):
    """ Parse arguments from command line
    Args:
        argv list: by default it's command line arguments

    Returns:
        argparse.Namespace: parsed argument
    """
    parser = argparse.ArgumentParser(
        description='MySQL binlog to Google Cloud Pub/Sub')
    parser.add_argument('conf',
                        help='configuration file for publishing')
    parser.add_argument('--log', '-l', default=None,
                        help='INI file to setup logging')

    args = parser.parse_args(argv)
    return args


_default_log_conf_file = os.path.join(os.path.dirname(__file__), 'logging.ini')


def main(argv):
    """ MySQL binlog to Google Pub/Sub entry point
    Args:
        argv (list): list of command line arguments
    """
    args = _setup_arg_parser(argv)
    conf_file = args.conf

    if conf_file:
        os.environ['BINLOG2GPUBSUB_CONF_FILE'] = conf_file

    log_conf_file = args.log or _default_log_conf_file
    logging.config.fileConfig(log_conf_file)

    import mysqlbinlog2gpubsub
    mysqlbinlog2gpubsub.start_publishing()


def entry_point():
    """Zero-argument entry point for use with setuptools/distribute."""
    raise SystemExit(main(sys.argv[1:]))


if __name__ == '__main__':
    entry_point()