"""
    该模块提供的类主要提供中文分词，主题向量转换功能，
    最终计算出每篇新闻的特征向量

    这个模块应该单独运行，以产生新闻的向量！

    @Author：FLX
    @Date: 2018-4-2
"""
from enum import Enum
from Utils.CorpusProvider import CorpusProvider
from Utils.BaseUtil import BaseUtil
from Model.Entity import Articles, Article
from Utils.CacheUtil import CacheUtil
import jieba
from gensim import corpora, models, similarities
from gensim.models import ldamodel, lsimodel

# 枚举常量
# 选择主题转换的模型
class TopicMethod(Enum):
    LDA = 'LDA'
    LSI = 'LSI'

class WordExtrator:
    """
        功能：新闻分词
    """
    path = {}
    path['stopWords'] = 'stop_words.txt'

    def __init__(self):
        self.stopWords = WordExtrator.loadStopWords()

    @staticmethod
    def loadStopWords():
        """加载停用词词典"""
        stop_words = [w.strip() for w in open(WordExtrator.path['stopWords'], 'r', encoding='utf8').readlines() if w.strip()]
        return stop_words

    @staticmethod
    def isAlphaOrNumeric(word):
        """判断是否是数字或字幕"""
        try:
            if word.encode('ascii').isalpha() or word.encode('ascii').isalnum():
                return True
            if float(word.encode('ascii')):
                return True
        except UnicodeEncodeError:
            return False
        except ValueError:
            return False

    def tokenize(self, sentence):
        """传入一条文本分词"""
        seg_list = [w for w in jieba.cut(sentence) if w not in self.stopWords and not WordExtrator.isAlphaOrNumeric(w)
                    and len(w) > 1 and w != '\t']
        return seg_list

    def tokenizeAll(self, sentenceList):
        """传入文本列表分词并返回 列表的列表"""
        res = []
        for sentence in sentenceList:
            res.append(' '.join(self.tokenize(sentence)))
        return res


class TopicVectorTransform:
    """
        功能：主题向量转换，采用了gensim库实现
    """
    def __init__(self):
        self.dictionary = None

    def generateDictionary(self, wordsLists):
        dictionary = corpora.Dictionary(wordsLists)
        once_ids = [tokenid for tokenid, docfreq in dictionary.dfs.items() if docfreq == 1]  # 去除词频为1的词
        dictionary.filter_tokens(once_ids)
        dictionary.compactify()
        self.dictionary=dictionary
        CacheUtil.dumpDictionary(dictionary)

    def generateBow(self, wordsLists):
        """step2: BOW转换"""
        if not self.dictionary:
            self.generateDictionary(wordsLists)
        bowCorpus = [self.dictionary.doc2bow(line) for line in wordsLists]
        return bowCorpus

    def generateTfidf(self, bowCorpus):
        """step3: Tfidf转换"""
        # 对整个语料库进行TFIDF转换
        tfidfModel = models.TfidfModel(bowCorpus, id2word=self.dictionary)
        tfidfCorpus = tfidfModel[bowCorpus]
        CacheUtil.dumpTfidfModel(tfidfModel)
        return tfidfCorpus

    def generateTopic(self,wordsLists, method=TopicMethod.LSI, numTopics=25):
        """step4: 主题向量转换"""
        """Note:
               采用LDA转换后，经文本相似度比较后发现效果一点都不好，
               故而采用LSI转换，效果不错.
                                Created by flx on 2018-4-7
        """
        bowCorpus = self.generateBow(wordsLists)
        tfidfCorpus = self.generateTfidf(bowCorpus)
        if method == TopicMethod.LDA:
            instance = ldamodel.LdaModel(tfidfCorpus, id2word=self.dictionary, num_topics=numTopics)
            CacheUtil.dumpTopicModel(instance)
        elif method == TopicMethod.LSI:
            instance = lsimodel.LsiModel(tfidfCorpus, id2word=self.dictionary, num_topics=numTopics)
            CacheUtil.dumpTopicModel(instance)
        dstCorpus = instance[tfidfCorpus]
        features=[]
        # gensim转换后的格式是tuple列表格式，如：
        #   vec = [(0, 0.12345), (2,0.458124),(4,0.485263),(7,0.589542)...]
        # 只保存向量中的非零值
        # 我们转换为普通向量形式
        for doc in dstCorpus:
            vector=[0]*numTopics
            for pair in doc:
                vector[pair[0]] = pair[1]
            features.append(vector)
        return features


class CorpusHandler(WordExtrator, TopicVectorTransform):
    """
        综合了文本分词和主题向量转换的处理类
    """
    def __init__(self):
        WordExtrator.__init__(self)
        TopicVectorTransform.__init__(self)
        # 产生文章列表
        self.corpusProvider = CorpusProvider()
        # 保存处理后的新闻到数据库
        self.articles = Articles()

    def process(self):
        print('正在对新闻分词...')
        articles = []
        wordsLists = []
        for news in self.corpusProvider:
            if news:
                newInfo = news.strip().split('\t')
                title = newInfo[0]
                cate = newInfo[1]
                content = newInfo[2]
                wordsList = self.tokenize(content)
                article = Article(title=title, category=cate, content=content)
                article.wordsList = BaseUtil.list2line(wordsList)
                wordsLists.append(wordsList)
                articles.append(article)
        print('正在进行主题向量转换...')
        topicVectors = self.generateTopic(wordsLists)
        for i, article in enumerate(articles):
            article.topicVector = BaseUtil.list2line(topicVectors[i])
            article.pubDateTime = BaseUtil.getCurrentTime()
            print(i)
            # 有少部分新闻因为本身含有引号，
            # 组合成sql语句时会出错，只占一小部分比例，
            # 舍弃掉即可.
            self.articles.add(article)

# if __name__ == '__main__':
#     handle = CorpusHandler()
#     handle.process()

