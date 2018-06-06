# coding=utf-8
import happybase

connection = happybase.Connection(host='192.168.1.51', port=9090, protocol='binary')
familes = {"a": dict(), "b": dict()}
connection.open()
# connection.create_table('test', familes)

print connection.is_table_enabled('test')

# table_name_list = connection.tables()
# print table_name_list
a = happybase.Table('爱仕达所大大', connection)
table = happybase.Table('test', connection)
table.put('1', {"a:1": "1"})
print table.cells('1', 'a:1', include_timestamp=True)  # 返回某一具体行，具体列的数据
print table.row('1')  # 返回某一行的数据
print table.rows(['1'])  # 返回多行数据　rows　可以是一个含有行健的列表或者元组

content = table.scan()
for c in content:
    print type(c)

table.counter_set('1', "a:3")
table.counter_inc('1', "a:3")
print table.counter_get('1', 'a:3')