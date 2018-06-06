# coding=utf-8

from twisted.enterprise import adbapi
from backend.config import config
import happybase
from twisted.internet import defer, reactor


class MySQLDBConnection(object):
    def __init__(self):
        self.dbpool = adbapi.ConnectionPool(
            "MySQLdb", host=config.host, port=int(config.port),
            cp_max=int(config.cp_max), cp_min=int(config.cp_min), db=config.database, user=config.owner,
            passwd=config.password)
        self.dbpool.execute_insert = self.execute_insert

    def execute_insert(self, family, column_names, data_listes):

        column = "("
        data = "("
        for index in range(len(column_names)):
            column += '`' + str(column_names[index]) + '`' + ','
            data += '\'' + str(data_listes[index]) + '\'' + ','

        column = column[:-1] + ')'
        data = data[:-1] + ')'
        sql = "insert into {} {} values {} ".format(family, column, data)
        result = db.dbpool.runQuery(sql)
        result.addCallbacks(self.finish, self.finish)
        return result

    def finish(self, param):
        print param
        return

    def query(self, sql):

        def success(info):
            print info

        result = db.dbpool.runQuery(sql)
        result.addCallbacks(success, self.finish)

        return result


class HBaseDBConnection(object):
    info_column = 'information'  # 数据
    sensor_column = 'sensor'    # 传感器
    user_column = 'user'

    def __init__(self):
        self.dbpool = happybase.Connection(host=config.host, port=int(config.port), protocol='binary')
        self.check_table()

    def check_table(self, table_name='cherrymonth'):
        try:
            if not self.dbpool.is_table_enabled(table_name):
                print 'table %s does not enable, Try to enable it!' % (table_name,)
                self.dbpool.enable_table(table_name)
                print 'enable %s table collect success!' % (table_name,)
        except Exception:
            print 'table %s does not existed, try to create it!' % (table_name,)
            self.create_table(table_name)
            print 'create %s success!' % (table_name,)

    def create_table(self, name):

        familes = {self.info_column: dict(), self.sensor_column: dict(), self.user_column: dict()}
        self.dbpool.create_table(name, familes)
        self.dbpool.table(name).counter_set('num', self.user_column + ':num')
        self.dbpool.table(name).counter_set('num', self.info_column + ':num')
        self.dbpool.table(name).counter_set('num', self.sensor_column + ':num')

    def execute_insert(self, family, column_names, data_listes, table_name='cherrymonth'):

        """
        为了封装execute_insert 函数使其调用规则类似SQL
        参数接收所有的列名以及列对应的数据

        无论是hbase还是sql 只需要填充列名和列对应的属性即可

        example:

        family = 'sensor'
        column_names = ['id', 'type', 'entry_time']
        data_listes = ['1', '温度', '2017']
        db.execute_insert(column_names, data_listes, family)

        :param column_names:
        :param data_listes:
        :param table_name:
        :param family:
        :return:
        """

        cmd = dict()

        for index in range(len(column_names)):
            cmd[family + ":" + column_names[index]] = str(data_listes[index])

        row = self.dbpool.table(table_name).counter_get('num', family + ':num')
        self.dbpool.table(table_name).counter_inc('num', family + ':num')
        self.dbpool.table(table_name).put(str(row), cmd)

        d = defer.Deferred()

        def success(info):
            print info

        d.addCallbacks(success, success)
        return d


if config.driver == 'hbase':
    db = HBaseDBConnection()
elif config.driver == 'mysql':
    db = MySQLDBConnection()
else:
    raise Exception(config.driver + ' not support in my system! only mysql and hbase can good working')


if __name__ == '__main__':
    # db.execute_insert('test', ['id', 'name', 'password'], ['123', 123, 123])
    db.query('select * from test where id > 0')
    reactor.run()
