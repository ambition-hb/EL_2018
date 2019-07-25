#-*- coding:utf-8 –*-
import logging
import os

#用字典保存日志级别


class Logger:
    def __init__(self, logfilename, logname):

        #创建日志文件
        self.txtCreate(logfilename)

        # 创建一个logger
        self.logger = logging.getLogger(logname)
        self.logger.setLevel(logging.DEBUG)

        # 创建一个handler，用于写入日志文件
        logfilename2 = logfilename[1:]
        fh = logging.FileHandler(logfilename2)
        fh.setLevel(logging.DEBUG)

        # 再创建一个handler，用于输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        # 定义handler的输出格式
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        #formatter = format_dict[int(loglevel)]
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        # 给logger添加handler
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)


    def getlog(self):
        return self.logger


    # 删除日志句柄
    def delLogger(self):
        #logger = self.getlog()
        for myHandler in self.handlers:
            myHandler.close()
            self.removeHandler(myHandler)

    #建立txt文件
    def txtCreate(self, filename):

        BASE_DIR = os.path.dirname(__file__)  # 获取当前文件夹的绝对路径

        full_path = BASE_DIR + filename

        if not os.path.exists(full_path):
            if not os.path.exists(BASE_DIR+'\log'):
                os.mkdir(BASE_DIR+'\log')
            file = open(full_path,'w')
            file.close()
