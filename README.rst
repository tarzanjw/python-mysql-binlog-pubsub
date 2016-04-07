MySQL binlog to Google Cloud Pub/Sub
====================================

This package allows to send MySQL binlog to Google Cloud Pub/Sub. Each binlog
event will be sent as a message.

You can use this package as a library or a command line.

It use https://github.com/tarzanjw/python-mysql-binlog-to-blinker to get binlog
event as blinker's signal.


How it works?
-------------

1. First, use pymysqlbinlog2blinker to get binlog and send to blinker's signals.
2. Subscribes the right signals (depended on configuration).
3. Pass the signal through list of filters (filters can be configured). For i.e:
   It will remove column name's prefix, remove some sensitive columns. Rename
   the schema or table etc,
3. On each row, make a JWT for it.
4. Send the JWT value to the pubsub topic, topic's name can be configured.


How to use?
-----------

    .. code-block:: shell

        mysqlbinlog2gpubsub test_conf.yaml


Configuration file
------------------

Example file `example_conf.yaml <https://github.com/tarzanjw/python-mysql-binlog-pubsub/blob/master/example_conf.yaml`_