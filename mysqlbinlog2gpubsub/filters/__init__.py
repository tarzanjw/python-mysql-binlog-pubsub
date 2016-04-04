# coding=utf-8
import logging
import re

from mysqlbinlog2gpubsub import config
from mysqlbinlog2gpubsub.filters import factory


__author__ = 'Tarzan'
_logger = logging.getLogger(__name__)


def rename_schema(schema):
    """ Map schema name to a new name
    Args:
        schema (str): name from

    Returns:
        str: to name
    """
    return config.schema_rename.get(schema, schema)


def rename_table(schema, table):
    return config.table_rename.get(schema, {}).get(table, table)


_table_filters = {}


def get_filters_for(table_name):
    """ Get list of filters for a table

    Args:
        table_name (str): table's name

    Returns:
        list[factory.BaseFilter]: list of filters
    """
    global _table_filters
    try:
        return _table_filters[table_name]
    except KeyError:
        filters = []
        for pattern, filters_conf in config.filters.items():
            if re.match('^%s$' % pattern, table_name):
                for fname, fconf in filters_conf.items():
                    filters.append(factory.create_filter(fname, fconf))
        _table_filters[table_name] = filters
        return filters


def apply_filters(rows, meta):
    """ Apply filters on rows and meta

    Args:
        rows (list[dict]): rows
        meta (dict): meta

    Every changes that happen on rows and meta will remain
    """
    # schema name mapping
    meta['schema'] = rename_schema(meta['schema'])
    meta['table'] = rename_table(meta['schema'], meta['table'])

    table_name = '%s.%s' % (meta['schema'], meta['table'])
    for f in get_filters_for(table_name):
        for i in reversed(range(len(rows))):
            if not f(rows[i]):
                del rows[i]
        if not rows:
            return False

    from pprint import pprint
    pprint(meta)
    pprint(rows)
    return True
