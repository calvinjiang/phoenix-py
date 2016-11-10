

import uuid
import phoenixdb
database_url = 'http://192.168.223.199:8765/?v=1.6'
conn = phoenixdb.connect(database_url, autocommit=True)
cursor = conn.cursor()
#cursor.execute("CREATE TABLE users_test (id INTEGER PRIMARY KEY, username VARCHAR)")
cursor.executemany("UPSERT INTO users_test VALUES (?, ?)", [(4, 'admin'),(5,'aaa')])
cursor.execute("SELECT * FROM users_test")
print cursor.fetchall()




import uuid
import phoenixdb
client=phoenixdb.AvaticaClient(url="http://192.168.223.199:8765//?v=1.6",max_retries=3)
client.connect()
conn_id=str(uuid.uuid4())
client.openConnection(conn_id)
props={}
props['autoCommit']=False
props['readOnly']=True
client.connectionSync(conn_id,props)

operation="UPSERT INTO users_test VALUES (?, ?)"

statement=client.prepare(conn_id,operation, maxRowCount=0)
state_id=statement['id']

client.execute(conn_id,state_id,
                    [{'type':'INTEGER', 'value': 8},{'type':'STRING', 'value':'lianghong'}],
                    maxRowCount=0)

client.execute(conn_id,state_id,
                    [{'type':'INTEGER', 'value': 9},{'type':'STRING', 'value':'heshihui'}],
                    maxRowCount=0)


sql="select * from ADWISE_2_DIM_RESULT_HOUR limit 105"

request = {
    'request': 'prepare',
    'connectionId': conn_id,
    'sql': sql,
    'maxRowCount': 100,
}

results=client._apply(request)

results=client.prepare(conn_id,"select * from ADWISE_2_DIM_RESULT_HOUR limit 105",maxRowCount=50)
state_id=results['id']

rs=client.fetch(conn_id,state_id,None,offset=0,fetchMaxRowCount=15)

print(len(rs['rows']))



client.closeConnection(conn_id)

request = {'request': 'getCatalogs'}
rs=client._apply(request,'resultSet')

request = {
    'request': 'getTables',
    'catalog': None,
    'schemaPattern': None,
    'tableNamePattern': None,
    'typeList': ['TABLE','INDEX'],
}
rs=client._apply(request,'resultSet')

request = {
    'request': 'getSchemas',
    'catalog': None,
    'schemaPattern': None,
}
rs=client._apply(request,'resultSet')

request = {'request': 'getTableTypes'}
rs=client._apply(request,'resultSet')




def getColumns(self, catalog=None, schemaPattern=None, tableNamePattern=None, columnNamePattern=None):
       

	request = {
    'request': 'getSchemas',
    'catalog': None,
    'schemaPattern': 'a',
}


	request = {
    'request': 'getTables',
    'catalog': None,
    'schemaPattern': None,
    'tableNamePattern': None,
    'typeList': ['INDEX'],
}
	rs=client._apply(request,'resultSet')

def getTables(self, catalog=None, schemaPattern=None, tableNamePattern=None, typeList=None):

        return self._apply(request)

{u'updateCount': -1, u'statementId': -1, u'connectionId': u'00000000-0000-0000-0000-000000000000', u'ownStatement': True, u'signature': {u'cursorFactory': {u'style': u'LIST', u'fieldNames': None, u'clazz': None}, u'parameters': [], u'columns': [{u'ordinal': 0, u'caseSensitive': False, u'columnName': u'TABLE_CAT', u'scale': 0, u'searchable': True, u'nullable': 1, u'autoIncrement': False, u'definitelyWritable': False, u'tableName': u'SYSTEM.TABLE', u'precision': 0, u'signed': False, u'label': u'TABLE_CAT', u'writable': False, u'currency': False, u'readOnly': True, u'columnClassName': u'java.lang.String', u'displaySize': 40, u'schemaName': u'', u'type': {u'rep': u'STRING', u'type': u'scalar', u'id': 12, u'name': u'VARCHAR'}, u'catalogName': u''}], u'sql': None}, u'response': u'resultSet', u'firstFrame': {u'rows': [], u'done': True, u'offset': 0}}\


