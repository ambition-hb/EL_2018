#-*- coding:utf-8 –*-

from mongodb import Mongo,Mongo_1,Mongo_2
import json
import datetime
import re

# 提取问题种子----（返回问题URL列表）
def extract_questionUrl():
    questionUrl_list = []
    mongo = Mongo_1()
    items = mongo.db.question_url.find({}, {"question_url": 1})#find()----检测字符串中是否包含子字符串str
    for item in items:
        questionUrl_list.append(item['question_url'])
    mongo.client.close()
    return questionUrl_list


# 提取回答ID----(返回回答ID列表)
def extract_answerID():
    answerID_list = []
    mongo = Mongo_1()
    temp_list = mongo.db.question_answers.find({}, {'answer_num': 1, 'answers': 1})
    # 旧的回答
    temp_list1 = mongo.db.answer.find({}, {'answer_num': 1, 'answers': 1})
    for item in temp_list:
        if item.get('answer_num') == 0:
            continue
        else:
            answer_list = item.get('answers')
            for answer in answer_list:
                answerID_list.append(answer.get('answer_id'))

    for item in temp_list1:
        if item.get('answer_num') == 0:
            continue
        else:
            answer_list = item.get('answers')
            for answer in answer_list:
                answerID_list.append(answer.get('answer_id'))

    mongo.client.close()
    #  去重
    return list(set(answerID_list))
    #换上面删下面
    # return answerID_list

#提取回答者的关注者ID----(返回回答者的关注者的ID列表)
def extract_answerers_followers(user_id, user_id_list):
    mongo = Mongo_1()
    follower_id = []
    if user_id in user_id_list:
        temp_list = mongo.db.haoyouguanxi.answerer_follower.find({"user_id":user_id})
        for list in temp_list:
            if list.get('follower') is not None:
                for l in list.get('follower'):
                    follower_id.append(l.get('follower_id'))
                break
        if len(follower_id) == 0:
            temp_list1 = mongo.db.haoyouguanxi.answerer_followers.find({"user_id":user_id})
            for list in temp_list1:
                if list.get('follower') is not None:
                    for l in list.get('follower'):
                        follower_id.append(l.get('follower_id'))
                    break
        follower_id.append('user_exists')
        mongo.client.close()
        return follower_id
    else:
        mongo.client.close()
        return follower_id

#提取回答者的关注了ID----(返回回答者的关注了的ID列表)
def extract_answerers_following(user_id, user_id_list):
    mongo = Mongo_1()
    following_id = []
    if user_id in user_id_list:
        temp_list = mongo.db.haoyouguanxi.answerer_following.find({"user_id":user_id})
        for list in temp_list:
            if list.get('following') is not None:
                for l in list.get('following'):
                    following_id.append(l.get('following_id'))
                break
        mongo.client.close()
        following_id.append('user_exists')
        return following_id
    else:
        mongo.client.close()
        return following_id

#提取评论者的关注了ID----(返回评论者的关注了的ID列表)
def extract_commenters_following(user_id, user_id_list):
    mongo = Mongo_1()
    following_id = []
    if user_id in user_id_list:
        temp_list = mongo.db.haoyouguanxi.commenter_following.find({"user_id":user_id})
        for list in temp_list:
            if list.get('following') is not None:
                for l in list.get('following'):
                    following_id.append(l.get('following_id'))
                break
        mongo.client.close()
        following_id.append('user_exists')
        return following_id
    else:
        mongo.client.close()
        return following_id

#提取评论者的关注者ID----(返回评论者的关注者的ID列表)
def extract_commenters_followers(user_id, user_id_list):
    mongo = Mongo_1()
    follower_id = []
    if user_id in user_id_list:
        temp_list = mongo.db.haoyouguanxi.commenter_follower.find({"user_id":user_id})
        for list in temp_list:
            if list.get('follower') is not None:
                for l in list.get('follower'):
                    follower_id.append(l.get('follower_id'))
                break
        mongo.client.close()
        follower_id.append('user_exists')
        return follower_id
    else:
        mongo.client.close()
        return follower_id

