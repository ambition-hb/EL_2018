#-*- coding:utf-8 –*-

from pymongo import MongoClient


# 可以通过ObjectId方法把str转成ObjectId类型
from bson.objectid import ObjectId
'''
print "_id 转换成ObjectId类型"
print coll.find_one({"_id": ObjectId(str(obj_id))})'''

class MG:
    def __init__(self):
        #建立连接
        uri = 'mongodb://dev:Chenshi2017@58.206.96.135:20250'
        self.client = MongoClient(uri)
        self.db = self.client.zhihu

class Mongo_1:
    def __init__(self):
        uri = 'mongodb://dev:Chenshi2017@58.206.96.135:20250'
        self.client = MongoClient(uri)
        self.db = self.client.EL

class Mongo_2:
    def __init__(self):
        uri = 'mongodb://dev:Chenshi2017@58.206.96.135:20250'
        self.client = MongoClient(uri)
        self.db = self.client.PM


class Mongo:

    def __init__(self):
        #建立连接
        uri = 'mongodb://dev:ChenShi2017@58.206.96.135:20250'
        self.client = MongoClient(uri)
        self.db = self.client.EnglishLearning20171109

    # 问题种子
    def insertToQuestionUrl(self, data):

        self.db.question_url.insert(data)

    #############################################################################

    # 问题内容
    def insertToQuestionContent(self, data):

        self.db.question_content.insert(data)

    # 问题日志
    def insertToQuestionLog(self, data):

        self.db.question_log.insert(data)

    # 回答
    def insertToAnswer(self, data):

        self.db.answer.insert(data)

    # 问题关注者
    def insertToQuestionFollowers(self, data):

        self.db.question_followers.insert(data)

    #############################################################################

    # 点赞者
    def insertToVoters(self, data):

        self.db.voters.insert(data)

    # 评论
    def insertToComment(self, data):

        self.db.comment.insert(data)

    #############################################################################

    # 用户个人信息
    def insertToUserDetails(self, data):
        self.db.user_deatails.insert(data)

    # 用户记录信息
    def insertToUserInfo(self, data):
        self.db.user_info.insert(data)

    # 用户关注的人
    def insertToUserFollowing(self, data):
        self.db.user_following.insert(data)

    # 用户关注者
    def insertToUserFollowers(self, data):
        self.db.user_followers.insert(data)

    # 用户关注的话题
    def insertToUserFollowTopics(self, data):
        self.db.user_follow_topics.insert(data)

    #############################################################################

    # 关注者、问题编辑者、回答者、点赞者去重
    def insertToUsersByFilter(self, data):
        self.db.all_users_by_filter.insert_many(data)

    # 第二层用户
    def insertToSecondUsers(self, data):
        pass

    # 第三层用户
    def insertToThirdUsers(self, data):
        pass