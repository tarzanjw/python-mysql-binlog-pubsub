# coding=utf-8
import logging

__author__ = 'Tarzan'
_logger = logging.getLogger(__name__)


class BaseFilter(object):
    def __init__(self, conf):
        self.conf = conf

    def __call__(self, row):
        raise NotImplementedError()

    apply = __call__


_registered_filter_classes = {}


def register_filter(name, cls):
    global _registered_filter_classes
    _registered_filter_classes[name] = cls


def create_filter(name, conf):
    """ Create a filter with conf

    Returns:
        BaseFilter
    """
    return _registered_filter_classes[name](conf)


class ColumnPrefixFilter(BaseFilter):
    def __init__(self, conf):
        super(ColumnPrefixFilter, self).__init__(conf)
        self.prefix = conf
        self.lprefix = len(self.prefix)

    def __call__(self, row):
        if not self.lprefix:
            return True
        prefix = self.prefix
        lprefix = self.lprefix
        for values in row.values():
            keys = list(values)
            for k in keys:
                if k.startswith(prefix):
                    values[k[lprefix:]] = values.pop(k)
        return True


class HideColumnsFilter(BaseFilter):
    def __init__(self, conf):
        super(HideColumnsFilter, self).__init__(conf)
        self._columns_names = self.conf

    def __call__(self, row):
        if not self._columns_names:
            return True
        for values in row.values():
            for col in self._columns_names:
                values.pop(col, None)
        return True


class VerifyChangingFilter(BaseFilter):
    def __init__(self, conf):
        super(VerifyChangingFilter, self).__init__(conf)
        self._ignore_columns = set(self.conf)

    def __call__(self, row):
        if not self._ignore_columns:
            return True
        updated_values = row.get('updated_values', None)  # type: dict
        if updated_values is None:
            return True

        return set(updated_values.keys()).issubset(self._ignore_columns)


register_filter('column_prefix', ColumnPrefixFilter)
register_filter('hide_columns', HideColumnsFilter)
register_filter('ignore_updated_columns', VerifyChangingFilter)