#提取编辑者的关注了ID----(返回编辑者的关注了的ID列表)
def extract_editors_following(user_id, user_id_list):
    mongo = Mongo_1()
    following_id = []
    if user_id in user_id_list:
        temp_list = mongo.db.haoyouguanxi.question_editors_following.find({"user_id":user_id})
        for list in temp_list:
            if list.get('following') is not None:
                for l in list.get('following'):
                    following_id.append(l.get('following_id'))
                break
        mongo.client.close()
        following_id.append('user_exists')
        return following_id
    else:
        mongo.client.close()
        return following_id

#提取编辑者的关注者ID----(返回编辑者的关注者的ID列表)
def extract_editors_followers(user_id, user_id_list):
    mongo = Mongo_1()
    follower_id = []
    if user_id in user_id_list:
        temp_list = mongo.db.haoyouguanxi.question_editors_follower.find({"user_id":user_id})
        for list in temp_list:
            if list.get('follower') is not None:
                for l in list.get('follower'):
                    follower_id.append(l.get('follower_id'))
                break
        mongo.client.close()
        follower_id.append('user_exists')
        return follower_id
    else:
        mongo.client.close()
        return follower_id

#提取关注者的关注了ID----(返回关注者的关注了的ID列表)
def extract_followers_following(user_id, user_id_list):
    mongo = Mongo_1()
    following_id = []
    if user_id in user_id_list:
        temp_list = mongo.db.haoyouguanxi.quesiton_follower_following.find({"user_id":user_id})
        for list in temp_list:
            if list.get('following') is not None:
                for l in list.get('following'):
                    following_id.append(l.get('following_id'))
                break
        if len(following_id) == 0:
            temp_list1 = mongo.db.haoyouguanxi.question_follower_following.find({"user_id":user_id})
            for list in temp_list1:
                if list.get('following') is not None:
                    for l in list.get('following'):
                        following_id.append(l.get('following_id'))
                    break
        mongo.client.close()
        following_id.append('user_exists')
        return following_id
    else:
        mongo.client.close()
        return following_id

#提取关注者的关注者ID----(返回关注者的关注者的ID列表)
def extract_followers_followers(user_id, user_id_list):
    mongo = Mongo_1()
    follower_id = []
    if user_id in user_id_list:
        temp_list = mongo.db.haoyouguanxi.question_followers_follower.find({"user_id":user_id})
        for list in temp_list:
            if list.get('follower') is not None:
                for l in list.get('follower'):
                    follower_id.append(l.get('follower_id'))
                break
        mongo.client.close()
        follower_id.append('user_exists')
        return follower_id
    else:
        mongo.client.close()
        return follower_id

#提取voters的关注了ID----（返回voters的关注了ID列表）
def extract_voters_following(user_id, user_id_list):
    mongo = Mongo_1()
    following_id = []
    if user_id in user_id_list:
        temp_list = mongo.db.haoyouguanxi.voter_following.find({"user_id":user_id})
        for list in temp_list:
            if list.get('following') is not None:
                for l in list.get('following'):
                    following_id.append(l.get('following_id'))
                break
        mongo.client.close()
        following_id.append('user_exists')
        return following_id
    else:
        mongo.client.close()
        return following_id

#提取voters的关注者ID----(返回voters的关注者ID列表)
def extract_voters_followers(user_id, user_id_list):
    mongo = Mongo_1()
    follower_id = []
    if user_id in user_id_list:
        temp_list = mongo.db.haoyouguanxi.voter_follower.find({"user_id":user_id})
        for list in temp_list:
            if list.get('follower') is not None:
                for l in list.get('follower'):
                    follower_id.append(l.get('follower_id'))
                break
        mongo.client.close()
        follower_id.append('user_exists')
        return follower_id
    else:
        mongo.client.close()
        return follower_id

#提取问题的回答ID----（返回问题的回答的ID列表）
def extract_question_answers(question_id):
    mongo = Mongo_1()
    temp_list = mongo.db.answer.find({"question_id":question_id})
    answer_id = []
    for list in temp_list:
        if list.get('answer_num') is not None:
            answer_id.append(list.get('answer_num'))
        break

    mongo.client.close()
    return answer_id

