# -*- coding: utf-8 -*-

from mongodb import MG

#返回一个IP
def get_IP():

    mongo = MG()
    try:
        proxy = mongo.db.proxy.find_one({}, {'proxy': 1, '_id': 0})
        py = proxy.get('proxy')
        mongo.db.proxies.remove({'proxy': py})
    except Exception as e:
        print '请求IP代理出错：' + str(e)
    else:
        print '已获取新IP代理'

    return py

#返回IP列表
def get_IPs(num=10):

    mongo = MG()
    ip_list = []
    try:
        proxies = mongo.db.proxies.find({}, {'proxy': 1, '_id': 0})
        for proxy in proxies:
            ip_list.append(proxy.get('proxy'))
        for i in xrange(num):
            mongo.db.proxies.remove({'proxy': ip_list[i]})
    except Exception as e:
        print '请求IP代理出错：' + e
    else:
        print '已获取新IP代理'

    return ip_list[0:num]