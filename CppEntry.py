"""
    该模块提供了类RecommenderForCpp，供C++进行嵌入混合编程
"""


from Model.Entity import User, Users, Article, Articles
from Core.Recommend import ContentBasedRecommend
from Model.Entity import Records, Record
from Utils.BaseUtil import BaseUtil


class RecommenderForCpp:
    def __init__(self):
        # 创建用户集合对象，自动连接了用户表
        self.users = Users()
        # 创建新闻集合对象，自动连接了新闻表
        self.articles = Articles()
        # 创建推荐日志记录对象，自动连接了用户记录表
        self.records = Records()
        # 创建推荐系统对象，传入以上三个对象作为初始化参数
        self.recommender = ContentBasedRecommend(self.users, self.articles, self.records)

    def loginUser(self, uname):
        """注册用户，只需提供注册用户名"""
        user = User(uname)
        return self.users.loginUser(user)

    def setUser(self, uname):
        """设置推荐用户"""
        self.user = self.users.getByName(uname)
        if not self.user:
            self.loginUser(uname)
            self.user = self.users.getByName(uname)
            return True

    def setRecord(self, aid, satisfaction):
        if self.user:
            record = Record(self.user.uid, aid, satisfaction, BaseUtil.getCurrentTime())
            return self.records.add(record)
        else:
            raise RuntimeError('Error: user has not specified yet, please call setUser Method First!')

    def recommendByCategory(self, cate, topN=5):
        '''

        :param cate:
        :return: [(title, cate, content),...]
        '''
        if self.user:
            result = []
            res = self.recommender.recommendByCategory(self.user.uid, cate, topN)
            for article in res:
                result.append((article.aid, article.title, article.category, article.content))
            return result
        else:
            raise RuntimeError('Error: user has not specified yet, please call setUser Method First!')

    def recommendByKeyWords(self, keyWords, topN=5):
        '''

        :param keyWords:
        :return: [(title, cate, content),...]
        '''
        if self.user:
            result = []
            res = self.recommender.recommendByKeyWords(self.user.uid, keyWords, topN)
            for article in res:
                result.append((article.aid, article.title, article.category, article.content))
            return result
        else:
            raise RuntimeError('Error: user has not specified yet, please call setUser Method First!')

    def recommendByInterest(self, topN=5):
        '''

        :return: [(title, cate, content),...]
        '''
        if self.user:
            result = []
            res = self.recommender.recommendByInterest(self.user.uid, topN)
            for article in res:
                result.append((article.aid, article.title, article.category, article.content))
            return result
        else:
            raise RuntimeError('Error: user has not specified yet, please call setUser Method First!')

    def updateInterest(self):
        if self.user:
            # 一轮推荐完成后进行模型兴趣更新
            userInterestAidList = self.records.getUserInterestAids(self.user.uid)
            userInterestArticleFeatures = self.articles.getArticleFeatures(userInterestAidList)

            self.users.updateInterest(self.user.uid, userInterestArticleFeatures)
        else:
            raise RuntimeError('Error: user has not specified yet, please call setUser Method First!')

if __name__ == '__main__':
    recommender = RecommenderForCpp()
    recommender.setUser('flx')
    res = recommender.recommendByInterest()
    for news in res:
        print('Robot:Recommend flx {NewsTitle} {cate}'.format(NewsTitle=news[1], cate=news[2]))
        print('Robot:你想要继续听完整的这篇新闻吗(y/n)?')
        response = ' '
        while response != 'y' and response != 'n':
            response = input('User: ')
        if response.lower() == 'y':
            print('Ronbot: {content}'.format(content=news[3]))
            print('这篇新闻就这样了，您感觉如何(0/1)?')
            satisfaction = -1
            while satisfaction !=0 and satisfaction != 1:
                satisfaction = int(input('User: '))
            recommender.setRecord(news[0], satisfaction)
        else:
            recommender.setRecord(news[0], 0)
        print('Robot: 好的，继续为您推荐下一篇新闻')

    # 一轮推荐完成后进行用户兴趣更新
    recommender.updateInterest()