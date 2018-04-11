"""
    该模块提供了新闻、用户、历史记录以及新闻集合、用户集合、历史记录集合对应的类

    @Author: flx
    @Date: 2018-4-2
"""

from Utils.DBUtil import DBHandle
import numpy as np
from Utils.BaseUtil import BaseUtil
import sys


class Article:
    """
        新闻类，存储了新闻的各个字段
    """

    def __init__(self, title, category, content, aid=None, topicVector=None, wordsList=None, pubDateTime=None):
        """
            parameter:
                title, category, content 三个参数值在构造该对象时必须提供

                title: String类型
                category: String类型
                content: String类型
                aid: int类型，在插入记录后由数据库提供
                topicvector: String类型，Mysql无法存储向量类型，BaseUtil中提供了向量和字符串之间的转换
                wordsList： String类型，在程序中是List类型，BaseUtil中提供了List和字符串之间的转换
                pubDateTime: String类型
        """
        self._aid = aid
        self._title = title
        self._content = content
        self._category = category
        self._topicVector = topicVector
        self._wordsList = wordsList
        self._pubDateTime = pubDateTime

    @property
    def aid(self):
        return self._aid

    @aid.setter
    def aid(self, aid):
        if not isinstance(aid, int):
            raise TypeError('Error: the aid must be of type int!')
        self._aid = aid

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title):
        if not isinstance(title, str):
            raise TypeError('Error: the title must be of type string!')
        self._title = title

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, category):
        if not isinstance(category, str):
            raise TypeError('Error: the category must be of type string!')
        self._category = category

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, content):
        if not isinstance(content, str):
            raise TypeError('Error: the content must be of type string!')
        self._content = content

    @property
    def topicVector(self):
        return self._topicVector

    @topicVector.setter
    def topicVector(self, topicVector):
        if not isinstance(topicVector, str):
            raise TypeError('Error: the topicVector must be of type string!')
        self._topicVector = topicVector

    @property
    def wordsList(self):
        return self._wordsList

    @wordsList.setter
    def wordsList(self, wordsList):
        if not isinstance(wordsList, str):
            raise TypeError('Error: the wordsList must be of type string!')
        self._wordsList = wordsList

    @property
    def pubDateTime(self):
        return self._pubDateTime

    @pubDateTime.setter
    def pubDateTime(self, pubDateTime):
        if not isinstance(pubDateTime, str):
            raise TypeError('Error: the pubDateTime must be of type string!')
        self._pubDateTime = pubDateTime


