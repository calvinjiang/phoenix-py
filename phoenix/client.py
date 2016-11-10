#####################################
# Author: Hua Jiang
# Date: 2016-08-12
# Desc:
# 
######################################

import os
import sys
import subprocess
import re
import logging
from collections import OrderedDict
import uuid
import phoenixdb
from phoenix.avatica import AmendedAvaticaClient
from phoenixdb.connection import Connection
from phoenixdb.cursor import Cursor
from phoenix.errors import (PhoenixUnfoundError,
                            PhoenixCommandExecuteError)


_logger = logging.getLogger(__name__)


class PhoenixClient(object):
    """PhoenixClicent may be looked as a wrapper of phoenixidb.

    You can create an object of PhoenixClicent,then execute most of phoenix sql
    by the class methods.

    Parameters
    ----------
    url : str
        URL to the Phoenix query server, e.g. ``http://localhost:8765/``
    max_retries : Optional[int]
        The maximum number of retries in case there is a connection error.
        Defaults 3.
    readonly : Optional[bool]
        Switch the connection to readonly mode.
        Defaults False.

    Raises
    ------
    ValueError
        If `url` is None or an empty string.
   
    Examples
    --------
    >>> from phoenix.client import PhoenixClient
    >>> client=PhoenixClient("http://192.168.223.123:8765/")
    >>> sql="select * from ADWISE_2_DIM_RESULT_HOUR where hour>=${var:shour} and hour<=${var:ehour} limit 20"
    >>> vars={}
    >>> vars['shour']='1'
    >>> vars['ehour']='10'
    >>> for row in client.fetch(vars=vars,sql=sql,maxRowCount=3):
    ...     print(row)
    ...
    [u'pre_adpos_creative', u'1', u'193972', 20160802, 1, 113036, 2266, 0, 113036, 69344, 69344, 65361, 1, 0, 38857, 38857, 0, 24163, 23330, 0, 0, 1, 0]
    [u'pre_adpos_creative', u'832', u'354370', 20160802, 2, 24, 0, 0, 24, 23, 23, 22, 0, 0, 14, 14, 0, 13, 12, 0, 0, 0, 0]
    [u'pre_adpos_creative', u'1', u'193972', 20160802, 2, 76326, 2221, 0, 76326, 42210, 42210, 40093, 0, 0, 28908, 28908, 0, 15822, 15289, 0, 0, 0, 0]

    >>> for row in client.fetch(sql_file='test.sql'):
    ...     print(row)
    ...
    [u'0', u'1', 20160726, 1105, 0, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]
    [u'pre_creative', u'245502', 20160622, 10, 10025, 1, 0, 10025, 3769, 3769, 3645, 23, 0, 7263, 7263, 7263, 3032, 2966, 2966, 0, 20, 0]
    [u'0', u'1', 20160730, 1, 0, 1, 0, 0, 0, 0, 0, None, None, None, None, None, None, None, None, None, None, None]
    [u'pre_creative', u'245502', 20160622, 11, 8562, 0, 0, 8562, 3250, 3250, 3167, 11, 0, 6349, 6349, 6349, 2648, 2595, 2595, 0, 11, 0]
    [u'0', u'127872', 20160726, 0, 0, 0, 0, 0, None, None, None, None, None, None, None, None, None, None, None, None, None, None]
    [u'pre_creative', u'245502', 20160622, 12, 7192, 0, 0, 7192, 2664, 2664, 2581, 11, 0, 5289, 5289, 5289, 2147, 2087, 2087, 0, 8, 0]

    """

    def __init__(self, url, max_retries=3, readOnly=False):
        if url is None or len(url) == 0:
            raise ValueError(
                "When you passed the argument of url,it should have a value.")

        self.url = url
        self.max_retries = max_retries
        self.autocommit = True
        self.readonly = readOnly
        self._client = AmendedAvaticaClient(url=url, max_retries=3)
        self._closed = True
        self._props = {}
        self._props['autocommit'] = self.autocommit
        self._props['readonly'] = self.readonly
        self._init_connect()

    def __del__(self):
        self.close()

    def _init_connect(self):
        if self._closed:
            self.open()

    def open(self):
        self._client.connect()
        self._connection = Connection(self._client,**self._props)
        self._conn_id = str(uuid.uuid4())
        self._client.openConnection(self._conn_id)
        self._closed = False

    def close(self):
        if not self._closed:
            if self._conn_id:
                self._client.closeConnection(self._conn_id)
                self._conn_id = None
            self._connection.close()
            self._client.close()
            self._closed = True

    def show_databases(self, pattern=None):
        "substitute for `show databases like '%pattern%'`"
        if pattern == "":
            pattern = None
        rs = self._client.getSchemas(catalog=None, schemaPattern=pattern)
        databases = []
        for element in rs['firstFrame']['rows']:
            databases.append(element[0])

        return databases

    def show_table_types(self):
        "returns a sequence of table type."

        rs = self._client.getTableTypes()
        types = []
        for element in rs['firstFrame']['rows']:
            if len(element) >= 1:
                types.append(element[0])

        return types

    def show_tables(self, db_pattern=None, table_pattern=None, types=['TABLE']):
        "substitute for `show tables like '%pattern%'`"

        if table_pattern is not None and len(table_pattern) == 0:
            raise ValueError(
                "this table_pattern value shouldn't be empty string.")

        if not isinstance(types, list):
            raise ValueError(
                "this types value should be a list.")

        rs = self._client.getTables(None, db_pattern, table_pattern, types)
        tables = []
        for element in rs['firstFrame']['rows']:
            if len(element) >= 3:
                tables.append(element[2])

        return tables

    def has_table(self, db_name, table_name, types=['TABLE']):
        tables = self.show_tables(db_pattern=db_name, types=types)
        for table in tables:
            if table == table_name:
                return True

        return False

    def desc_table(self, db_name, table_name):
        "returns a dict of columns"

        if not table_name:
            raise ValueError(
                "this table_name value shouldn't be empty string.")

        rs = self._client.getColumns(None, db_name, table_name, None)
        table_info = {"fields": []}

        for element in rs['firstFrame']['rows']:
            if len(element) >= 5:
                column_info = {}
                column_info['name'] = element[3]
                column_info['type'] = element[5]
                table_info['fields'].append(column_info)

        return table_info

    def fetch(self, sql=None, sql_file=None, maxRowCount=-1, vars=None,vars_pattern="${var:#value}"):
         # validate the parameters
        if vars and not isinstance(vars, dict):
            raise ValueError(
                "the function sql:The argument variable_substitution must be dict type.")

        if sql_file is None and sql is None:
            raise ValueError(
                "the function sql:At least one argument of sql_file and sql passed.")

        if sql_file and not os.path.exists(sql_file):
            raise ValueError(
                "The hive sql file:%s doesn't exists." % (sql_file))

        if sql_file:
            with open(sql_file, "r") as file:
                lines = file.readlines()
            sql = "".join(lines)

        if vars:
            for element in vars.items():
                var_key = vars_pattern.replace("#value", element[0])
                sql = sql.replace(var_key, element[1])

        _logger.info("fetch sql:%s" % (sql))
        count = 0
        cursor = self._connection.cursor()
        cursor.execute(sql)
        for row in cursor:
            row_codec=[]
            for x in row:
                if isinstance(x,unicode):
                    row_codec.append(x.encode("utf-8"))
                else:
                    row_codec.append(str(x))

            yield row_codec
            count += 1
            if maxRowCount>=0 and count>=maxRowCount:
                break

        cursor.close()
        return

    def execute(self, sql, seq_of_parameters=None):
        """this method can be used to execute phoenix sql.

        Parameters
        ----------
        sql : str
            The phoenix sql,if this parameter is required.
        seq_of_parameters : str
            The parameter is a list of tuple.

        """
        cursor = self._connection.cursor()
        _logger.debug("execute sql:%s,parameters:%s" % (sql,seq_of_parameters))

        if seq_of_parameters is None or len(seq_of_parameters)==0:
            cursor.execute(sql)
        else:
            cursor.executemany(sql, seq_of_parameters)
        cursor.close()
        return cursor.rowcount

