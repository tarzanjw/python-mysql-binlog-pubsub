#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""MySQL binlog to Google Pub/Sub entry point"""
from __future__ import print_function
import logging
import argparse
import sys
from mysqlbinlog2gpubsub import metadata


__author__ = 'tarzan'
_logger = logging.getLogger(__name__)


def _setup_arg_parser(argv):
    """ Parse arguments from command line
    Args:
        argv list: by default it's command line arguments

    Returns:
        argparse.Namespace: parsed argument
    """
    parser = argparse.ArgumentParser(description=metadata.project)
    parser.add_argument('conf',
                       help='configuration file for publishing')

    args = parser.parse_args(argv)
    return args


def main(argv):
    """ MySQL binlog to Google Pub/Sub entry point
    Args:
        argv (list): list of command line arguments
    """
    args = _setup_arg_parser(argv)

    from mysqlbinlog2gpubsub import config
    import mysqlbinlog2gpubsub

    config.import_from_python_file(args.conf)
    mysqlbinlog2gpubsub.start_publishing()


def entry_point():
    """Zero-argument entry point for use with setuptools/distribute."""
    raise SystemExit(main(sys.argv[1:]))


if __name__ == '__main__':
    entry_point()