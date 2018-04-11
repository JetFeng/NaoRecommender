"""
    数据库基本操作类的实现.

    @Author: flx
    @Date: 2018-4-2
"""

import pymysql
import sys
from Utils.BaseUtil import BaseUtil


class DBHandle:
    """数据库基本的增删改查，只提供基础共用的sql语句操作

    提供的基本sql操作只能带 "相等" 条件，作为父类继承，
    要实现复杂sql操作，应当在子类中实现

    """

    # 打开数据库链接
    db = pymysql.connect('localhost', 'root', '196214', 'robotnews')
    # 使用cursor方法创建一个游标对象
    cursor = db.cursor()

    def __init__(self, tbName):
        """初始化指定要连接的数据表名，一个实例只能连接一个数据表"""
        self._table = tbName

    @property
    def table(self):
        return self._table

    def insert(self, **kwargs):
        """数据库插入操作

        Args:
            kwargs:使用可变参数搜集要插入的字段和对应值,只能插入整型和字符串型的字段.
                   不具体检查字段以及字段值是否合法.
        Returns:
            成功插入返回True,失败返回False
        """
        if len(kwargs) == 0:
            return False
        else:
            kvs = {}
            for k, v in kwargs.items():
                if v is None:
                    continue
                # 注意：如果是字符串类型的值，在sql语句中要为该值额外添加引号
                if isinstance(v, str):
                    v = "'" + v + "'"
                else:
                    v = str(v)
                kvs[k] = v

            sql = "INSERT INTO {table}({keys}) VALUES({values})"\
                .format(table=self._table, keys=','.join(list(kvs.keys())), values=','.join(list(kvs.values())))
            try:
                # 执行sql语句
                DBHandle.cursor.execute(sql)
                # 提交到数据库执行
                DBHandle.db.commit()
                return True
            except:
                # 打印异常sql语句
                sys.stderr.write(sql)
                # 事物回滚
                DBHandle.db.rollback()
                return False

    def modify(self, **kwargs):
        """提供了sql基本修改操作

        该方法只能按id号进行定位实现修改，即：
        在kwargs传入的所有字段值中，必须有含有'id'子串的字段值

        Returns:
            成功修改返回True,失败返回False
        """
        if len(kwargs) == 0:
            return False
        else:
            kvs = []
            for k, v in kwargs.items():
                if v is None:
                    continue
                if 'id' in k:
                    id = k
                    continue
                # 注意：如果是字符串类型的值，在sql语句中要为该值额外添加引号
                if isinstance(v, str):
                    v = "'" + v + "'"
                kvs.append(k + '=' + str(v))
            sql = 'UPDATE {table} SET {kvs} WHERE {idk}={idv}'.format(table=self._table, kvs=','.join(kvs),
                                                                      idk=id, idv=str(kwargs[id]))
            try:
                # 执行sql语句
                DBHandle.cursor.execute(sql)
                # 提交到数据库执行
                DBHandle.db.commit()
                return True
            except:
                # 打印异常sql语句
                sys.stderr.write(sql)
                DBHandle.db.rollback()
                return False

    def delete(self, **kwargs):
        """提供了sql基本删除操作

        删除条件只能使用简单的"相等"条件，例如：id=5,date=2018-3-23...
        参数为空时删除所有记录.

        Returns:
            成功执行返回True,失败返回False.
        """

        if len(kwargs) == 0:
            sql = 'DELETE FROM {table}'.format(table=self._table)
        else:
            kvs = {}
            for k, v in kwargs.items():
                if v is None:
                    continue
                # 字段值是字符串时多加一对引号
                if isinstance(v, str):
                    v = "'" + v + "'"
                else:
                    v = str(v)
                kvs[k] = v
            conditions = [k + "=" + v for k, v in kvs.items()]
            sql = "DELETE FROM {table} WHERE {conditions}".format(table=self._table, conditions=' AND '.join(conditions))
        try:
            # 执行sql语句
            DBHandle.cursor.execute(sql)
            # 提交修改
            DBHandle.db.commit()
            return True
        except:
            # 打印异常sql语句
            sys.stderr.write(sql)
            # 事物回滚
            DBHandle.db.rollback()
            return False

    def select(self, **kwargs):
        """提供了sql基本查询操作

        查询条件只能使用简单的"相等"条件，例如：id=5, date=2018-3-23...
        参数为空返回所有记录.

        Returns:
            成功执行返回查询记录，否则返回None
        """
        if len(kwargs) == 0:
            sql = 'SELECT * FROM {table}'.format(table=self._table)
        else:
            kvs = {}
            for k, v in kwargs.items():
                if v is None:
                    continue
                # 字段值是字符串时多加一对引号
                if isinstance(v, str):
                    v = "'" + v + "'"
                else:
                    v = str(v)
                kvs[k] = v
            conditions = [k + "=" + v for k, v in kvs.items()]
            sql = "SELECT * FROM {table} WHERE {conditions}".format(table=self._table, conditions=' AND '.join(conditions))
        try:
            # 执行sql语句
            DBHandle.cursor.execute(sql)
            # 获取所有记录列表
            results = DBHandle.cursor.fetchall()
            return results
        except:
            # 打印异常sql语句
            sys.stderr.write(sql)
            # 事物回滚
            DBHandle.db.rollback()
            return None

# if __name__ == '__main__':
#     dbA = DbHandle('articles')
#     dbA.delete()
#     # dbA.insert(title='标题5', content='内容5', category='类别5', pubDateTime=BaseUtil.getCurrentTime())
#     # res = dbA.select(title='标题5')
#     # print(type(res))
#     # for article in dbA.select(title='标题5'):
#     #     for field in article:
#     #         print(field, type(field))
#     # dbU = DbHandle('users')
#     # dbU.insert(uname='flx')