class Articles(DBHandle):
    """
        新闻集合类，继承了DBHandle类，直接连接数据库中对应的表，
        可以实时与数据库进行交互.
    """

    def __init__(self):
        super().__init__(tbName='articles')

    def getAll(self):
        """返回所有新闻记录"""
        res = self.select()
        if res:
            for line in res:
                yield Article(aid=line[0], title=line[1], category=line[2],
                              content=line[3], topicVector=line[4], wordsList=line[5], pubDateTime=line[6])
        else:
            return None

    def getByAid(self, aid):
        """通过Aid返回新闻"""
        res = self.select(aid=aid)
        if res:
            # Aid不会有重复，只会返回一个对象
            line = res[0]
            return Article(aid=line[0], title=line[1], category=line[2],
                          content=line[3], topicVector=line[4], wordsList=line[5], pubDateTime=line[6])
        else:
            return None

    def _selectByCategory(self, cate):
        """按时间降序返回特定类别的新闻"""
        sql = "SELECT * FROM {table} WHERE category='{cate}' ORDER BY pubDateTime DESC".format(table='articles', cate=cate)
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

    def getByCategory(self, cate):
        """按类别返回新闻"""
        res = self._selectByCategory(cate)
        if res:
            for line in res:
                yield Article(aid=line[0], title=line[1], category=line[2],
                              content=line[3], topicVector=line[4], wordsList=line[5], pubDateTime=line[6])
        else:
            return None

    def _selectByKeyWords(self, keyWordsList):
        """返回含有特定关键词的新闻"""
        word0 = keyWordsList[0]
        sql = "SELECT * FROM {table} WHERE CONCAT(title, content) LIKE '%{word}%' ".format(table='articles', word=word0)
        for word in keyWordsList[1:]:
            sql += "OR CONCAT(title, content) LIKE '%{word}%' ".format(word=word)
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

    def getByKeyWords(self, keyWordsList):
        """返回含有特定关键词的新闻"""
        res = self._selectByKeyWords(keyWordsList)
        if res:
            for line in res:
                yield Article(aid=line[0], title=line[1], category=line[2],
                              content=line[3], topicVector=line[4], wordsList=line[5], pubDateTime=line[6])
        else:
            return None

    def getArticleFeatures(self, aidList):
        """返回新闻id列表对应的新闻特征向量"""
        afs = []
        for aid in aidList:
            res = self.select(aid=aid)
            if res:
                # 只会返回一个对象
                line = res[0]
                if line[4]:
                    afs.append(BaseUtil.line2float64list(line[4]))
                else:  # topicVector为None
                    raise ValueError('Error: the value of topicVector is None!')

        return afs

    def add(self, article):
        """加入一个新闻对象，会直接插入数据库"""
        if not isinstance(article, Article):
            raise TypeError('Error: the arguments to the add method only support the Article type!')
        return self.insert(aid=article.aid, title=article.title, category=article.category, content=article.content,
                    topicVector=article.topicVector, wordsList=article.wordsList, pubDateTime=article.pubDateTime)

    def update(self, article):
        """更新新闻对新"""
        if not isinstance(article, Article):
            raise TypeError('Error: the arguments to the update method only support the Article type!')
        return self.modify(aid=article.aid, title=article.title, category=article.category, content=article.content,
                    topicVector=article.topicVector, wordsList=article.wordsList, pubDateTime=article.pubDateTime)

    def remove(self, article):
        pass

    def save(self, article):
        pass


class User:
    """用户类，存储了用户的各个字段"""

    def __init__(self, uname, uid=None, interest=None, updateTime=None):
        self._uid = uid
        self._uname = uname
        self._interest = interest
        # 此处的time是指兴趣最后更新时间
        self._updateTime = updateTime

    @property
    def uid(self):
        return self._uid

    @uid.setter
    def uid(self, uid):
        if not isinstance(uid, int):
            raise TypeError('Error: the uid must be of type int!')
        self._uid = uid

    @property
    def uname(self):
        return self._uname

    @uname.setter
    def uname(self, uname):
        if not isinstance(uname, str):
            raise TypeError('Error: the uname must be of type string!')
        self._uname = uname

    @property
    def interest(self):
        return self._interest

    @interest.setter
    def interest(self, interest):
        if not isinstance(interest, str):
            raise TypeError('Error: the interest must be of type string!')
        self._interest = interest

    @property
    def updateTime(self):
        return self._updateTime

    @updateTime.setter
    def updateTime(self, updateTime):
        if not isinstance(updateTime, str):
            raise TypeError('Error: the updateTime must be of type string!')
        self._updateTime = updateTime


class Users(DBHandle):
    """
        用户集合类，继承了DBHandle类，直接连接数据库中对应的表，
        可以实时与数据库进行交互.
    """
    def __init__(self):
        super().__init__(tbName='users')

    def _add(self, user):
        if not isinstance(user, User):
            raise TypeError('Error: the arguments to the add method only support the User type!')
        # 用户名设定为不能重复
        if len(self.select(uname=user.uname)) > 0:
            print('Error: this uname has be registered!')
            return False
        return self.insert(uid=user.uid, uname=user.uname, interest=user.interest, updateTime=user.updateTime)

    def loginUser(self, user):
        """注册一个新用户"""
        return self._add(user)

    def getById(self, uid):
        """按Uid返回用户"""
        res = self.select(uid=uid)
        if res:
            # 只会返回一个对象
            line = res[0]
            return User(uid=line[0], uname=line[1], interest=line[2], updateTime=line[3])
        else:
            return None

    def getByName(self, uname):
        """按用户名返回用户，如果有多个相同用户名的用户，则只能返回第一个."""
        res = self.select(uname=uname)
        if res:
            # 只会返回一个对象
            line = res[0]
            return User(uid=line[0], uname=line[1], interest=line[2], updateTime=line[3])
        else:
            return None

    def updateInterest(self, uid, afList):
        """计算用户的兴趣向量，采用向量相加求均值的策略"""
        afArrray = np.array(afList)
        newInterest = afArrray.sum(axis=0) / afArrray.shape[0]
        user = self.getById(uid)
        user.interest = BaseUtil.list2line(newInterest)
        user.updateTime = BaseUtil.getCurrentTime()
        return self.modify(uid=user.uid, uname=user.uname, interest=user.interest, updateTime=user.updateTime)


