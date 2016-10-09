# -*- coding:utf-8 -*-

import pymongo
import time


class StockSelector(object):
    def __init__(self, testday):
        tdb = pymongo.MongoClient()
        self.db = tdb.stock
        self.today = int(time.mktime(time.strptime(testday, "%Y-%m-%d")))
        # self.today = time.time()
        info = self.db.tctimeinfo.find({"time": {"$lte": self.today}}).sort("time", pymongo.DESCENDING).limit(2832)
        self.allinfo = []
        for i in info:
            self.allinfo.append(i)
        self.final = []
        self.stop = []
        self.goodnumber = 0

    def moveStop(self):
        selector = self.allinfo
        self.final = []
        for i in range(len(selector)):
            if selector[i]["vol"] != 0:
                self.final.append(selector[i])

    def moveCirculationmarketvalue(self):
        selector = self.final
        self.final = []
        for i in range(len(selector)):
            if 90 <= selector[i]["circulationmarketvalue"] <= 300:
                self.final.append(selector[i])

    def selectPE(self):#筛选市盈率
        selector = self.allinfo
        for i in range(len(selector)):
            peratio = selector[i]["peratio"]
            if 0 < peratio < 150:
                self.final.append(selector[i])

    def selectRetailnetin(self):#筛选散户净流
        selector = self.final
        self.final = []
        for i in range(len(selector)):
            if selector[i]["retailnetin"] < 500:
                self.final.append(selector[i])
        self.final.sort(key=lambda x: x["retailnetin"])

    def selectTurnoverrate(self):#筛选换手率
        selector = self.final
        self.final = []
        selector.sort(key=lambda x: x["turnoverrate"], reverse=True)
        for i in range(len(selector)):
            self.final.append(selector[i])

    def selectAmplitudepc(self):#筛选振幅
        selector = self.final
        self.final = []
        for i in range(len(selector)):
            if selector[i]["amplitudepc"] < 22:
                self.final.append(selector[i])

    def selectIncreasepc(self):#筛选涨幅
        selector = self.final
        self.final = []
        for i in range(len(selector)):
            if selector[i]["increasepc"] < 11:
                self.final.append(selector[i])

    def selectBigpowernetin(self):#筛选主力净流入/流通市值
        selector = self.final
        self.final = []
        for i in range(len(selector)):
            if selector[i]["name"][0] != "3" and selector[i]["name"] != "603701" and selector[i]["name"] != "603798" and selector[i]["name"] != "603868" and selector[i]["name"] != "002684" and selector[i]["name"] != "002788" and selector[i]["name"] != "002793" and selector[i]["name"] != "002613":
                self.final.append(selector[i])
        self.final.sort(key=lambda x: x["bigpowernetin"], reverse=True)

    def selectBigpowernetup(self):
        selector = self.final
        self.final = []
        for i in range(len(selector)):
            twodayinfo = self.db.tctimeinfo.find({"name": selector[i]["name"], "time": {"$lt": self.today}}).sort("time", pymongo.DESCENDING).limit(2).skip(0)
            info = []
            for j in twodayinfo:
                info.append(j)
            bigpowernetinup = (info[0]["bigpowernetin"] - info[1]["bigpowernetin"]) / info[1]["bigpowernetin"]
            selector[i]["bigpowernetup"] = bigpowernetinup
            self.final.append(selector[i])
        self.final.sort(key=lambda x: x["bigpowernetup"], reverse=True)

    def selectBigpowernetdayup(self):
        selector = self.final
        self.final = []
        for i in range(len(selector)):
            twodayinfo = self.db.tctimeinfo.find({"name": selector[i]["name"], "time": {"$lt": self.today}}).sort("time", pymongo.DESCENDING).limit(3).skip(0)
            info = []
            for j in twodayinfo:
                info.append(j)
            bigpowernetinup = (info[0]["bigpowernetin"] - info[1]["bigpowernetin"]) / info[1]["bigpowernetin"]
            bigpowernetinup += (info[1]["bigpowernetin"] - info[2]["bigpowernetin"]) / info[2]["bigpowernetin"]
            selector[i]["bigpowernetup"] = bigpowernetinup
            self.final.append(selector[i])
        self.final.sort(key=lambda x: x["bigpowernetup"], reverse=True)

    def selectDisstribution(self):
        selector = self.final
        self.final = []
        for i in range(len(selector)):
            percent = int((selector[i]["historypricelist"][2] - selector[i]["historypricelist"][0]) / (selector[i]["historypricelist"][1] - selector[i]["historypricelist"][0]) * 100 + 1)
            crypercent = sum(selector[i]["disstributionlist"][percent:])
            print selector[i]["name"], crypercent

    def funtioncontry(self):
        self.moveStop()
        # self.moveCirculationmarketvalue()
        # self.selectPE()
        # self.selectRetailnetin()
        # self.selectTurnoverrate()
        # self.selectAmplitudepc()
        # self.selectIncreasepc()
        # self.selectBigpowernetin()
        # self.selectFourdaysnetout()
        # self.selectBaolao()
        # self.selectBigpowernetup()
        # self.selectRetailnetindown()
        self.selectDisstribution()

    def showfinal(self):
        self.funtioncontry()
        selector = self.final
        final = []
        for i in range(len(selector)):
            final.append((selector[i]["name"]))
            print selector[i]["name"], selector[i]["bigpowernetin"], selector[i]["retailnetin"]
            # print selector[i]["name"], selector[i]["retailnetin"]
        buylist = ["600221", "002697", "600776", "000878", "002135", "000848", "000876", "000333", "002157", "600115"]
        for i in buylist:
            if i not in final:
                print "sale, " + i
        return final

    def test(self):#测试函数
        self.funtioncontry()
        selector = self.final
        self.final = []
        shouyi = 0
        final = []
        for i in range(len(selector)):
            try:
                self.final.append(selector[i])
                for i in self.final:
                    nextday = self.db.tctimeinfo.find({"name": i["name"], "time": self.today}).sort("time").limit(1)
                for x in nextday:
                    shouyi += x["increasepc"]
                    final.append((x["name"], x["increasepc"]))
            except IndexError:
                pass
        try:
            final.append(shouyi / len(self.final))
        except ZeroDivisionError:
            pass
        return final

# testday = ['2016-05-15', '2016-05-13', '2016-05-12', '2016-05-11', '2016-05-10', '2016-05-09', '2016-05-06', '2016-05-05', '2016-05-04', '2016-05-03', '2016-04-29']
# zongshouyi = 0
# for i in testday:
#     a = StockSelector(i)
#     a = a.test()
#     a.append(i)
#     try:
#         zongshouyi += a[-2]
#         print a
#     except IndexError:
#         zongshouyi += 0
# print zongshouyi, zongshouyi / len(testday)

# a = StockSelector('2016-05-13')
# a = a.showfinal()
# print a