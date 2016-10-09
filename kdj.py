# -*- coding:utf-8 -*-

import pymongo
import time

class KDJ(object):
    def __init__(self, testday):
        tdb = pymongo.MongoClient()
        self.db = tdb.stock
        self.today = int(time.mktime(time.strptime(testday, "%Y-%m-%d")))
        info = self.db.info.find({"time": {"$lt": self.today}}).sort("time", pymongo.DESCENDING).limit(2847)
        self.allinfo = []
        for i in info:
            self.allinfo.append(i)
        self.final = []
        self.countday = 9
        self.RSV = 0

    def makeRSV(self):
        selector = self.final
        self.final = []
        for i in xrange(len(selector)):
            name = selector[i]["name"]
            info = self.db.info.find({"name": name, "time": {"$lt": self.today}}).sort("time", pymongo.DESCENDING).limit(self.countday)
            lowestlist = []
            highestlist = []
            for j in xrange(len(info)):
                lowestlist.append(info[j]["lowest"])
                highestlist.append(info[j]["highest"])
            ln = min(lowestlist)
            hn = max(highestlist)
            cn = selector[i]["currentprice"]
            self.RSV = (cn - ln) / (hn - ln) * 100

    def K(self):
        pass
