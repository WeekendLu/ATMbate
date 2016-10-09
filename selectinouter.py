# -*- coding: utf-8 -*-
import pymongo
import time


class Inouter(object):
    def __init__(self):
        tdb = pymongo.MongoClient()
        db = tdb.stock
        self.stockname = []
        c = db.tcinfo.find({"date": {"$lte": time.time()}}).sort("date", pymongo.DESCENDING).limit(2832)
        for i in c:
            self.stockname.append(i["name"])




a = Inouter()
a = a.test()
print len(a)