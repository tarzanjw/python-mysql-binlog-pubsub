# -*- coding: utf-8 -*-
""" This module will convert a BinlogRowEvent to a dict data and meta data """
import logging
from pymysqlreplication import row_event
from . import config

__author__ = 'tarzan'
_logger = logging.getLogger(__name__)


def _get_event_action(event):
    if isinstance(event, row_event.WriteRowsEvent):
        return 'insert'
    if isinstance(event, row_event.UpdateRowsEvent):
        return 'update'
    if isinstance(event, row_event.DeleteRowsEvent):
        return 'delete'
    assert False, "Can not detect event action"


def _get_updated_values(before_values, after_values):
    """ Get updated values from 2 dict of values
    :param dict before_values: values before update
    :param dict after_values: values after update
    :return: a diff dict with key is field key, value is tuple of
    (before_value, after_value)
    :rtype: dict
    """
    assert before_values.keys() == after_values.keys()
    return dict([(k, [before_values[k], after_values[k]])
                 for k in before_values.keys()
                 if before_values[k] != after_values[k]])


class TableAdapter(object):
    def __init__(self, schema, table):
        self.schema = schema
        self.table = table
        self.prefix = config.TABLE_PREFIX.get(table, '')
        self.prefix_length = len(self.prefix)
        self.ignored_update_fields = \
            config.TABLE_IGNORED_UPDATE_FIELDS.get(table, [])

        if self.prefix_length:
            self.remove_prefix_for_list = self._do_remove_prefix_for_list
            self.remove_prefix_for_dict = self._do_remove_prefix_for_dict
        else:
            self.remove_prefix_for_list = self._do_nothing
            self.remove_prefix_for_dict = self._do_nothing
        if self.ignored_update_fields:
            self.remove_ignored_fields = self._do_remove_ignored_fields
        else:
            self.remove_ignored_fields = self._do_nothing
        self.key_fields = config.TABLE_PRIMARY_KEYS[self.table]

    def _do_nothing(self, val):
        return val

    def _do_remove_prefix_for_list(self, vals):
        return map(
            lambda v: v[self.prefix_length:] if v.startswith(self.prefix) else v,
            vals)

    def _do_remove_prefix_for_dict(self, data):
        return {
            k[self.prefix_length:] if k.startswith(self.prefix) else k: v
            for k, v in data.items()
        }

    def _do_remove_ignored_fields(self, data):
        return dict([(k, v)
                     for k, v in data.items()
                     if k not in self.ignored_update_fields])

    def refine_insert_row(self, row):
        return {
            'values': self.remove_prefix_for_dict(row['values'])
        }

    refine_delete_row = refine_insert_row

    def refine_update_row(self, row):
        updated_values = _get_updated_values(row['before_values'],
                                             row['after_values'])
        updated_values = self.remove_prefix_for_dict(updated_values)
        updated_values = self.remove_ignored_fields(updated_values)
        if not updated_values:
            return False
        return {
            'updated_values': updated_values,
            'values': self.remove_prefix_for_dict(row['after_values'])
        }

    def get_primary_key_values(self, row):
        vals = row['values']
        return dict([(pk, vals[pk]) for pk in self.key_fields])

    def make_data(self, event):
        """ Hàm này phục vụ các việc quyết định xem 1 binlog event có được bắn đi hay
        không? Nếu có thì dữ liệu bắn đi là gì?

        Các bước thực hiện như sau:

        1. Loại bỏ prefix của các field trên các rows dựa theo config.
        2. Loại bỏ các ignore field trong quá trình update.
        3. Loại bỏ các empty updated rows: các row được update nhưng không update field
           nào (sau khi đã loại bỏ bởi ignored fields).
        4. Trả về các not empty rows cùng `dbname` và `tbname`.

        Các row sau khi format sẽ có dạng:

        > Under construction

        :param pymysqlreplication.row_event.RowsEvent event: binlog event
        :return: False or (meta, rows)
        """
        raw_rows = event.rows
        event_action = _get_event_action(event)
        if event_action == 'insert':
            refine_func = self.refine_insert_row
        elif event_action == 'update':
            refine_func = self.refine_update_row
        elif event_action == 'delete':
            refine_func = self.refine_delete_row
        rows = []
        for r in raw_rows:
            r = refine_func(r)
            if not r:
                continue
            r['keys'] = self.get_primary_key_values(r)
            rows.append(r)

        if not rows:
            return False

        return ({
            'time': event.timestamp,
            'log_pos': event.packet.log_pos,
            'schema': self.schema,
            'table': self.table,
            'type': event_action,
        }, rows)


_event_data_makers = dict()


def get_event_data_maker(schema, table):
    global _event_data_makers
    schema_makers = _event_data_makers.setdefault(schema, {})
    try:
        data_maker = schema_makers[table]
    except KeyError:
        data_maker = TableAdapter(schema, table)
        schema_makers[table] = data_maker
    return data_maker


def make_event_data(event):
    """ This function make event data for a binlog event.

    The event data are rows and meta that contain data for rows and meta data
    the binlog event.

    Args:
        event (pymysqlreplication.row_event.RowsEvent): the binlog event

    Returns:
        tuple(rows, meta): The data that is made from event

        Where:

        **rows**


    Hàm này phục vụ các việc quyết định xem 1 binlog event có được bắn đi hay
    không? Nếu có thì dữ liệu bắn đi là gì?
    Các bước thực hiện như sau:

    1. Xuất phát từ event, đưa qua database mapping, table mapping để có `dbname` và
       `tbname` mới.
    2. Loại bỏ prefix của các field trên các rows dựa theo config.
    3. Loại bỏ các ignore field trong quá trình update.
    4. Loại bỏ các empty updated rows: các row được update nhưng không update field
       nào (sau khi đã loại bỏ bởi ignored fields).
    5. Trả về các not empty rows cùng `dbname` và `tbname`.

    Các row sau khi format sẽ có dạng:

    > Under construction

    :param pymysqlreplication.row_event.RowsEvent event: binlog event
    :return: False or (meta, rows)
    """
    # apply mappings
    schema = config.SCHEMA_NAME_MAPPINGS.get(event.schema, event.schema)
    table = config.TABLE_NAME_MAPPINGS.get(event.table, event.table)

    data_maker = get_event_data_maker(schema, table)
    return data_maker.make_data(event)
