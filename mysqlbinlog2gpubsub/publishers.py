# coding=utf-8
""" This module define class Publisher that controls the publishing progress"""
import json
import logging

import collections

import re

import gcloud.pubsub
import jose.jwk
import jose.jws

from mysqlbinlog2gpubsub import config
from mysqlbinlog2blinker import signals
from mysqlbinlog2gpubsub import filters as _filters

__author__ = 'Tarzan'
_logger = logging.getLogger(__name__)


def _json_default(o):
    import datetime
    if isinstance(o, (datetime.datetime, datetime.date)):
        return o.isoformat()
    if isinstance(o, (tuple, set)):
        return list(o)
    return o


_json_encoder = json.JSONEncoder(default=_json_default)
json_dumps = _json_encoder.encode


class Publisher(object):
    """ Control a publishing progress, from tables' binlog event and send to
    a pubsub topic
    """
    def __init__(self, name, topic_name, jwt, signals=None,
                 schema_rename=None, table_rename=None,
                 filters=None):
        """
        Args:
            name (str):
            topic_name (str):
            jwt (dict[str, str]): JWT configuration, including algorithm and key
            signals (dict[str, list]):
            schema_rename (dict[str, str]):
            table_rename (dict[str, dict[str, str]])
            filters (dict[str, mixed])
        """
        self.__name__ = name
        self.topic_name_pattern = topic_name
        self.signals_conf = signals

        self.schema_rename = schema_rename
        self._schema_new_names = dict()  # type: dict[str, str]
        self.table_rename = table_rename
        self._table_new_names = dict()  # type: dict[tuple(str, str), str]

        self.filters = _filters.Filters(filters or {})
        self.pubsub_client = gcloud.pubsub.Client(
            project=config.pubsub_project_name)
        self.pubsub_topics = dict()
        self.jwt_alg = jwt['alg']
        self.jwt_key = jose.jwk.RSA.importKey(jwt['key'])


    def _get_pubsub_topic(self, meta):
        """Get pubsub topic that corresponding to an event

        Returns:
            gcloud.pubsub.topic.Topic: the topic
        """
        topic_name = self.topic_name_pattern % meta
        try:
            return self.pubsub_topics[topic_name]
        except KeyError:
            topic = self.pubsub_client.topic(topic_name)
            if not topic.exists():
                topic.create()
            self.pubsub_topics[topic_name] = topic
            return topic

    def _bind_to_rows_signals(self):
        if self.signals_conf:
            for table_name, actions in self.signals_conf.items():
                actions = actions or ['insert', 'update', 'delete']
                if 'insert' in actions:
                    signals.rows_inserted.connect(self.on_rows_signal,
                                                  sender=table_name)
                if 'update' in actions:
                    signals.rows_updated.connect(self.on_rows_signal,
                                                 sender=table_name)
                if 'delete' in actions:
                    signals.rows_deleted.connect(self.on_rows_signal,
                                                 sender=table_name)
        else:
            signals.rows_inserted.connect(self.on_rows_signal)
            signals.rows_updated.connect(self.on_rows_signal)
            signals.rows_deleted.connect(self.on_rows_signal)

    def _unbind_to_rows_signals(self):
        if self.signals_conf:
            for table_name, actions in self.signals_conf.items():
                actions = actions or ['insert', 'update', 'delete']
                if 'insert' in actions:
                    signals.rows_inserted.disconnect(self.on_rows_signal,
                                                  sender=table_name)
                if 'update' in actions:
                    signals.rows_updated.disconnect(self.on_rows_signal,
                                                 sender=table_name)
                if 'delete' in actions:
                    signals.rows_deleted.disconnect(self.on_rows_signal,
                                                 sender=table_name)
        else:
            signals.rows_inserted.disconnect(self.on_rows_signal)
            signals.rows_updated.disconnect(self.on_rows_signal)
            signals.rows_deleted.disconnect(self.on_rows_signal)

    def start(self):
        """Start listening signals"""
        self._bind_to_rows_signals()

    def stop(self):
        """Stop listening signals"""
        self._unbind_to_rows_signals()

    def _rename_schema(self, schema):
        """ Rename a schema name and return new name

        Args:
            schema (str): schema nae

        Returns:
            str
        """
        try:
            return self._schema_new_names[schema]
        except KeyError:
            new_name = schema
            for pattern, repl in self.schema_rename.items():
                new_name, subs_made = re.subn(pattern, repl, schema)
                if subs_made:
                    break

            self._schema_new_names[schema] = new_name
            return new_name

    def _rename_table(self, schema, table):
        """ Rename a table and rereturn new name

        Args:
            schema (str): schema name (the new one)
            table (str): table name

        Returns:
            str
        """
        try:
            return self._table_new_names[(schema, table)]
        except KeyError:
            new_name = table
            _rules = self.table_rename.get(schema, {})
            for pattern, repl in _rules.items():
                new_name, subs_made = re.subn(pattern, repl, table)
                if subs_made:
                    break

            self._table_new_names[(schema, table)] = new_name
            return new_name

    def on_rows_signal(self, table_name, rows, meta):
        meta['schema'] = self._rename_schema(meta['schema'])
        meta['table'] = self._rename_table(meta['schema'], meta['table'])

        for row in self.filters.yield_rows(rows, meta):
            self.publish_row_to_pubsub(row, meta)

    def _make_jwt(self, row, meta):
        return jose.jws.sign(row, key=self.jwt_key, algorithm=self.jwt_alg)

    def publish_row_to_pubsub(self, row, meta):
        topic = self._get_pubsub_topic(meta=meta)  # type: gcloud.pubsub.Topic
        meta = {
            str(k): str(v)
            for k, v in meta.items()
        }

        # make row is json competible
        row = json.loads(json_dumps(row))
        _logger.info('Publishing %s.%s.%s#%s to %s' % (
            meta['schema'],
            meta['table'],
            meta['action'],
            row['keys'],
            topic.name
        ))

        msg_data = self._make_jwt(row, meta)
        topic.publish(msg_data, **meta)


_publishers = dict()  # type: dict[str, Publisher]


def init_publishers():
    """Read configuration and initialize publishers"""
    global _publishers  # type: dict

    def _merge_publisher_conf(conf, default):
        """ Merge default publisher configuration to a specific conf

        Args:
            conf (dict[str, dict]):
            default (dict[str, dict):

        Returns:

        """
        conf = conf.copy()
        conf.setdefault('schema_rename', {})
        conf.setdefault('table_rename', {})
        conf.setdefault('filters', {})
        conf.setdefault('jwt', {})
        conf['schema_rename'].update(default.get('schema_rename', {}))
        conf['table_rename'].update(default.get('table_rename', {}))
        conf['filters'].update(default.get('filters', {}))
        conf['jwt'].update(default.get('jwt', {}))
        return conf

    default_publisher_conf = config.default_publisher_conf

    for p_name, p_conf in config.publishers.items():
        _publishers[p_name] = Publisher(
            p_name,
            **_merge_publisher_conf(p_conf, default_publisher_conf))

    for p in _publishers.values():
        p.start()