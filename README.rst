=========================
Skyfront
=========================

Skyfront is a lightweight sql frontend.
Purpose of skyfront is to give simple uniform interface to SQL backend.
It is **not another orm**, just query generator.

Usage
=========================

Skyfront may works in two modes: as SQL frontend and as query generator.

Frontend
=========================

At first you need to setup backend and database connection. Just import
module and initialize SQL class from it with backend name as first
argument and database parameters as others. All database arguments
directly passed to your backend **connect** method. Only sqlite and mysql
backend are supported yet.

>>> import skyfront
>>> sql = skyfront.SQL('sqlite', 'test.sqlite')

.. _executeQuery:

Query execution
-------------------------

After database connection mades, you can execute queries through
**executeQuery** class method. This method takes 2 arguments: query
string as first and action type as second. Method return list of two
values: execution status as bool and returned data. Action type is
"*select*" by defalt. It affects on the return value. Only two types
available now: "*select*" and "*insert*", "*select*" returns cursor
fetchall result and insert returns last row id. All module basic
functions returns result of this function unless otherwise noted.

>>> sql.executeQuery("""CREATE TABLE IF NOT EXISTS `test` (
                            id INTEGER PRIMARY KEY autoincrement,
                            name VARCHAR UNIQUE,
                            title VARCHAR NOT NULL,
                            text VARCHAR NOT NULL)""")
[True, []]

.. _insertNew:

Records insertion
-------------------------

For add new record to the database you can use **insertNew** method.
First argument of this function is a database table name. Second argument
is array of field names which needs to be updated on duplicate key (if
it supported by backend).
Other arguments must be keyword arguments where key - field name and
value is field value wich needs to be added to database.

>>> sql.insertNew('test', None, name='Alabama', title='AL', text='Audemus jura nostra defendere')
[True, 1]
>>> sql.insertNew('test', None, name='Alaska', title='AK', text='North to the future')
[True, 2]
>>> sql.insertNew('test', None, name='Arizona', title='AZ', text='Ditat Deus')
[True, 3]
>>> sql.insertNew('test', None, name='Arkansas', title='AR', text='Regnat populus')
[True, 4]
>>> sql.insertNew('test', None, name='California', title='CA', text='Eureka')
[True, 5]

.. _getRecords:

Records selection
-------------------------

For select records you can use **getRecords** method.
First argument of this function is a database table name.
Arguments:

:select:   List of fields which will be selected
           ('*' will be used if not given).
:limit:    Query results count which will be returned.
:limstart: First record from which limit counts.
:order:    Name of field for ordering. You can just add `ASC` or `DESC`
           at the end if you want.

All other arguments will be passed to createClause_ function.

>>> sql.getRecords('test')
[True,
 [(1, u'Alabama', u'AL', u'Audemus jura nostra defendere'),
  (2, u'Alaska', u'AK', u'North to the future'),
  (3, u'Arizona', u'AZ', u'Ditat Deus'),
  (4, u'Arkansas', u'AR', u'Regnat populus'),
  (5, u'California', u'CA', u'Eureka')]]
>>> sql.getRecords('test', ['name', 'title'], limit=3, limstart=2, order='text')
[True, [(u'California', u'CA'), (u'Alaska', u'AK'), (u'Arkansas', u'AR')]]
>>> sql.getRecords('test', ['name', 'title'], limit=2, id=[2, '>'])
[True, [(u'Arizona', u'AZ'), (u'Arkansas', u'AR')]]

.. _updateRecords:

Records updating
-------------------------

For updating you can use **updateRecords** method.
First argument of this function is  database table name.
Second argument is dictionary with keys - field names and values -
data which must be set. Other arguments will be passed to
createClause_ function.

>>> sql.updateRecords('test', {'name': 'Connecticut', 'title': 'CT',
                'text': 'Qui transtulit sustinet'}, id=5)
[True, []]
>>> sql.getRecords('test', id=5)
[True, [(5, u'Connecticut', u'CT', u'Qui transtulit sustinet')]]

