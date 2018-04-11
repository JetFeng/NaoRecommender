from gensim.models import Word2Vec
from gensim.models.word2vec import LineSentence
from gensim.models import KeyedVectors
from gensim import similarities
import os

class NLPUtil:

    dirPath = os.path.dirname(__file__)
    word_vectors = KeyedVectors.load(os.path.join(os.path.dirname(dirPath), 'Cache/model/w2v/word_vectors.model'))

    @staticmethod
    def findSimilarWords(word, k=5):
        """
         查询和查询词意思最相近的几个词
        """
        # print(word_vectors.model.wv[word])
        semi = ''
        try:
            semi = NLPUtil.word_vectors.wv.most_similar(word, topn=k)
        except KeyError:
            print('Error: the word not in w2v vocabulary!')

        for term in semi:
            print('%s, %s' % (term[0], term[1]))

    @staticmethod
    def genSimilarityMatrix(topicVecs):
        indexPath = os.path.join(os.path.dirname(NLPUtil.dirPath), 'Cache/model/Similarity.index')
        if os.path.exists(indexPath):
            return similarities.MatrixSimilarity.load(indexPath)
        index = similarities.MatrixSimilarity(topicVecs)
        index.save(indexPath)
        return index
