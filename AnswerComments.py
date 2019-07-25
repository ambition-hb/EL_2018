#-*- coding:utf-8 –*-

import requests
from bs4 import BeautifulSoup
import re
import time
import sys
import datetime
from extractor import extract_answerID
from mongodb import Mongo,Mongo_1,Mongo_2
from proxy_pool import get_IP
from logger import Logger
from extractor import extract_answer_comments

reload(sys)
sys.setdefaultencoding('utf8')

class AnswerComments:

    def __init__(self, fileNum):
        self.answer_id = None
        self.is_del = False
        self.mongo = Mongo_1()
        self.fileNum = fileNum
        self.file = None
        self.start = None
        self.end = None
        self.answerID_list = None
        # self.proxy = None
        self.type = None
        self.state = False
        self.answer_type = None
        self.comment_id_list = []

        self.current_proxy = None
        self.headers = {
            'Accept': 'textml,application/json,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4,zh-TW;q=0.2',
            'Host': 'www.zhihu.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.81 Safari/537.36',
            'Referer': 'http://www.zhihu.com/',
            #需要修改
            'Cookie': None,
            'x-udid':None,
        }
        self.get_comment()
    # 获取评论，包含评论人信息
    def get_comment(self):
        self.copycookies()
        # ※从两个合并的数据库中抽取answerID※
        self.answerID_list = extract_answerID()
        print len(self.answerID_list)#输出回答ID列表的长度
        self.get_createpoint()
        self.current_proxy = get_IP()
        self.get_cookie()
        dt = re.sub(r'[^0-9]', '', str(datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S')))
        for i in xrange(self.start, self.end):
            self.file.seek(0,2)
            dt1 = re.sub(r'[^0-9]', '', str(datetime.datetime.now().strftime('%Y-%m-%d')))
            News = self.type + ','+ str(i+1) + ',' + str(self.end) + ',' + str(dt1) + '\n'
            self.file.write(News)
            self.answer_id = self.answerID_list[i]
            logfielname = '/log/' + dt + 'answer_' + sys._getframe().f_code.co_name + '.log'
            logger = Logger(logfilename=logfielname,
                        logname='正在爬取第' + str(i + 1) + '项回答的评论').getlog()

            url = r'https://www.zhihu.com/api/v4/answers/' + str(self.answer_id) + r'/comments?include=data%5B*%5D.author%2Ccollapsed%2Creply_to_author%2Cdisliked%2Ccontent%2Cvoting%2Cvote_count%2Cis_parent_author%2Cis_author&order=reverse&limit=20&offset={0}&status=open'
            comment_num = 0

            while 1:
                try:
                    r = requests.get(url, headers=self.headers, timeout=5, proxies=self.current_proxy)
                    time.sleep(3)
                    logger.info('第一次请求状态码' + str(r.status_code))
                    if r.status_code == 404:#服务器找不到请求的网页
                        self.is_del = True
                        logger.info('!!!该回答被删!!!')
                        self.delLogger(logger)
                        break
                    elif r.status_code == 200:#成功处理了请求
                        j = r.json()
                        comment_num = j['paging']['totals']
                    elif r.status_code == 401:#请求要求身份验证（针对于需要登陆的网页）
                        logger.info('Cookie过期，正在更换')
                        f = open('Cookies/answer_comments_cookies.txt', "r")
                        Lines = f.readlines()
                        if len(Lines) == 0:
                            logger.info('备用Cookies用完！')
                            self.delLogger(logger)
                            return
                        else:
                            self.change_cookie()
                            with open('User/answer_comments_loseuser_' + str(self.fileNum) + '.txt','a+') as f1:
                                f1.write(str(i + 1) + '\n')
                    else:
                        self.delLogger(logger)
                        return

                except Exception, e:
                    logger.error('查看评论数出错！' + str(e))
                    self.current_proxy = get_IP()
                    logger.warning('切换ip代理!中断3秒！')
                    time.sleep(5)
                    continue

                else:
                    # 没有评论的回答也要保存一下
                    if comment_num == 0:
                        logger.info('回答没有评论！')
                        self.delLogger(logger)
                        data_plus = {'answer_id': self.answer_id, "comment_num": 0}
                        self.mongo.db.answer_comments.insert(data_plus)
                        break
                    else:
                        offset = 0
                        while 1:
                            try:
                                soup = requests.get(url.format(str(offset)), headers=self.headers, timeout=5, proxies=self.current_proxy)
                                time.sleep(3)
                                logger.info('请求状态码' + str(soup.status_code))
                            except Exception, e:
                                logger.error('请求评论出错！' + str(e))
                                self.current_proxy = get_IP()
                                logger.warning('切换ip代理!中断3秒！')
                                time.sleep(5)
                                continue
                            else:
                                comments_data = soup.json()
                                data = comments_data['data']
                                #print 'is_end:' + str(comments_data['paging']['is_end'])
                                logger.info('is_end?' + str(comments_data['paging']['is_end']))
                                if comments_data['paging']['is_end']:
                                    comment_list = []
                                    for i in range(0, len(data)):
                                        commenter_id = data[i]['author']['member']['url_token']#用户ID
                                        comment_info = data[i]#全部信息
                                        info = {
                                        "commenter_id": commenter_id,
                                        "comment_info": comment_info
                                        }

                                        if comment_info['created_time'] > 1500566400:
                                            comment_list.append(info)
                                        else:
                                            break

                                    data_plus = {
                                    'answer_id': self.answer_id,
                                    "comment_num": comment_num,
                                    "comments": comment_list
                                    }

                                    self.mongo.db.answer_comments.insert(data_plus)

                                    logger.info('已获得该回答下所有评论！')
                                    break
                                else:
                                    offset = offset + 20
                                    comment_list = []
                                    for i in range(0, len(data)):
                                        commenter_id = data[i]['author']['member']['url_token']#用户ID
                                        comment_info = data[i]#全部信息
                                        info = {
                                        "commenter_id": commenter_id,
                                        "comment_info": comment_info
                                        }
                                        if comment_info['created_time'] > 1500566400:
                                            comment_list.append(info)
                                        else:
                                            self.state = True
                                            break

                                    data_plus = {
                                    'answer_id': self.answer_id,
                                    "comment_num": comment_num,
                                    "comments": comment_list
                                    }
                                    self.mongo.db.answer_comments.insert(data_plus)
                                    if self.state:
                                        self.delLogger(logger)
                                        break
                        logger.info('所有数据成功保存！')
                        self.delLogger(logger)
                        break

    def copycookies(self):
        with open('Cookies/cookies.txt', "r") as f:
            Lines = f.readlines()
        with open('Cookies/answer_comments_cookies.txt','a+') as f_a:
            Lines1 = f_a.readlines()
            if len(Lines1) == 0:
                for line in Lines:
                    f_a.write(line)

    def change_cookie(self):
        with open('Cookies/answer_comments_cookies.txt', "r") as f:
            Lines = f.readlines()
            dict = eval(Lines[0])
            self.type = dict['type']
            self.headers['Cookie'] = dict['Cookie']
            self.headers['x-udid'] = dict['x-udid']
        with open('Cookies/answer_comments_cookies.txt', "w") as f_w:
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
        with open('Cookies/answer_comments_cookies.txt', "r") as f:
            Lines = f.readlines()
        with open('Cookies/answer_comments_cookies.txt', "w") as f_w:
            for line in Lines:
                if self.type != eval(line)['type']:
                    f_w.write(line)

    def get_createpoint(self):
        self.file = open('CreatePoint/answer_comments_createpoint_' + str(self.fileNum) + '.txt','a+')
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

    # 删除日志手柄
    def delLogger(self, myLogger):
        for myHandler in myLogger.handlers:
            myHandler.close()
            myLogger.removeHandler(myHandler)