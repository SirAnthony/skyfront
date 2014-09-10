#!/usr/bin/python

"""
Tests for skyfront
"""

import unittest
import os
from skyfront import SkyFront


table_create = '''CREATE TABLE IF NOT EXISTS `test` (
                                id INTEGER PRIMARY KEY autoincrement,
                                name VARCHAR UNIQUE,
                                title VARCHAR NOT NULL,
                                text VARCHAR NOT NULL)'''


class TestDatabase(unittest.TestCase):

    def setUp(self):
        self.sql = SkyFront('sqlite', 'test.sqlite')
        self.sql.executeQuery(table_create)

    def tearDown(self):
        os.unlink('test.sqlite')


class TestDatabaseNoFixture(TestDatabase):

    def test_execute(self):
        query = '''CREATE TABLE IF NOT EXISTS `test2` (
                    id INTEGER PRIMARY KEY autoincrement,
                    name VARCHAR UNIQUE,
                    title VARCHAR NOT NULL,
                    text VARCHAR NOT NULL)'''
        self.assertEquals(self.sql.executeQuery(query), [True, []])

    def test_insertion(self):
        self.assertEquals(self.sql.insertNew('test', None, name='Alabama',
            title='AL', text='Audemus jura nostra defendere'), [True, 1])
        self.assertEquals(self.sql.insertNew('test', None, name='Alaska',
            title='AK', text='North to the future'), [True, 2])
        self.assertEquals(self.sql.insertNew('test', None, name='Arizona',
            title='AZ', text='Ditat Deus'), [True, 3])
        self.assertEquals(self.sql.insertNew('test', None, name='Arkansas',
            title='AR', text='Regnat populus'), [True, 4])
        self.assertEquals(self.sql.insertNew('test', None, name='California',
            title='CA', text='Eureka'), [True, 5])


class TestDatabaseFixture(TestDatabase):

    def setUp(self):
        super(TestDatabaseFixture, self).setUp()
        self.sql.insertNew('test', None, name='Alabama', title='AL',
                           text='Audemus jura nostra defendere')
        self.sql.insertNew('test', None, name='Alaska', title='AK',
                           text='North to the future')
        self.sql.insertNew('test', None, name='Arizona', title='AZ', text='Ditat Deus')
        self.sql.insertNew('test', None, name='Arkansas', title='AR', text='Regnat populus')
        self.sql.insertNew('test', None, name='California', title='CA', text='Eureka')

    def test_select(self):
        self.assertEquals(self.sql.getRecords('test'), [True,
            [(1, u'Alabama', u'AL', u'Audemus jura nostra defendere'),
            (2, u'Alaska', u'AK', u'North to the future'),
            (3, u'Arizona', u'AZ', u'Ditat Deus'),
            (4, u'Arkansas', u'AR', u'Regnat populus'),
            (5, u'California', u'CA', u'Eureka')]])
        self.assertEquals(self.sql.getRecords('test', ['name', 'title'],
            limit=3, limstart=2, order='text'), [True,
            [(u'California', u'CA'), (u'Alaska', u'AK'), (u'Arkansas', u'AR')]])
        self.assertEquals(self.sql.getRecords('test', ['name', 'title'],
            limit=2, id=[2, '>']), [True, [(u'Arizona', u'AZ'), (u'Arkansas', u'AR')]])

    def test_update(self):
        self.assertEquals(self.sql.updateRecords('test',
            {'name': 'Connecticut', 'title': 'CT',
            'text': 'Qui transtulit sustinet'}, id=5), [True, []])
        self.assertEquals(self.sql.getRecords('test', id=5), [True,
            [(5, u'Connecticut', u'CT', u'Qui transtulit sustinet')]])

    def test_deletion(self):
        self.assertEquals(self.sql.delete('test', id=5), [True, []])
        self.assertEquals(self.sql.getRecords('test', id=5), [True, []])

    def test_count(self):
        self.assertEquals(self.sql.getCount('test'), [True, 5])
        self.assertEquals(self.sql.getCount('test', id=[2, '>']), [True, 3])


class TestGenerator(unittest.TestCase):

    def setUp(self):
        self.sql = SkyFront()

    def test_generation(self):
        self.assertEquals(self.sql.insertNew('test', None, name='Alabama',
            title='AL', text='Audemus jura nostra defendere'),
            u"INSERT INTO `test` (text, name, title) VALUES('Audemus jura nostra defendere', 'Alabama', 'AL')")
        self.assertEquals(self.sql.getRecords('test'), u'SELECT DISTINCT * FROM `test`')
        self.assertEquals(self.sql.getRecords('test', ['name', 'title'],
            limit=3, limstart=2, order='text'),
            u'SELECT DISTINCT name,title FROM `test` ORDER BY text LIMIT 2,3')
        self.assertEquals(self.sql.getRecords('test', ['name', 'title'], limit=2, id=[2, '>']),
            u"SELECT DISTINCT name,title FROM `test` WHERE id > '2' LIMIT 0,2")
        self.assertEquals(self.sql.updateRecords('test', {'name': 'Connecticut',
            'title': 'CT', 'text': 'Qui transtulit sustinet'}, id=5),
            u"UPDATE `test` SET text='Qui transtulit sustinet', name='Connecticut', title='CT' WHERE id = '5'")
        self.assertEquals(self.sql.delete('test', id=5), u"DELETE FROM test WHERE id = '5'")
        self.assertEquals(self.sql.getCount('test', id=[2, '>']), u"SELECT COUNT(*) FROM `test` WHERE id > '2'")

    def test_clause(self):
        self.assertEquals(self.sql.createClause(one=1), u"WHERE one = '1'")
        self.assertEquals(self.sql.createClause(one=[1, '>']), u"WHERE one > '1'")
        self.assertEquals(self.sql.createClause(one=[1, '>', 40, '<', '%3%', 'LIKE']),
            u"WHERE one > '1' AND one < '40' AND one LIKE '%3%'")
        self.assertEquals(self.sql.createClause(one=[['%3', 'LIKE'], 'OR', ['2', 'NOT'], 'AND']),
            u"WHERE (one LIKE '%3') AND (one NOT '2')")
        self.assertEquals(self.sql.createClause(False,
            one=[1, '>', 40, '<']), u"WHERE one > '1' OR one < '40'")
        self.assertEquals(self.sql.createClause(one='1', two=['2'], three=['3', '>'],
            four=[['4_1', '>', '4_2', '<'], 'AND', '4'], five=[[['%5_1_1', 'LIKE'],
            'OR', ['5_1_3', 'NOT'], 'AND'], 'AND', ['5_2_1', '>', '5_2_2'], 'OR', '5_3', 'NOT']),
            u"WHERE (four > '4_1' AND four < '4_2') AND four = '4' AND three > '3' \
AND ((five LIKE '%5_1_1') AND (five NOT '5_1_3')) AND (five > '5_2_1' OR five = '5_2_2') \
AND five NOT '5_3' AND two = '2' AND one = '1'")


if __name__ == '__main__':
    unittest.main()
