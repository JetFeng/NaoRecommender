from Model.Entity import User, Users, Article, Articles
from Core.Recommend import ContentBasedRecommend
from Model.Entity import Records, Record
from Utils.BaseUtil import BaseUtil


if __name__ == '__main__':
    # print('hello!')
    # 创建用户集合对象,自动连接了用户表
    users = Users()

    # users.login(user)注册新用户功能，自动返回userid.

    # 注册一个新用户，只需要提供用户名
    # user = User('flx')
    # users.loginUser(user)

    # 从用户集合中获取一个用户
    user = users.getByName('flx')

    # 创建文章集合对象，自动连接了新闻表
    articles = Articles()

    # 创建推荐日志记录对象
    records = Records()

    # 创建推荐系统对象
    recommender = ContentBasedRecommend(users, articles, records)

    # 推荐新闻
    # 三种推荐方式：按兴趣推荐，按类别推荐，按关键词搜索推荐
    res = recommender.recommendByInterest(user.uid, topN=5)
    # res = recommender.recommendByCategory(user.uid, cate='娱乐', topN=5)
    # res = recommender.recommendByKeyWords(user.uid, keyWordsList=['NBA'], topN=5)

    for article in res:
        print('Robot:Recommend {user} {NewsTitle} {cate}'.format(user=user.uname, NewsTitle=article.title, cate=article.category))
        print('Robot:你想要继续听完整的这篇新闻吗(y/n)?')
        response = input('User: ')
        if response.lower() == 'y':
            print('Ronbot: {content}'.format(content=article.content))
            print('这篇新闻就这样了，您感觉如何(0/1)?')
            response = input('User:')
            record = Record(user.uid, article.aid, int(response), BaseUtil.getCurrentTime())
            records.add(record)
        print('Robot: 好的，继续为您推荐下一篇新闻')

    # 一轮推荐完成后进行模型兴趣更新
    userInterestAidList = records.getUserInterestAids(user.uid)
    userInterestArticleFeatures = articles.getArticleFeatures(userInterestAidList)

    users.updateInterest(user.uid, userInterestArticleFeatures)

    # res = recommender.recommendByInterest(user.uid, topN=5)
    # for article in res:
    #     print('Robot:Recommend {user} {NewsTitle} {cate}'.format(user=user.uname, NewsTitle=article.title,
    #                                                              cate=article.category))
    #     response = input('Robot:你想要继续听完整的这篇新闻吗(y/n)?')
    #     if response == 'y':
    #         print('Ronbot: {content}'.format(content=article.content))
    #         response = input('这篇新闻就这样了，您感觉如何(0/1)?')
    #         record = Record(user.uid, article.aid, int(response), BaseUtil.getCurrentTime())
    #         records.add(record)
    #     print('Robot: 好的，继续为您推荐下一篇新闻')

    # 一轮推荐完成后进行模型兴趣更新
    # userInterestAidList = records.getUserInterestAids(user.uid)
    # userInterestArticleFeatures = articles.getArticleFeatures(userInterestAidList)
    #
    # users.updateInterest(user.uid, userInterestArticleFeatures)



