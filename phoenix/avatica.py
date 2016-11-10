#! /usr/bin/env python
# coding=UTF-8

from phoenixdb.avatica import AvaticaClient

class AmendedAvaticaClient(AvaticaClient):

    def __init__(self,url, version=None, max_retries=None):
        super(AmendedAvaticaClient,self).__init__(url, version,max_retries)

    def getCatalogs(self):
        request = {'request': 'getCatalogs'}
        return self._apply(request,'resultSet')

    def getSchemas(self, catalog=None, schemaPattern=None):
        request = {
            'request': 'getSchemas',
            'catalog': catalog,
            'schemaPattern': schemaPattern,
        }
        return self._apply(request,'resultSet')

    def getTables(self, catalog=None, schemaPattern=None, tableNamePattern=None, typeList=None):
        request = {
            'request': 'getTables',
            'catalog': catalog,
            'schemaPattern': schemaPattern,
            'tableNamePattern': tableNamePattern,
            'typeList': typeList,
        }
        return self._apply(request,'resultSet')

    def getColumns(self, catalog=None, schemaPattern=None, tableNamePattern=None, columnNamePattern=None):
        request = {
            'request': 'getColumns',
            'catalog': catalog,
            'schemaPattern': schemaPattern,
            'tableNamePattern': tableNamePattern,
            'columnNamePattern': columnNamePattern,
        }
        return self._apply(request,'resultSet')

    def getTableTypes(self):
        request = {'request': 'getTableTypes'}
        return self._apply(request,'resultSet')

    def getTypeInfo(self):
        request = {'request': 'getTypeInfo'}
        return self._apply(request,'resultSet')