#提取问题的关注者ID----（返回问题的关注者的ID列表）
def extract_question_followers(question_id):
    mongo = Mongo_1()
    lists = mongo.db.english_followers_new.find({"question_id":question_id})
    follower_id = []
    for l in lists:
        if l.get('followers') is not None:
            for l1 in l.get('followers'):
                follower_id.append(l1)
    mongo.client.close()
    return follower_id

#提取问题的评论ID----(返回问题的评论的ID列表)
def extract_answer_comments(answer_id):
    mongo = Mongo_1()
    temp_list = mongo.db.comment.find({"answer_id":answer_id})
    comment_id = []
    for list in temp_list:
        if list.get('comment_num') is not None:
            comment_id.append(list.get('comment_num'))
        break

    mongo.client.close()
    return comment_id

#提取问题的voters----(返回问题的voter的ID)
def extract_answer_voters(answer_id):
    mongo = Mongo_1()
    lists = mongo.db.voters_old.find({"answer_id":answer_id})
    voter_id = []
    for l in lists:
        if l.get('voters') is not None:
            for l1 in l.get('voters'):
                voter_id.append(l1)
    mongo.client.close()
    return voter_id

#提取回答者的信息----（返回回答者的信息字典）
def extract_answerers_info():
    mongo = Mongo_1()
    temp_list = mongo.db.answerers_info_1111.find({},{"user_id":1})
    dt = {list.get('user_id'):"" for list in temp_list}
    mongo.client.close()
    return dt

#提取评论者的信息----（返回评论者的信息字典）
def extract_commenters_info():
    mongo = Mongo_1()
    temp_list = mongo.db.commenters_info_1111.find({},{"user_id":1})
    dt = {list.get('user_id'):"" for list in temp_list}
    mongo.client.close()
    return dt

#提取编辑者的信息----（返回编辑者的信息字典）
def extract_editors_info():
    mongo = Mongo_1()
    temp_list = mongo.db.question_editors_info_1111.find({},{"user_id":1})
    dt = {list.get('user_id'):"" for list in temp_list}
    mongo.client.close()
    return dt

#提取关注者的信息----（返回关注者的信息字典）
def extract_followers_info():
    mongo = Mongo_1()
    temp_list = mongo.db.question_followers_info_1111.find({},{"user_id":1})
    dt = {list.get('user_id'):"" for list in temp_list}
    mongo.client.close()
    return dt

#提取voters的信息----（返回voters的信息字典）
def extract_voters_info():
    mongo = Mongo_1()
    temp_list = mongo.db.voters_info_1111.find({},{"user_id":1})
    dt = {list.get('user_id'):"" for list in temp_list}
    mongo.client.close()
    return dt

#提取最后的提问者----（返回最后的提问者的ID列表）
def extract_last_answerers():
    mongo = Mongo_1()
    temp = mongo.db.answerers_last.find({})
    user_id_list = []
    for l in temp:
        user_id_list.append(l.get('user_id'))
    mongo.client.close()
    return user_id_list

#提取最后的评论者----（返回最后的评论者的ID列表）
def extract_last_commenters():
    mongo = Mongo_1()
    temp = mongo.db.commenters_last.find({})
    user_id_list = []
    for l in temp:
        user_id_list.append(l.get('user_id'))
    mongo.client.close()
    return user_id_list

#提取最后的编辑者----（返回最后的编辑者ID列表）
def extract_last_editors():
    mongo = Mongo_1()
    temp = mongo.db.editors_last.find({})
    user_id_list = []
    for l in temp:
        user_id_list.append(l.get('user_id'))
    mongo.client.close()
    return user_id_list

#提取最后的关注者----（返回最后的关注者的ID列表）
def extract_last_followers():
    mongo = Mongo_1()
    temp = mongo.db.followers_last.find({})
    user_id_list = []
    for l in temp:
        user_id_list.append(l.get('user_id'))
    mongo.client.close()
    return user_id_list

#提取最后的voters----(返回最后的voters的ID列表)
def extract_last_voters():
    mongo = Mongo_1()
    temp = mongo.db.voters_last.find({})
    user_id_list = []
    for l in temp:
        user_id_list.append(l.get('user_id'))
    mongo.client.close()
    return user_id_list

# if __name__ == "__main__":
#     print extract_answer_voters(255313072)