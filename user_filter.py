#-*- coding:utf-8 –*-

import datetime
import time

from mongodb import Mongo,Mongo_1,Mongo_2



class Extractor:

    def __init__(self):
        self.user_list = []
        self.mongo = Mongo_1()


    # 从问题日志提取问题编辑者
    def extractFromLog(self):

        print '开始提取问题编辑者...'
        count = 1
        temp_list = []

        items = self.mongo.db.question_log.find({}, {"log": 1})

        for item in items:
            print '第%d个问题'% count
            count = count + 1
            log = item.get('log')
            for i in xrange(0, len(log)):
                temp = log[i].get('question_editor')
                if temp == None or temp == '':
                    continue
                else:
                    url_token = temp[8:]
                    temp_list.append(url_token)

        if temp_list == []:
            print '提取错误...'
        else:
            print len(temp_list)
            #去重
            temp_list = list(set(temp_list))
            print len(temp_list)
            for user in temp_list:
                self.user_list.append({'user_id': user})

        #self.mongo.insertToUsersByFilter(self.user_list)
        self.mongo.db.editors.insert_many(self.user_list)

        print '提取问题编辑者完毕...'

    # 从回答中提取回答者
    def extractFromAnswer(self):

        print '开始提取回答者...'
        count = 1
        temp_list = []

        items = self.mongo.db.question_answers.find({})
        for item in items:
            print '第%d个'% count
            count = count + 1
            if item.get('answer_num') == 0:
                print item.get('answer_num')
                continue
            else:
                answers = item.get('answers')
                for i in range(0, len(answers)):
                    temp = answers[i].get('author_url')
                    if temp == None or temp == '':
                        continue
                    else:
                        temp_list.append(temp)

        if temp_list == []:
            print '提取错误...'
        else:
            print len(temp_list)
            temp_list = list(set(temp_list))
            print len(temp_list)
            for user in temp_list:
                self.user_list.append({'user_id': user})

        #self.mongo.insertToUsersByFilter(self.user_list)
        self.mongo.db.answerers.insert_many(self.user_list)

        print '提取回答者完毕...'


    # 提取问题关注者
    def extractQuestionFollowers(self):

        print '开始提取问题关注者...'
        count = 1
        temp_list = []

        items = self.mongo.db.question_followers.find({}, {"follower_num": 1, "followers": 1 })
        for item in items:
            print '第%d个' % count
            count = count + 1
            if item.get('follower_num') == 0:
                print item.get('follower_num')
                continue
            else:
                self.user_list = []
                followers = item.get('followers')
                for i in range(0, len(followers)):
                    temp = followers[i].get('follower_url')
                    if temp == None or temp == '':
                        continue
                    else:
                        temp_list.append(temp)


        if temp_list == []:
            print '提取错误...'
        else:
            print len(temp_list)
            temp_list = list(set(temp_list))
            print len(temp_list)
            for user in temp_list:
                self.user_list.append({'user_id': user})

        #self.mongo.insertToUsersByFilter(self.user_list)
        self.mongo.db.followers.insert_many(self.user_list)

        print '提取问题关注者完毕...'

    # 提取点赞者
    def extractVoters(self):

        print '开始提取回答点赞者...'
        count = 1
        temp_list = []

        items = self.mongo.db.answer_voters.find({}, {'voter_num': 1, 'voters': 1})
        for item in items:
            print '第%d个回答' % count
            count += 1
            if item.get('voter_num') == 0:
                print item.get('voter_num')
                continue
            else:
                voters = item.get('voters')
                for i in xrange(0, len(voters)):
                    temp = voters[i].get('voter_id')
                    if temp == None or temp == '':
                        continue
                    else:
                        temp_list.append(temp)

        if temp_list == []:
            print '提取错误...'
        else:
            print len(temp_list)
            temp_list = list(set(temp_list))
            print len(temp_list)
            for user in temp_list:
                self.user_list.append({'user_id': user})

        #self.mongo.insertToUsersByFilter(self.user_list)
        self.mongo.db.voters.insert_many(self.user_list)

        print '提取回答点赞者完毕...'

    # 提取评论者
    def extractCommenters(self):

        print '开始提取评论者...'
        count = 1
        temp_list = []

        items = self.mongo.db.answer_comments.find({}, {'comment_num': 1, 'comments': 1})
        for item in items:
            print '第%d个评论...' % count
            count += 1
            if item.get('comment_num') == 0:
                print item.get('comment_num')
                continue
            else:
                comments = item.get('comments')
                for i in xrange(0, len(comments)):
                    temp = comments[i].get('commenter_id')
                    if temp == None or temp == '':
                        continue
                    else:
                        temp_list.append(temp)

        if temp_list == []:
            print '提取错误...'
        else:
            print len(temp_list)
            temp_list = list(set(temp_list))
            print len(temp_list)
            for user in temp_list:
                self.user_list.append({'user_id': user})

        #self.mongo.insertToUsersByFilter(self.user_list)
        self.mongo.db.commenters.insert_many(self.user_list)

        print '提取评论者完毕...'

        #评论者数：28472

    # 把所有‘者’都放到一个集合中
    def getAllUsers(self):

        users = []
        items = self.mongo.db.all_users_by_filter.find({},{'url_token':1, '_id':0})
        for item in items:
            users.append(item.get('url_token'))

        #print len(users)
        self.user_list = list(set(users))
        #print len(self.user_list)

        return self.user_list


        #print count
        #32656用时：0:00:00.118000【问题编辑者和回答者】
        #223472用时：0:00:01.449000【加入问题关注者后】




if __name__ == "__main__":

    begin = datetime.datetime.now()
    #创建对象
    extr = Extractor()
    #从问题日志提取问题编辑者
    # extr.extractFromLog()#21409用时：0:00:05.147000
    #从回答中提取回答者(在开始之前先导入旧的回答)
    # extr.extractFromAnswer()#36719用时：0:00:10.768000_第11740个
    #提取问题关注者
    # extr.extractQuestionFollowers()

    #（等3跑完）提取点赞者
    #extr.extractVoters()
    #（等3跑完）提取评论者
    extr.extractCommenters()

    #把所有“者”放在一个集合中
    #extr.getAllUsers()

    end = datetime.datetime.now()

    print '用时：' + str(end - begin)