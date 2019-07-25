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

    def __init__(self):

        self.mongo = Mongo_1()

    def get_people_detail(self, id, i, dt):

        url = "https://www.zhihu.com/people/" + str(id) + "/answers"

        detail = {"people": id}

        driver.get(url)
        time.sleep(2)

        content = driver.page_source

        soup = BeautifulSoup(content, 'lxml')
        logfielname = '/log/' + dt +  'answerers_' + sys._getframe().f_code.co_name + '.log'
        #answerers
        #question_followers
        #voters
        #commenters
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
                driver.find_element_by_xpath("//button[@class='Button ProfileHeader-expandButton Button--plain']").click()
            except Exception, e:
                logger.error('无其他详细资料！')
            else:
                content = driver.page_source
                soup = BeautifulSoup(content, 'lxml')

                items = soup.findAll('div', class_='ProfileHeader-detailItem')

                for item in items:
                    key = item.find('span', class_='ProfileHeader-detailLabel').get_text()
                    value = item.find('div', class_=re.compile("ProfileHeader-detailValue$")).get_text()

                    detail[key] = value

        # self.mongo.db.question_editors_userDetail_1111.insert(detail)
        logger.info('用户信息已保存！')
        self.mongo.db.answerers_userDetail.insert(detail)
        # self.mongo.db.question_followers_userDetail_2222.insert(detail)
        # self.mongo.db.voters_userDetail_2222.insert(detail)
        # self.mongo.db.commenters_userDetail.insert(detail)
        self.delLogger(logger)
        self.mongo.client.close()

    # 删除日志手柄
    def delLogger(self, myLogger):
        for myHandler in myLogger.handlers:
            myHandler.close()
            myLogger.removeHandler(myHandler)

if __name__ == '__main__':

    userID_list = []
    mongo = Mongo_1()
    items = mongo.db.answerers.find()
    for item in items:
        userID_list.append(item.get('user_id'))
    mongo.client.close()

    ud = UserDetail()

    #driver = webdriver.Chrome()
    driver = webdriver.PhantomJS(executable_path=r'D:\PhantomJS\phantomjs-2.1.1-windows\bin\phantomjs.exe')

    dt = re.sub(r'[^0-9]', '', str(datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S')))
    for i in xrange(2367, 4735):

        ud.get_people_detail(userID_list[i], i , dt)
        #time.sleep(1)

    driver.close()