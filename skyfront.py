#!/usr/bin/python
# -*- coding: utf-8 -*-

class SQL:
    "SQL module"

    def __init__(self, backend, **kwargs):
        if self.chooseBackend(backend):
            self.connect(**kwargs)
        else:
            print 'Backend not choosed.'

    def chooseBackend(self, backend='sqlite'):
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


    def connect(self, **kwargs):
        self.__db = self.backend.connect(**kwargs)
        self.cursor = self.__db.cursor(cursorclass=self.__cursorclass)

    def executeQuery(self, query, action="select"):
        ##Add more debugging information
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
        for name in vars:
            if vars[name] != None:
                fields.append(name)
                values.append(unicode(vars[name]))
        if len(upd) > 0:
            up = []
            for i in upd:
                if vars.has_key(i) and vars[i] != None:
                    up.append(u"%s = '%s'" % (i, vars[i]))
            if len(up) > 0:
                update = u'ON DUPLICATE KEY UPDATE %s' % u', '.join(unicode(up))
        fields = u', '.join(fields)
        values = u'", "'.join(values)
        qw = u'INSERT INTO `%s` (%s) VALUES("%s") %s' % (tbl, fields, values, update)
        return self.executeQuery(qw, 'insert')

    def find(self, tbl, value, column, *fields):
        '''Usage: (table, find_value, find_column, return_columns). ID column added if not given'''
        fields = list(fields)
        try:
            fields.index('id')
        except:
            fields.append('id')
        var = {}
        var[column] = value
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
            return ['error', qw]
        ret = self.executeQuery(qw)
        return ret

    def updateRecords(self, tbl, set={}, **vars):
        update = []
        for key in set.keys():
            update.append(u"%s='%s'" % (key, set[key]))
        update = u', '.join(update)
        clause = self.createClause(**vars)
        qw = u'UPDATE `%s` SET %s %s' % (tbl, update, clause)
        rows = self.executeQuery(qw)
        return rows

    def createClause(self, And = True, WClauseOperator = '=', **vars):
        wclause = []
        for i in vars.keys():
            if vars[i]:
                if type(vars[i]).__name__ == 'list':
                    v = vars[i]
                    cl = []
                    for j in v:
                        cl.append(u"%s %s '%s'" % (i, WClauseOperator, j))
                    wclause.append(u'(%s)' % ' OR '.join(cl))
                else:
                    wclause.append(u"%s %s '%s'" % (i, WClauseOperator, vars[i]))
        if len(wclause):
            if And:
                wclause = 'WHERE ' + ' AND '.join(wclause)
            else:
                wclause = 'WHERE ' + ' OR '.join(wclause)
        else:
            wclause = ''
        return wclause
