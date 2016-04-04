# -*- coding: utf-8 -*-
"""Project metadata
Information describing the project.
"""
import logging

__author__ = 'tarzan'
_logger = logging.getLogger(__name__)


# The package name, which is also the "UNIX name" for the project.
package = 'mysqlbinlog2gpubsub'
project = "MySQL binlog to Google Cloud Pub/Sub"
project_no_spaces = project.replace(' ', '')
version = '1.0'
description = 'Send MySQL binlog event to Google Cloud Pub/Sub'
authors = ['Tarzan', ]
authors_string = ', '.join(authors)
emails = ['hoc3010@gmail.com', ]
license = 'MIT'
copyright = '2016 ' + authors_string
url = ''