.. _delete:

Records deletion
-------------------------

You can delete records through **delete** method.
First argument of this function is a database table name.
All other arguments will be passed to createClause_ function.

>>> sql.delete('test', id=5)
[True, []]
>>> sql.getRecords('test', id=5)
[True, []]

.. _getCount:

Counting records
-------------------------

To obtain number of records you can use **getCount** method.
First argument of this function is a database table name.
All other arguments will be passed to createClause_ function.

>>> sql.getCount('test')
[True, 4]
>>> sql.getCount('test', id=[2, '>'])
[True, 2]

Query generator
=========================

Just initialize SQL class without arguments. Or set *ATTACHED*
property of class to False. When *ATTACHED* class property is False
executeQuery_ method returns query string without execution, so you
can get queries from functions noted above.

>>> sql.ATTACHED = False
>>> sql.insertNew('test', None, name='Alabama', title='AL', text='Audemus jura nostra defendere')
u"INSERT INTO `test` (text, name, title) VALUES('Audemus jura nostra defendere', 'Alabama', 'AL') "
>>> sql.getRecords('test')
u'SELECT DISTINCT * FROM `test`    LIMIT 0,20'
>>> sql.getRecords('test', ['name', 'title'], limit=3, limstart=2, order='text')
u'SELECT DISTINCT name,title FROM `test`   ORDER BY text LIMIT 2,3'
>>> sql.getRecords('test', ['name', 'title'], limit=2, id=[2, '>'])
u"SELECT DISTINCT name,title FROM `test`  WHERE id > '2'  LIMIT 0,2"
>>> sql.updateRecords('test', {'name': 'Connecticut', 'title': 'CT',
                     'text': 'Qui transtulit sustinet'}, id=5)
u"UPDATE `test` SET text='Qui transtulit sustinet', name='Connecticut', title='CT' WHERE id = '5'"
>>> sql.delete('test', id=5)
u"DELETE FROM test WHERE id = '5'"
>>> sql.getCount('test', id=[2, '>'])
u"SELECT COUNT(*) FROM `test` WHERE id > '2'"

Additional functions
-------------------------

.. _createClause:

**createClause** function provides simple interface to create clause
strings. It returns string regardless of *ATTACHED* class property.
Function accepts keyword arguments where key - column and value -
clause for this column. One equality doesn't need additional parameters
and may have string argument.

>>> sql.createClause(one=1)
u"WHERE one = '1'"

When you clause is not equality or you needs to create complex clause,
you must declare function symbol as each second value in list of
arguments.

>>> sql.createClause(one=[1, '>'])
u"WHERE one > '1'"
>>> sql.createClause(one=[1, '>', 40, '<', '%3%', 'LIKE'])
u"WHERE one > '1' AND one < '40' AND one LIKE '%3%'"

Needs more complex clauses? You can use lists instead of values to
create subclauses:

>>> sql.createClause(one=[['%3', 'LIKE'], 'OR', ['2', 'NOT'], 'AND'])
u"WHERE (one LIKE '%3') AND (one NOT '2')"

You can change global summarise symbol from `AND` to `OR` by passing
False as first argument.

>>> sql.createClause(one=[1, '>', 40, '<'])
u"WHERE one > '1' OR one < '40'"

Complex example (it is just example of the possibilities, please do not
do such things):

>>> sql.createClause(one='1', two=['2'], three=['3', '>'], four=[['4_1', '>', '4_2', '<'], 'AND', '4'], five=[[['%5_1_1', 'LIKE'], 'OR', ['5_1_3', 'NOT'], 'AND'], 'AND', ['5_2_1', '>', '5_2_2'], 'OR', '5_3', 'NOT'])
 u"WHERE (four > '4_1' AND four < '4_2') AND four = '4' AND three > '3' AND ((five LIKE '%5_1_1') AND (five NOT '5_1_3')) AND (five > '5_2_1' OR five = '5_2_2') AND five NOT '5_3' AND two = '2' AND one = '1'"
