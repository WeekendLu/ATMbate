# -*- coding:utf-8 -*-
import pymongo
import time


class Strategy(object):

    def __init__(self, stockname, testday):
        self.stockname = stockname
        # testday = '2016-05-03'
        self.date = int(time.mktime(time.strptime(testday, "%Y-%m-%d")))
        # self.date = date
        self.infolist = []
        self.datelist = []
        self.BuyTargetList = []
        self.Amplitude = 0

    def makeinfo(self):
        tdb = pymongo.MongoClient()
        db = tdb.stock
        c = db.info.find({"name": self.stockname, "time": {"$lt": self.date}}).sort("time", pymongo.DESCENDING).limit(40).skip(1)
        for o in c:
            self.infolist.append((o["time"], o["highest"], o["lowest"]))
            self.datelist.append((o["time"], o["highest"], o["lowest"]))

    def getbidprice(self, ):
        self.makeinfo()
        try:
            lowestinfolist = self.infolist
            lowestinfolist.sort(key=lambda x: x[2])
            dateinfolist = self.datelist
            dateinfolist.sort(key=lambda x: x[0], reverse=True)
            lowerstprice = lowestinfolist[0][2]
            for i in range(len(lowestinfolist)):
                LPT = lowestinfolist[i][2] - lowerstprice
                lowestday = lowestinfolist[0]
                thisday = lowestinfolist[i]
                LDT = dateinfolist.index(lowestday) - dateinfolist.index(thisday)#计算低的两天时间差
                TLD = dateinfolist.index(thisday)#第二天低到上个交易日时间
                if LDT > 0:
                    EDBA = LPT / LDT
                    BuyTarget = EDBA * TLD + dateinfolist[0][2]
                    if dateinfolist[0][1] > BuyTarget > dateinfolist[0][2]:
                        BuyTarget = float('%.2f' % (BuyTarget + EDBA))
                        self.BuyTargetList.append(BuyTarget)
                        self.Amplitude = dateinfolist[0][2] / dateinfolist[0][1]
            self.BuyTargetList.sort()
            if len(self.BuyTargetList) > 0:
                return self.stockname, self.BuyTargetList
            else:
                return self.stockname, self.BuyTargetList
        except IndexError:
            return "oops"



# b = Strategy("000858")
# a = b.getbidprice()
# print a