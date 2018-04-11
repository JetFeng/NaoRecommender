"""
    推荐系统核心模块，包含基于内容的推荐系统类

    @Author: flx
    @Date: 2018-4-2
"""
from Utils.BaseUtil import BaseUtil
from sklearn.neighbors import NearestNeighbors
from gensim import similarities
from Utils.BaseUtil import BaseUtil
from Utils.NLPUtil import NLPUtil

class ContentBasedRecommend:
    """基于内容的推荐系统类

    可以按三种方式进行推荐：
        1.按用户兴趣的挖掘推荐
        2.按类别推荐
        3.按关键词搜索推荐

    parameters:
        users: 用户集合对象，Users的实例
        articles: 新闻集合对象, Articles的实例
        records: 浏览记录类, Records的实例
    """
    def __init__(self, users, articles, records):
        self.users = users
        self.articles = articles
        self.records = records
        self.model = None
        self.maxNum = 50
        self.aidList = []
        self.index = None

    def recommendByCategory(self, uid, cate, topN=5):
        """按新闻类别进行推荐"""
        articleList = self.articles.getByCategory(cate=cate)
        recordList = self.records.getByUid(uid)
        userRecordAids = [record.aid for record in recordList]
        # 过滤掉阅读过的新闻
        articleList = [article for article in articleList if article.aid not in userRecordAids]

        return articleList[:topN] if topN < len(articleList) else articleList

    def recommendByInterest(self, uid, topN=5):
        """按用户浏览历史进行推荐"""
        if not self.model:
            articleList = self.articles.getAll()
            self.aidList = [article.aid for article in articleList]
            afs = self.articles.getArticleFeatures(self.aidList)
            self.model = NearestNeighbors(n_neighbors=self.maxNum, algorithm='auto', metric='cosine').fit(afs)
        user = self.users.getById(uid)
        recordList = self.records.getByUid(uid)
        recordAids = [record.aid for record in recordList]
        distance, candidates = self.model.kneighbors([BaseUtil.line2float64list(user.interest)])
        temp = []
        for i in range(self.maxNum):
            temp.append((candidates[0][i],  distance[0][i]))
        # 按距离从小到大排，即按相似度从大到小排
        # print(temp)
        temp.sort(key=lambda x: x[1])
        res = []
        k = 0
        for can in temp:
            aid = self.aidList[can[0]]
            if aid in recordAids:
                continue
            res.append(self.articles.getByAid(aid))
            k += 1
            if k >= topN:
                break
        return res

    def recommendByInterest2(self, uid, topN=5):
        if not self.index:
            articleList = self.articles.getAll()
            self.aidList = [article.aid for article in articleList]
            afs = self.articles.getArticleFeatures(self.aidList)
            topicVectors = BaseUtil.lists2gensimlists(afs)
            self.index = NLPUtil.genSimilarityMatrix(topicVectors)
        user = self.users.getById(uid)
        recordList = self.records.getByUid(uid)
        recordAids = [record.aid for record in recordList]
        sims = self.index[BaseUtil.list2gensimlist(BaseUtil.line2float64list(user.interest))]
        sims = sorted(enumerate(sims), key=lambda item: -item[1])
        res = []
        k = 0
        for can in sims:
            aid = self.aidList[can[0]]
            if aid in recordList:
                continue
            res.append(self.articles.getByAid(aid))
            k += 1
            if k >= topN:
                break

        return res

    def recommendByKeyWords(self, uid, keyWordsList, topN=5):
        """按关键词搜索进行推荐"""
        articleList = self.articles.getByKeyWords(keyWordsList)
        recordList = self.records.getByUid(uid)
        userRecordsAids = [record.aid for record in recordList]
        # 过滤掉阅读过的新闻
        articleList = [article for article in articleList if article.aid not in userRecordsAids]

        return articleList[:topN] if topN < len(articleList) else articleList

