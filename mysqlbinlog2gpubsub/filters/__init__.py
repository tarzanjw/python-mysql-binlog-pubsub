# coding=utf-8
import logging
import re

from mysqlbinlog2gpubsub import config
from mysqlbinlog2gpubsub.filters import factory


__author__ = 'Tarzan'
_logger = logging.getLogger(__name__)


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


class Filters(object):
    """ Handle a filters chain """
    def __init__(self, filters_conf):
        self._filters_conf = filters_conf
        self._table_filters = {}
        self._filters_by_pattern = {}

    def _get_filters_for_pattern(self, pattern):
        try:
            return self._filters_by_pattern[pattern]
        except KeyError:
            filters = []
            for fname, fconf in self._filters_conf[pattern].items():
                filters.append(factory.create_filter(fname, fconf))
            self._filters_by_pattern[pattern] = filters
            return filters

    def get_filters_for_table(self, table_name):
        try:
            return self._table_filters[table_name]
        except KeyError:
            filters = []
            for pattern, filters_conf in self._filters_conf.items():
                if re.match('^%s$' % pattern, table_name):
                    filters.extend(self._get_filters_for_pattern(pattern))
            self._table_filters[table_name] = filters
            return filters

    def apply(self, rows, meta):
        """ Apply filters on rows and meta

        Args:
            rows (list[dict]): rows
            meta (dict): meta

        Every changes that happen on rows and meta will remain
        """
        table_name = '%s.%s' % (meta['schema'], meta['table'])
        for f in self.get_filters_for_table(table_name):
            for i in reversed(range(len(rows))):
                if not f(rows[i]):
                    del rows[i]
            if not rows:
                return False
        return True

    def yield_rows(self, rows, meta):
        """ Yield a list of rows that satisfy the filters

        Returns:
            list[dict]
        """
        table_name = '%s.%s' % (meta['schema'], meta['table'])
        filters = self.get_filters_for_table(table_name)
        for row in rows:
            if all([f(row) for f in filters]):
                yield row