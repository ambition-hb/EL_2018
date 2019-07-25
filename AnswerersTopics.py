#_*_coding:utf8_*_
import requests
import sys
import time
import codecs
import re
import datetime
from bs4 import BeautifulSoup

from logger import Logger
from mongodb import Mongo,Mongo_1,Mongo_2
from proxy_pool import get_IP

reload(sys)
sys.setdefaultencoding('utf8')

class AnswerersTopics:

    def __init__(self, fileNum):
        self.user_id = None
        self.user_url = 'https://www.zhihu.com/people/' + str(self.user_id) +'/following'
        self.topic_url = self.user_url + '/topics'
        self.is_del = False
        # self.proxy = None
        self.userID_list = []
        self.fileNum = fileNum
        self.file = None
        self.start = None
        self.end = None
        self.type = None

        self.mongo = Mongo_1()
        self.mongo1 = Mongo()

        self.current_proxy = None
        self.content = None
        self.headers = {
            'Accept': 'textml,application/json,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4,zh-TW;q=0.2',
            'Host': 'www.zhihu.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.81 Safari/537.36',
            'Referer': 'http://www.zhihu.com/',
            'Cookie': None,
            'x-udid':None,
        }

        self.get_Topics()

    def parser(self, url, logger):

        while 1:
            try:
                r = requests.get(url, headers=self.headers, timeout=5, proxies=self.current_proxy)
                time.sleep(3)
                logger.info('请求状态码' + str(r.status_code))
                if r.status_code == 404:
                    logger.warning('该用户被删！无法获得用户信息!!!')
                    self.is_del = True
                    break
                if r.status_code == 200:
                    self.content = BeautifulSoup(r.content, "lxml")
                    break
            except Exception as e:
                logger.error('请求出错！' + str(e))
                self.current_proxy = get_IP()
                logger.warning('切换ip代理!中断3秒！')
                time.sleep(3)
                continue

    def get_Topics(self):
        self.copycookies()
        self.get_createpoint()
        items = self.mongo.db.answerers_new.find()
        for item in items:
            self.userID_list.append(item.get('user_id'))
        self.current_proxy = get_IP()
        self.get_cookie()
        dt = re.sub(r'[^0-9]', '', str(datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S')))
        for i in xrange(self.start, self.end):
            self.file.seek(0,2)
            dt1 = re.sub(r'[^0-9]', '', str(datetime.datetime.now().strftime('%Y-%m-%d')))
            News = self.type + ','+ str(i+1) + ',' + str(self.end) + ',' + str(dt1) + '\n'
            self.file.write(News)
            self.user_id = self.userID_list[i]
            logfielname = '/log/' + dt + 'answerers_' + sys._getframe().f_code.co_name + '.log'
            logger = Logger(logfilename=logfielname,
                            logname='正在爬取第' + str(i + 1) + '个用户的关注话题').getlog()
            topics_url = 'https://www.zhihu.com/api/v4/members/'+str(self.user_id)+'/following-topic-contributions?include=data%5B*%5D.topic.introduction&offset={0}&limit=20'
            topics_count = 0

            while 1:
                try:
                    r = requests.get(topics_url, headers=self.headers, timeout=5, proxies=self.current_proxy)
                    time.sleep(3)
                    logger.info('第一次请求状态码' + str(r.status_code))
                    if r.status_code == 200:
                        j = r.json()
                        topics_count = j['paging']['totals']
                    elif r.status_code == 404:
                        self.is_del = True
                        logger.info('!!!该用户被删!!!')
                        self.delLogger(logger)
                        break
                    elif r.status_code == 401:
                        logger.info('Cookie过期，正在更换')
                        f = open('Cookies/answerers_topics_cookies.txt', "r")
                        Lines = f.readlines()
                        if len(Lines) == 0:
                            logger.info('备用Cookies用完！')
                            self.delLogger(logger)
                            return
                        else:
                            self.change_cookie()
                            with open('User/answerers_topics_loseuser_' + str(self.fileNum) + '.txt','a+') as f1:
                                f1.write(str(i + 1) + '\n')
                    else:
                        self.delLogger(logger)
                        return

                except Exception, e:
                    logger.error('查看回答数出错！' + str(e))
                    self.current_proxy = get_IP()
                    logger.warning('切换ip代理!中断3秒！')
                    time.sleep(3)
                    continue

                else:
                    # 没有关注者的用户也要保存一下
                    if topics_count == 0:
                        logger.warning('用户没有关注话题！')
                        self.delLogger(logger)
                        data_plus = {'user_id': self.user_id, "topics_count": 0}
                        self.mongo.db.answerers_topics.insert(data_plus)
                        break
                    else:
                        offset = 0
                        while 1:
                            try:
                                soup = requests.get(topics_url.format(str(offset)), headers=self.headers, timeout=5, proxies=self.current_proxy)
                                time.sleep(3)
                                logger.info('请求状态码' + str(soup.status_code))
                            except Exception, e:
                                logger.error('请求关注话题出错！' + str(e))
                                self.current_proxy = get_IP()
                                logger.warning('切换ip代理!中断3秒！')
                                time.sleep(3)
                                continue
                            else:
                                topics_data = soup.json()
                                data = topics_data.get('data')
                                logger.info('is_end?' + str(topics_data['paging']['is_end']))
                                if topics_data['paging']['is_end']:
                                    topic_list = []
                                    for i in range(0, len(data)):
                                        info = {
                                        "name": data[i]['topic']['name'],
                                        "contributions_count": data[i]['contributions_count']
                                        }
                                        topic_list.append(info)
                                    data_plus = {
                                        'user_id': self.user_id,
                                        "topics_count": topics_count,
                                        "topic": topic_list
                                    }

                                    self.mongo.db.answerers_topics.insert(data_plus)

                                    logger.info('已获得所有用户关注话题！')
                                    logger.info('成功保存数据！')
                                    self.delLogger(logger)
                                    break
                                else:
                                    offset = offset + 20
                                    topic_list = []
                                    for i in range(0, len(data)):
                                        info = {
                                        "name": data[i]['topic']['name'],
                                        "contributions_count": data[i]['contributions_count']
                                        }
                                        topic_list.append(info)
                                    data_plus = {
                                    'user_id': self.user_id,
                                    "topics_count": topics_count,
                                    "topic": topic_list
                                    }

                                    self.mongo.db.answerers_topics.insert(data_plus)

                        self.mongo.client.close()
                        break

    def copycookies(self):
        with open('Cookies/cookies.txt', "r") as f:
            Lines = f.readlines()
        with open('Cookies/answerers_topics_cookies.txt','a+') as f_a:
            Lines1 = f_a.readlines()
            if len(Lines1) == 0:
                for line in Lines:
                    f_a.write(line)

    def change_cookie(self):
        with open('Cookies/answerers_topics_cookies.txt', "r") as f:
            Lines = f.readlines()
            dict = eval(Lines[0])
            self.type = dict['type']
            self.headers['Cookie'] = dict['Cookie']
            self.headers['x-udid'] = dict['x-udid']
        with open('Cookies/answerers_topics_cookies.txt', "w") as f_w:
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
        with open('Cookies/answerers_topics_cookies.txt', "r") as f:
            Lines = f.readlines()
        with open('Cookies/answerers_topics_cookies.txt', "w") as f_w:
            for line in Lines:
                if self.type != eval(line)['type']:
                    f_w.write(line)

    def get_createpoint(self):
        self.file = open('CreatePoint/answerers_topics_createpoint_' + str(self.fileNum) + '.txt','a+')
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