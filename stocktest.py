# -*- coding:utf-8 -*-
import pymongo
import time


class gethisinfo(object):
    def __init__(self, stockname, date):
        self.stockname = stockname
        self.time = int(time.mktime(time.strptime(date, "%Y-%m-%d")))
        tdb = pymongo.MongoClient()
        self.db = tdb.stock
        self.lastinfo = []
        self.hisinfo = []

    def findgood(self):
        info = self.db.info.find({"time": {"$lt": self.time}}).sort("time", pymongo.DESCENDING).limit(2854)
        goodlist = []
        for i in info:
            goodlist.append(i)
        goodname = []
        for i in goodlist:
            goodname.append(i["name"])


    def findlastinfo(self):
        lastinfo = self.db.info.find({"name": self.stockname, "time": {"$lt": self.time}}).sort("time", pymongo.DESCENDING).limit(1)
        for i in lastinfo:
            self.lastinfo.append(i)

    def findhisinfo(self):
        hisinfo =self.db.info.find({"name": self.stockname, "time": {"$lt": self.time}}).sort("time", pymongo.DESCENDING).skip(1).limit(5)
        for i in hisinfo:
            self.hisinfo.append(i)

    def showfinal(self):
        self.findlastinfo()
        self.findhisinfo()

        lastinfo = 0
        for i in xrange(len(self.lastinfo)):
            lastinfo = (self.lastinfo[i]["outer"], self.lastinfo[i]["inter"])
        hisinfo = []
        for i in xrange(len(self.hisinfo)):
            hisinfo.append((self.hisinfo[i]["outer"], self.hisinfo[i]["inter"]))
        # hisinfo = sum(hisinfo) / len(hisinfo)
        return lastinfo, hisinfo

goodinfo = []
stocklist = ["300082"]
date = "2016-06-08"
for stockname in stocklist:
    a = gethisinfo(stockname, date)
    a = a.showfinal()
    print a
