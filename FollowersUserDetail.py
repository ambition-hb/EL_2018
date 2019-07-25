# -*- coding:utf-8 –*-

import datetime
import time

import sys
from bs4 import BeautifulSoup
import re
import json

from selenium import webdriver
from mongodb import Mongo,Mongo_1
from user_filter import Extractor
from logger import Logger

class UserDetail:

    def __init__(self, fileNum):
        self.fileNum = fileNum
        self.mongo = Mongo_1()
        self.userID_list = []
        self.id = None
        self.file = None
        self.start = None
        self.end = None
        self.driver = None

        self.get_people_detail()

    def get_people_detail(self):
        self.get_createpoint()
        self.driver = webdriver.PhantomJS(executable_path=r'E:\PhantomJS\phantomjs-2.1.1-windows\bin\phantomjs.exe')
        items = self.mongo.db.followers_new.find()
        for item in items:
            self.userID_list.append(item.get('user_id'))
        dt = re.sub(r'[^0-9]', '', str(datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S')))
        for i in xrange(self.start, self.end):
            self.id = self.userID_list[i]
            self.file.seek(0,2)
            dt1 = re.sub(r'[^0-9]', '', str(datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S')))
            News = str(i+1) + ',' + str(self.end) + ',' + str(dt1) + '\n'
            self.file.write(News)
            url = "https://www.zhihu.com/people/" + str(self.id) + "/answers"
            detail = {"people": self.id}
            self.driver.get(url)
            time.sleep(2)
            content = self.driver.page_source
            soup = BeautifulSoup(content, 'lxml')
            logfielname = '/log/' + dt +  'answerers_' + sys._getframe().f_code.co_name + '.log'
            logger = Logger(logfilename=logfielname,
                        logname='正在爬取第' + str(i + 1) + '个用户的个人资料').getlog()
            try:
                gender = soup.find('svg', class_=re.compile("Icon Icon\S+male")).get('class')
            except:
                logger.warning('暂无个人资料!')
            else:
                sex = re.search('\w{0,2}male$', gender[1]).group()
                detail["gender"] = sex
                try:
                    self.driver.find_element_by_xpath("//button[@class='Button ProfileHeader-expandButton Button--plain']").click()
                except Exception, e:
                    logger.error('无其他详细资料！')
                else:
                    content = self.driver.page_source
                    soup = BeautifulSoup(content, 'lxml')

                    items = soup.findAll('div', class_='ProfileHeader-detailItem')

                    for item in items:
                        key = item.find('span', class_='ProfileHeader-detailLabel').get_text()
                        value = item.find('div', class_=re.compile("ProfileHeader-detailValue$")).get_text()

                        detail[key] = value

            logger.info('用户信息已保存！')
            self.mongo.db.followers_userDetail.insert(detail)
            self.delLogger(logger)
        self.mongo.client.close()
        self.driver.close()

    # 删除日志手柄
    def delLogger(self, myLogger):
        for myHandler in myLogger.handlers:
            myHandler.close()
            myLogger.removeHandler(myHandler)

    def get_createpoint(self):
        self.file = open('CreatePoint/followers_userdetail_createpoint_' + str(self.fileNum) + '.txt','a+')
        Lines = self.file.readlines()
        if len(Lines) == 0:
            print '请输入爬取的起始点和终止点：'
            Input = raw_input()
            self.start = int(Input.split(',')[0])
            self.end = int(Input.split(',')[1].strip('\n'))
            self.file.write(Input + '\n')
        else:
            self.start = int(Lines[-1].split(',')[0])
            self.end = int(Lines[-1].split(',')[1].strip('\n'))
