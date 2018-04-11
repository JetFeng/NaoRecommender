import pickle as pk
import os
from gensim import corpora

class CacheUtil:
    """
        缓存相关模型和文件
    """
    path = {}
    path['data'] = None
    path['dictionary'] = '../Cache/model/articles.dict'
    path['tfidfModel'] = '../Cache/model/tfidf.mo'
    path['topicModel'] = '../Cache/model/topic.mo'
    path['articleFeature'] = None
    path['userInterest'] = None
    path['recommendation'] = None

    @staticmethod
    def loadDictionary():
        return corpora.Dictionary.load(CacheUtil.path['dictionary'])

    @staticmethod
    def dumpDictionary(dictionary):
        dictionary.save(CacheUtil.path['dictionary'])

    @staticmethod
    def dumpTfidfModel(tfidfModel):
        tfidfModel.save(CacheUtil.path['tfidfModel'])

    @staticmethod
    def dumpTopicModel(topicModel):
        topicModel.save(CacheUtil.path['topicModel'])

    @staticmethod
    def dumpArticleFeature(feature):
        pk.dump(feature,open(CacheUtil.path["articleFeature"],'wb'))

    @staticmethod
    def loadArticleFeature():
        if not os.path.exists(CacheUtil.path["articleFeature"]):
            return None
        return pk.load(open(CacheUtil.path["articleFeature"],'rb'))

    @staticmethod
    def dumpUserInterest(interest):
        pk.dump(interest, open(CacheUtil.path['userInterest'], 'wb'))

    @staticmethod
    def loadUserInterest():
        if not os.path.exists(CacheUtil.path["userInterest"]):
            return None
        return pk.load(open(CacheUtil.path["userInterest"],'rb'))