class Record:
    """浏览记录类，存储了浏览记录的各个字段

       parameters:
         uid: 用户id
         aid: 阅读的新闻id
         preference: 用户对该新闻的偏好,1为喜欢，0为不喜欢
         recordTime: 记录的时间
    """

    def __init__(self, uid, aid, preference, recordTime=None):
        self._uid = uid
        self._aid = aid
        self._preference = preference
        self._recordTime = recordTime

    @property
    def uid(self):
        return self._uid

    @uid.setter
    def uid(self, uid):
        if not isinstance(uid, int):
            raise TypeError('Error: the uid must be of type int!')
        self._uid = uid

    @property
    def aid(self):
        return self._aid

    @aid.setter
    def aid(self, aid):
        if not isinstance(aid, int):
            raise TypeError('Error: the aid must be of type int!')
        self._aid = aid

    @property
    def preference(self):
        return self._preference

    @preference.setter
    def preference(self, preference):
        if not isinstance(preference, int):
            raise TypeError('Error: the preference must be of type int!')
        if not preference in [1, 0]:
            raise ValueError('Error: the value of preference can only be 0 or 1!')
        self._preference = preference

    @property
    def recordTime(self):
        return self._recordTime

    @recordTime.setter
    def recordTime(self, recordTime):
        if not isinstance(recordTime, str):
            raise TypeError('Error: the recordTime must be of type string!')
        self._recordTime = recordTime


class Records(DBHandle):
    """
        浏览日志集合类，继承了DBHandle类，直接连接数据库中对应的表，
        可以实时与数据库进行交互.
    """
    def __init__(self):
        super().__init__(tbName='records')

    def add(self, record):
        """插入一条记录"""
        if not isinstance(record, Record):
            raise TypeError('Error: the arguments to the add method only support the Record type!')
        return self.insert(uid=record.uid, aid=record.aid, preference=record.preference, recordTime=record.recordTime)

    def getAll(self):
        """获取所有浏览记录"""
        res = self.select()
        if res:
            for line in res:
                yield Record(uid=line[0], aid=line[1], preference=line[2], recordTime=line[3])
        else:
            return None

    def getByAid(self, aid):
        """获取包含特定新闻id的浏览记录"""
        res = self.select(aid=aid)
        if res:
            for line in res:
                yield Record(uid=line[0], aid=line[1], preference=line[2], recordTime=line[3])
        else:
            return None

    def getByUid(self, uid):
        """获取包含特定用户id的浏览记录"""
        res = self.select(uid=uid)
        if res:
            for line in res:
                yield Record(uid=line[0], aid=line[1], preference=line[2], recordTime=line[3])
        else:
            return None

    def getUserInterestAids(self, uid):
        """返回用户浏览过的并且感兴趣的新闻aid"""
        # res = self.select(uid=uid)
        res = self._selectLatestInterestAids(uid)
        if res:
            res = [line[1] for line in res]
            return res
        else:
            return None

    def _selectLatestInterestAids(self, uid):
        """查询用户浏览过的并且感兴趣的新闻aid"""
        sql = "SELECT * FROM {table} WHERE uid={uid} ORDER BY recordTime DESC LIMIT 20".format(table='records', uid=uid)
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
#     articles = Articles()
#     for article in articles.getByKeyWords(['篮球', '足球']):
#         print(article.topicVector)
