import numpy as np
import time

class BaseUtil:
    """
      该类提供了相关的功能性函数，特别是对于Mysql无法存储向量问题,
      提供了向量和字符串之间的相互转换。
    """
    @staticmethod
    def list2line(lst):
        """将列表转换为字符串"""
        if not isinstance(lst, list) and not isinstance(lst, np.ndarray):
            raise TypeError('Error: the argument type must be a list!')
        try:
            return ' '.join(lst)
        except:
            lst = [str(i) for i in lst]
            return ' '.join(lst)

    @staticmethod
    def line2float64list(line):
        """字符串转换为数字型列表向量"""
        lst = line.split(' ')
        lst = [np.float64(i) for i in lst]
        return lst

    @staticmethod
    def line2strlist(line):
        """字符串转换为字符串型列表向量"""
        return line.split(' ')

    @staticmethod
    def list2gensimlist(lst):
        """普通向量转换为gensim格式的向量"""
        if not isinstance(lst, list) and not isinstance(lst, np.ndarray):
            raise TypeError('Error: the argument type must be a list!')
        res = []
        for i, e in enumerate(lst):
            if e > 0:
                pair = (i, e)
                res.append(pair)
        return res

    @staticmethod
    def lists2gensimlists(lsts):
        """普通向量集合转换为gensim格式的向量集合"""
        res = []
        for lst in lsts:
            res.append(BaseUtil.list2gensimlist(lst))
        return res

    @staticmethod
    def gensimlist2list(gsmlist, numTopics=100):
        """gensim格式的向量转换为普通的向量"""
        if not isinstance(gsmlist, list):
            raise TypeError('Error: the argument type must be a list!')
        vector = [0] * numTopics
        for pair in gsmlist:
            if not isinstance(pair, tuple):
                raise TypeError('Error: the element in gensimlist must be type of tuple!')
            vector[pair[0]] = pair[1]
        return vector

    @staticmethod
    def gensimlists2lists(gsmlists, numTopics=100):
        """gensim格式的向量集合转换为普通的向量集合"""
        res = []
        for gsmlist in gsmlists:
            res.append(BaseUtil.gensimlist2list(gsmlist, numTopics))
        return res

    @staticmethod
    def getCurrentTime():
        """获取当前时间"""
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

# if __name__ == '__main__':
#     lists = [
#         [(0, 1), (1, 1), (2, 1)],
#         [(0, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1)],
#         [(2, 1), (5, 1), (7, 1), (8, 1)],
#         [(1, 1), (5, 2), (8, 1)],
#         [(3, 1), (6, 1), (7, 1)],
#         [(9, 1)],
#         [(9, 1), (10, 1)],
#         [(9, 1), (10, 1), (11, 1)],
#         [(4, 1), (10, 1), (11, 1)]
#     ]
#     gsmlists1 = BaseUtil.gensimlists2lists(lists)
#     finallists = BaseUtil.lists2gensimlists(gsmlists1)
#     print(finallists)