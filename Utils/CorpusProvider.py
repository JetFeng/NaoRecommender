
class CorpusProvider:
    """
        该类从本地文件中提供原始新闻
        每条新闻包括 标题, 类别， 内容
    """

    def __init__(self, path='../Cache/data/data'):
        self.file = open(path, 'r', encoding='utf8')

    def __iter__(self):
        return self

    def __next__(self):
        return self.file.__next__()
