#!/usr/bin/python
# -*- coding: utf-8 -*-

class SQL:
    "SQL module"

    def __init__(self, backend, *args, **kwargs):
        if self.chooseBackend(backend):
            try:
                self.connect(*args, **kwargs)
            except Exception, e:
                print 'Connection not made: %s' % e
        else:
            print 'Backend not choosed.'

    def chooseBackend(self, backend='sqlite'):
        self.backend = backend
        if backend == 'mysql':
            try:
                self.__backed = __import__('MySQLdb')
                self.__cursorclass = self.__backed.cursors.DictCursor
            except ImportError, e:
                print e
            else:
                if not vars.has_key("db"):
                    print "Database not specified"
                elif not vars.has_key("user"):
                    print "Database user name not specified"
                elif not vars.has_key("passwd"):
                    print "Database user password not specified"
                else:
                    return True
        elif backend == 'sqlite':
            try:
                self.__backed = __import__('sqlite3')
                self.__cursorclass = self.__backed.Cursor
            except ImportError, e:
                print e
            else:
                return True
        else:
            print "Backend not supported yet."

    def connect(self, *args, **kwargs):
        self.__db = self.__backed.connect(*args, **kwargs)
        self.cursor = self.__db.cursor(self.__cursorclass)

    @classmethod
    def escape(self, string):
        return string.replace(u"'", u"''")

    def executeQuery(self, query, action="select"):
        ##Add more debugging information
        if not self.cursor:
            return [False, 'Database not initialized.']
        c = self.cursor
        try:
            c.execute(query)
        except Exception, e:
            return [False, unicode(e)]
        self.__db.commit()
        if action == "select":
            fetch = c.fetchall()
            return [True, fetch]
        if action == "insert":
            return [True, c.lastrowid]

    def insertNew(self, tbl, upd=[], **vars):
        fields = []
        values = []
        update = ''
        for name in vars.keys():
            if vars[name] != None:
                fields.append(self.escape(name))
                values.append(self.escape(unicode(vars[name])))
        if len(upd) > 0:
            up = []
            for i in upd:
                if vars.has_key(i) and vars[i] != None:
                    up.append(u"%s = '%s'" % (self.escape(i), self.escape(vars[i])))
            if len(up) > 0:
                update = u'ON DUPLICATE KEY UPDATE %s' % u', '.join(unicode(up))
        fields = u', '.join(fields)
        values = u"', '".join(values)
        qw = u"INSERT INTO `%s` (%s) VALUES('%s') %s" % (tbl, fields, values, update)
        return self.executeQuery(qw, 'insert')

    def delete(self, tbl, delete_all_records=False, **vars):
        c = self.createClause(**vars)
        if not c and not delete_all_records:
            return [False, 'Please pass delete_all_records to make complete deletion.']
        return self.executeQuery(u"DELETE FROM %s %s" % (tbl, c))

    def find(self, tbl, value, column, *fields):
        '''Usage: (table, find_value, find_column, return_columns). ID column added if not given'''
        fields = list(fields)
        try:
            fields.index('id')
        except:
            fields.append('id')
        var = {column: value}
        res = self.getRecords(tbl, select=fields, limit=1, **var)
        return res

    def getCount(self, tbl, clause = None, **vars):
        if not clause:
            clause = self.createClause(**vars)
        qw = 'SELECT COUNT(*) FROM `%s` %s' % (tbl, clause)
        ret = self.executeQuery(qw)
        if ret[0]:
            ret[1] = ret[1][0].values()[0]
        return ret;

    def getRecords(self, tbl, select = [], QueryJoins = '', limit = 20,
                              limstart = 0, order='', **vars):
        if len(select):
            select = u','.join(select)
        else:
            select = u'*'
        if limit:
            limit = u'LIMIT %s,%s' % (limstart, limit)
        else:
            limit = u''
        if order:
            order = u'ORDER BY %s' % order
        clause = self.createClause(**vars)
        qw = u'SELECT DISTINCT %s FROM `%s` %s %s %s %s' % (select,
                tbl, QueryJoins, clause, order, limit)
        if vars.has_key('debug'):
            return [False, qw]
        return self.executeQuery(qw)

    def updateRecords(self, tbl, set={}, **vars):
        update = []
        for key in set.keys():
            update.append(u"%s='%s'" % (self.escape(key), self.escape(set[key])))
        update = u', '.join(update)
        clause = self.createClause(**vars)
        qw = u'UPDATE `%s` SET %s %s' % (tbl, update, clause)
        rows = self.executeQuery(qw)
        return rows

    def createClause(self, And = True, **vars):
        if not vars.keys():
            return ''
        def _l(lst, var):
            cl = []
            if len(lst) % 2:
                lst.append('=')
            for item in zip(*[lst[i::2] for i in range(2)]):
                if type(item[0]) is list:
                    if not item[1]:
                        item[1] = 'OR'
                    cl.append(u'(%s)' % (u' %s ' % item[1]).join(_l(item[0], var)))
                else:
                    cl.append(u"%s %s '%s'" % (self.escape(var), self.escape(item[1]), self.escape(item[0])))
            return cl
        wclause = []
        for i in vars.keys():
            if vars[i]:
                if type(vars[i]) is list:
                    wclause.extend(_l(vars[i], i))
                else:
                    wclause.append(u"%s = '%s'" % (self.escape(i), self.escape(vars[i])))
        if And:
            wclause = 'WHERE ' + ' AND '.join(wclause)
        else:
            wclause = 'WHERE ' + ' OR '.join(wclause)
        return wclause
