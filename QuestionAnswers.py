#-*- coding:utf-8 –*-

import os
import requests
import sys
from bs4 import BeautifulSoup
import time
import re
import random
import datetime


from mongodb import Mongo,Mongo_1,Mongo_2
from proxy_pool import get_IP
from logger import Logger
from extractor import extract_questionUrl
from extractor import extract_question_answers

reload(sys)
sys.setdefaultencoding('utf8')

class QuestionAnswers:

    def __init__(self, fileNum):

        # self.question_url = question_url
        # self.id = question_url.replace('/question/', '')
        self.question_url = None
        self.id = None
        self.log_url = None
        self.url = None
        # self.log_url = 'https://www.zhihu.com' + question_url + '/log'
        # self.url = 'https://www.zhihu.com' + question_url #'/answers/created'
        self.url_domain = 'https://www.zhihu.com'
        self.content = None
        self.is_del = False
        self.fileNum = fileNum
        self.file = None
        self.start = None
        self.end = None
        # self.proxy = None
        self.type = None
        self.questionUrl_list = None
        self.topic_list = []
        self.log = []
        self.mongo = Mongo_1()
        self.current_proxy = None
        self.state = False
        self.question_type = None
        self.answer_id_list = []

        self.headers = {
            'Accept': 'textml,application/json,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4,zh-TW;q=0.2',
            'Host': 'www.zhihu.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36',
            'Referer': 'http://www.zhihu.com/',
            'Cookie': None,
            'x-udid':None,
        }
        self.get_answers()

    def parser(self, i, url, logger):

        while 1:
            try:
                r = requests.get(url, headers=self.headers, timeout=5, proxies=self.current_proxy)
                time.sleep(random.randint(3, 5))
                logger.info('请求状态码' + str(r.status_code))
                if r.status_code == 404:
                    self.is_del = True
                    logger.warning('!!!该问题被删!!!')
                    self.delLogger(logger)
                    break
                elif r.status_code == 200:
                    self.content = BeautifulSoup(r.content, "lxml")
                    break
                elif r.status_code == 401:
                        logger.info('Cookie过期，正在更换')
                        f = open('Cookies/question_answers_cookies.txt', "r")
                        Lines = f.readlines()
                        if len(Lines) == 0:
                            logger.info('备用Cookies用完！')
                            self.delLogger(logger)
                            sys.exit(0)
                        else:
                            self.change_cookie()
                            with open('User/question_answers_loseuser_' + str(self.fileNum) + '.txt','a+') as f1:
                                f1.write(str(i + 1) + '\n')
                else:
                    self.delLogger(logger)
                    sys.exit(0)
            except Exception as e:
                logger.error(str(e))
                self.current_proxy = get_IP()
                logger.warning('切换ip代理!中断3秒！')
                time.sleep(3)
                continue

    def get_answers(self):
        self.copycookies()
        self.get_createpoint()
        self.questionUrl_list = extract_questionUrl()
        self.current_proxy = get_IP()
        self.get_cookie()
        dt = re.sub(r'[^0-9]', '', str(datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S')))
        for i in xrange(self.start, self.end):
            self.is_del = False
            self.file.seek(0,2)
            dt1 = re.sub(r'[^0-9]', '', str(datetime.datetime.now().strftime('%Y-%m-%d')))
            News = self.type + ','+ str(i+1) + ',' + str(self.end) + ',' + str(dt1) + '\n'
            self.file.write(News)
            self.question_url = self.questionUrl_list[i]
            self.id = self.question_url.replace('/question/', '')
            logfielname = '/log/' + dt + sys._getframe().f_code.co_name + '.log'
            logger = Logger(logfilename=logfielname,
                        logname='正在爬取第' + str(i + 1) + '项问题的回答').getlog()
            answer_url = 'https://www.zhihu.com/api/v4/questions/'+ str(self.id) +'/answers?include=data%5B*%5D.is_normal%2Cis_collapsed%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Cmark_infos%2Ccreated_time%2Cupdated_time%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cupvoted_followees%3Bdata%5B*%5D.author.follower_count%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics&offset={0}&limit=20&sort_by=created'
            answer_number = 0
            while 1:
                try:
                    r = requests.get(answer_url, headers=self.headers, timeout=5, proxies=self.current_proxy)
                    time.sleep(3)
                    logger.info('第一次请求状态码' + str(r.status_code))
                    if r.status_code == 404:
                        self.is_del = True
                        logger.info('!!!该问题被删!!!')
                        self.delLogger(logger)
                        break
                    elif r.status_code == 200:
                        j = r.json()
                        answer_number = j['paging']['totals']
                    elif r.status_code == 401:
                        logger.info('Cookie过期，正在更换')
                        f = open('Cookies/question_answers_cookies.txt', "r")
                        Lines = f.readlines()
                        if len(Lines) == 0:
                            logger.info('备用Cookies用完！')
                            self.delLogger(logger)
                            return
                        else:
                            self.change_cookie()
                            with open('User/question_answers_loseuser_' + str(self.fileNum) + '.txt','a+') as f1:
                                f1.write(str(i + 1) + '\n')
                    else:
                        self.delLogger(logger)
                        return
                except Exception, e:
                    logger.error('查看回答数出错！' + str(e))
                    self.current_proxy = get_IP()
                    logger.warning('切换ip代理!中断3秒！')
                    time.sleep(3)
                else:
                    # 没有回答的问题也要保存一下
                    if answer_number == 0:
                        logger.warning('该问题没有回答！')
                        self.delLogger(logger)
                        data_plus = {'question_id': self.id, "answer_num": 0}
                        self.mongo.db.question_answers.insert(data_plus)
                        break
                    else:
                        offset = 0
                        while 1:
                            try:
                                soup = requests.get(answer_url.format(str(offset)), headers=self.headers, timeout=5, proxies=self.current_proxy)
                                time.sleep(3)
                                logger.info('请求状态码' + str(soup.status_code))
                            except Exception, e:
                                logger.error('请求回答出错！' + str(e))
                                self.current_proxy = get_IP()
                                logger.warning('切换ip代理!中断3秒！')
                                time.sleep(3)
                                continue
                            else:
                                answer_data = soup.json()
                                answer_info = answer_data['data']
                                if answer_data['paging']['is_end']:
                                    answer_list = []
                                    for i in range(0, len(answer_info)):
                                        #回答时间
                                        created_time = answer_info[i]['created_time']
                                        #更新时间
                                        updated_time = answer_info[i]['updated_time']
                                        #回答的点赞数 int
                                        vote_count = answer_info[i]['voteup_count']
                                        #回答id int
                                        answer_id = answer_info[i]['id']
                                        #回答文本
                                        answer_content = answer_info[i]['content']
                                        #评论数
                                        comment_count = answer_info[i]['comment_count']
                                        #回答者
                                        author_json = answer_info[i]['author']
                                        #回答者url_token
                                        author_url = answer_info[i]['author']['url_token']
                                        data = {
                                        "created_time": created_time,
                                        "updated_time": updated_time,
                                        "vote_count": vote_count,
                                        "answer_id": answer_id,
                                        "answer_content": answer_content,
                                        "comment_count": comment_count,
                                        "author_json": author_json,
                                        "author_url": author_url,
                                        }
                                        if updated_time > 1500393600:
                                            answer_list.append(data)
                                        else:
                                            break
                                    data_plus = {
                                    "question_id": self.id,
                                    "answer_num": answer_number,
                                    "answers": answer_list
                                    }

                                    self.mongo.db.question_answers.insert(data_plus)
                                    logger.info('已获得该问题下所有回答！')
                                    break
                                else:
                                    offset = offset + 20
                                    answer_list = []
                                    for i in range(0, 20):
                                        #回答时间
                                        created_time = answer_info[i]['created_time']
                                        #更新时间
                                        updated_time = answer_info[i]['updated_time']
                                        #回答的点赞数 int
                                        vote_count = answer_info[i]['voteup_count']
                                        #回答id int
                                        answer_id = answer_info[i]['id']
                                        #回答文本
                                        answer_content = answer_info[i]['content']
                                        #评论数
                                        comment_count = answer_info[i]['comment_count']
                                        #回答者
                                        author_json = answer_info[i]['author']
                                        #回答者url_token
                                        author_url = answer_info[i]['author']['url_token']
                                        data = {
                                        "created_time": created_time,
                                        "updated_time": updated_time,
                                        "vote_count": vote_count,
                                        "answer_id": answer_id,
                                        "answer_content": answer_content,
                                        "comment_count": comment_count,
                                        "author_json": author_json,
                                        "author_url": author_url,
                                        }
                                        if updated_time > 1500393600:
                                            answer_list.append(data)
                                        else:
                                            self.state = True
                                            break
                                    data_plus = {
                                    "question_id": self.id,
                                    "answer_num": answer_number,
                                    "answers": answer_list
                                    }
                                    self.mongo.db.question_answers.insert(data_plus)
                                    if self.state:
                                        self.delLogger(logger)
                                        break

                        logger.info('成功保存数据！')
                        self.delLogger(logger)
                        break

    def copycookies(self):
        with open('Cookies/cookies.txt', "r") as f:
            Lines = f.readlines()
        with open('Cookies/question_answers_cookies.txt','a+') as f_a:
            Lines1 = f_a.readlines()
            if len(Lines1) == 0:
                for line in Lines:
                    f_a.write(line)

    def change_cookie(self):
        with open('Cookies/question_answers_cookies.txt', "r") as f:
            Lines = f.readlines()
            dict = eval(Lines[0])
            self.type = dict['type']
            self.headers['Cookie'] = dict['Cookie']
            self.headers['x-udid'] = dict['x-udid']
        with open('Cookies/question_answers_cookies.txt', "w") as f_w:
            for line in Lines[1:]:
                f_w.write(line)

    def get_cookie(self):
        with open('Cookies/cookies.txt', "r") as f:
            Lines = f.readlines()
            for line in Lines:
                dict = eval(line)
                if self.type == dict['type']:
                    self.headers['Cookie'] = dict['Cookie']
                    self.headers['x-udid'] = dict['x-udid']
        with open('Cookies/question_answers_cookies.txt', "r") as f:
            Lines = f.readlines()
        with open('Cookies/question_answers_cookies.txt', "w") as f_w:
            for line in Lines:
                if self.type != eval(line)['type']:
                    f_w.write(line)

    def get_createpoint(self):
        self.file = open('CreatePoint/question_answers_createpoint_' + str(self.fileNum) + '.txt','a+')
        Lines = self.file.readlines()
        if len(Lines) == 0:
            print '请输入爬取的Cookie编号、起始点和终止点：'
            Input = raw_input()
            self.type = Input.split(',')[0]
            self.start = int(Input.split(',')[1])
            self.end = int(Input.split(',')[2].strip('\n'))
            self.file.write(Input + '\n')
        else:
            self.type = Lines[-1].split(',')[0]
            self.start = int(Lines[-1].split(',')[1])
            self.end = int(Lines[-1].split(',')[2].strip('\n'))

    def delLogger(self, myLogger):
        for myHandler in myLogger.handlers:
            myHandler.close()
            myLogger.removeHandler(myHandler)