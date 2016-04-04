# -*- coding: utf-8 -*-
import functools
import json
import logging
import gcloud.pubsub
from mysqlbinlog2gpubsub import config

__author__ = 'tarzan'
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


pubsub_client = gcloud.pubsub.Client(project=config.PUBSUB_PROJECT_NAME)


def publish_rows(topic_name, rows, meta):
    topic = pubsub_client.topic(topic_name)

    rows_message = json_dumps(rows).encode('utf-8')
    attrs = {
        k: str(v)
        for k, v in meta.items()
    }

    _logger.debug('Publish %d rows to topic "%s"' % (len(rows), topic_name))
    topic.publish(rows_message, **attrs)