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
from extractor import extract_question_followers

reload(sys)
sys.setdefaultencoding('utf8')

class QuestionFollowers:

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
        self.follower_id_list = []
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
        self.get_followers()

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
                    return
                elif r.status_code == 200:
                    self.content = BeautifulSoup(r.content, "lxml")
                    return
                elif r.status_code == 401:
                        logger.info('Cookie过期，正在更换')
                        f = open('Cookies/question_followers_cookies.txt', "r")
                        Lines = f.readlines()
                        if len(Lines) == 0:
                            logger.info('备用Cookies用完！')
                            self.delLogger(logger)
                            sys.exit(0)
                        else:
                            self.change_cookie()
                            with open('User/question_followers_loseuser_' + str(self.fileNum) + '.txt','a+') as f1:
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

    def get_followers(self):
        self.copycookies()
        self.get_createpoint()
        self.questionUrl_list = extract_questionUrl()
        self.current_proxy = get_IP()
        self.get_cookie()
        dt = re.sub(r'[^0-9]', '', str(datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S')))
        for i in xrange(self.start, self.end):
            self.is_del = False
            self.state = False
            self.file.seek(0,2)
            dt1 = re.sub(r'[^0-9]', '', str(datetime.datetime.now().strftime('%Y-%m-%d')))
            News = self.type + ','+ str(i+1) + ',' + str(self.end) + ',' + str(dt1) + '\n'
            self.file.write(News)
            self.question_url = self.questionUrl_list[i]
            self.id = self.question_url.replace('/question/', '')
            logfielname = '/log/' + dt + sys._getframe().f_code.co_name + '.log'
            logger = Logger(logfilename=logfielname,
                        logname='正在爬取第' + str(i + 1) + '项问题的关注者').getlog()

            followers_url = u'https://www.zhihu.com/api/v4/questions/' + str(self.id) + u'/followers?include=data[*].gender,answer_count,articles_count,follower_count,is_following,is_followed&limit=10&offset={0}'
            follower_num = 0
            self.follower_id_list = extract_question_followers(self.id)
            while 1:
                try:
                    r = requests.get(followers_url, headers=self.headers, timeout=5, proxies=self.current_proxy)
                    time.sleep(3)
                    logger.info('第一次请求状态码' + str(r.status_code))
                    if r.status_code == 404:
                        self.is_del = True
                        logger.info('!!!该问题被删!!!')
                        self.delLogger(logger)
                        break
                    elif r.status_code == 200:
                        j = r.json()
                        follower_num = j['paging']['totals']
                    elif r.status_code == 401:
                        logger.info('Cookie过期，正在更换')
                        f = open('Cookies/question_followers_cookies.txt', "r")
                        Lines = f.readlines()
                        if len(Lines) == 0:
                            logger.info('备用Cookies用完！')
                            return
                        else:
                            self.change_cookie()
                            with open('User/question_followers_loseuser_' + str(self.fileNum) + '.txt','a+') as f1:
                                f1.write(str(i + 1) + '\n')
                    else:
                        return
                except Exception, e:
                    logger.error('获取关注者数出错！' + str(e))
                    self.current_proxy = get_IP()
                    logger.warning('切换ip代理!中断3秒！')
                    time.sleep(3)
                    continue
                else:
                    # 没有关注者的问题也要保存一下
                    if follower_num == 0:
                        logger.warning('问题没有关注者！')
                        data_plus = {'question_id': self.id, "follower_num": 0}
                        self.mongo.db.question_followers.insert(data_plus)
                        self.delLogger(logger)
                        break
                    else:
                        offset = 0
                        while 1:
                            try:
                                soup = requests.get(followers_url.format(str(offset)), headers=self.headers, timeout=5, proxies=self.current_proxy)
                                time.sleep(3)
                                logger.info('请求状态码' + str(soup.status_code))
                            except Exception, e:
                                logger.error('请求关注者出错！' + str(e))
                                self.current_proxy = get_IP()
                                logger.warning('切换ip代理!中断3秒！')
                                time.sleep(3)
                                continue
                            else:
                                followers_data = soup.json()
                                data = followers_data.get('data')
                                #print 'is_end:' + str(followers_data['paging']['is_end'])
                                logger.info('is_end?' + str(followers_data['paging']['is_end']))

                                if followers_data['paging']['is_end']:
                                    follower_list = []
                                    for i in range(0, len(data)):
                                        follower_url = data[i]['url_token']#用户ID
                                        follower_info = data[i]#全部信息

                                        info = {
                                        "follower_url": follower_url,
                                        "follower_info": follower_info
                                        }
                                        if follower_url in self.follower_id_list:
                                            break
                                        follower_list.append(info)
                                    data_plus = {
                                    "question_id": self.id,
                                    "follower_num": follower_num,
                                    "followers": follower_list
                                    }
                                    self.mongo.db.question_followers.insert(data_plus)
                                    logger.info('已经获得所有新增关注者！')
                                    logger.info('成功保存数据!')
                                    self.delLogger(logger)
                                    break
                                else:
                                    offset = offset + 10
                                    follower_list = []
                                    for i in range(0, len(data)):
                                        follower_url = data[i]['url_token']#用户ID
                                        follower_info = data[i]#全部信息
                                        info = {
                                        "follower_url": follower_url,
                                        "follower_info": follower_info
                                        }
                                        if follower_url in self.follower_id_list:
                                            self.state = True
                                            break
                                        follower_list.append(info)
                                    data_plus = {
                                    "question_id": self.id,
                                    "follower_num": follower_num,
                                    "followers": follower_list
                                    }
                                self.mongo.db.question_followers.insert(data_plus)
                                if self.state:
                                    self.delLogger(logger)
                                    break

                        self.delLogger(logger)
                        break

    def copycookies(self):
        with open('Cookies/cookies.txt', "r") as f:
            Lines = f.readlines()
        with open('Cookies/question_followers_cookies.txt','a+') as f_a:
            Lines1 = f_a.readlines()
            if len(Lines1) == 0:
                for line in Lines:
                    f_a.write(line)

    def change_cookie(self):
        with open('Cookies/question_followers_cookies.txt', "r") as f:
            Lines = f.readlines()
            dict = eval(Lines[0])
            self.type = dict['type']
            self.headers['Cookie'] = dict['Cookie']
            self.headers['x-udid'] = dict['x-udid']
        with open('Cookies/question_followers_cookies.txt', "w") as f_w:
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
        with open('Cookies/question_followers_cookies.txt', "r") as f:
            Lines = f.readlines()
        with open('Cookies/question_followers_cookies.txt', "w") as f_w:
            for line in Lines:
                if self.type != eval(line)['type']:
                    f_w.write(line)

    def get_createpoint(self):
        self.file = open('CreatePoint/question_followers_createpoint_' + str(self.fileNum) + '.txt','a+')
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