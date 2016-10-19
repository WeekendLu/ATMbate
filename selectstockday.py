# -*- coding:utf-8 -*-

import pymongo
import time


class StockSelector(object):
    def __init__(self, testday):
        tdb = pymongo.MongoClient()
        self.db = tdb.stock
        self.today = int(time.mktime(time.strptime(testday, "%Y-%m-%d")))
        # self.today = time.time()
        info = self.db.info.find({"time": {"$lt": self.today}}).sort("time", pymongo.DESCENDING).limit(2932)
        self.allinfo = []
        for i in info:
            self.allinfo.append(i)
        self.final = []

        self.marketvaluesmall = 0  #最小流值,默认20
        self.marketvaluebig = 999999  #最大流值,默认90
        self.cirlation = 0  #流值/市值,默认0.88
        self.pemin = 0  #最小市盈率,默认0
        self.pemax = 999999  #最大市盈率,默认999
        self.turnoverretemin = 1  #换手率最小,默认5
        self.turnoverretemax = 6  #换手率最大,默认20
        self.amplitudepcsmall = 3  #振幅下限,默认5
        self.amplitudepcbig = 20  #振幅上限,默认20
        self.increasemin = -11
        self.increasemax = 11  #涨幅,默认11
        self.volcountday = 30  #交易量统计天数,默认30
        self.volamplitude = 1.2  #不超过最低交易量的几倍,默认1.2
        self.vollastamplitude = 0.98  #大于前一天交易量的几倍,默认0。98
        self.hisincreasecountday = 7
        self.hisincreasedaymax = 7
        self.pricecountday = 7  #股价统计天数,默认7
        self.priceincreasesmall = -0.8  #上面天数+1合计最低涨幅,默认-0.006
        self.priceincreasebig = 8  #上面天数+1合计最高涨幅,默认0.05
        self.pricecontrol = 1000  #股价上限控制,默认1000
        self.showcount = 1 #统计几只入围股票,默认3
        self.holdday = 2  #持有天数
        self.skipday = 0  #跳过天数
        self.bomeng = 100000 * 0.01  #博萌比例

    def funtioncontry(self):
        self.moveStop()
        self.pe()
        self.moveCirculationmarketvalue()
        self.turnoverrate()
        self.amplitudepc()
        self.increasepc()
        self.vol()
        self.hisincrease()
        self.currentprice()
        self.countfinanwerght()

    def moveStop(self):  #停牌筛选
        selector = self.allinfo
        self.final = []
        for i in xrange(len(selector)):
            if selector[i]["vol"] != 0:
                if selector[i]["name"] != "002256":
                # if selector[i]["name"][0] != "3":
                    selector[i]["weight"] = []
                    self.final.append(selector[i])

    def moveCirculationmarketvalue(self): #筛选流值
        selector = self.final
        self.final = []
        for i in xrange(len(selector)):
            try:
                if self.marketvaluesmall <= selector[i]["circulationmarketvalue"] <= self.marketvaluebig:
                    if 1 > selector[i]["circulationmarketvalue"] / selector[i]["marketvalue"] >= self.cirlation:
                        self.final.append(selector[i])
            except:
                pass

    def pe(self):#筛选市盈率
        selector = self.final
        self.final = []
        for i in range(len(selector)):
            try:
                if self.pemin <= selector[i]["peratio"] <= self.pemax:
                    self.final.append(selector[i])
            except:
                print selector[i]["name"], "pass"

    def turnoverrate(self):#筛选换手率
        selector = self.final
        self.final = []
        for i in range(len(selector)):
            if self.turnoverretemin <= selector[i]["turnoverrate"] <= self.turnoverretemax:
                self.final.append(selector[i])

    def amplitudepc(self):#筛选振幅
        selector = self.final
        self.final = []
        for i in range(len(selector)):
            if self.amplitudepcsmall <= selector[i]["amplitudepc"] <= self.amplitudepcbig:
                selector[i]["weight"].append(selector[i]["amplitudepc"])
                selector[i]["weight"].append(selector[i]["increase"])
                self.final.append(selector[i])

    def increasepc(self):#筛选涨幅
        selector = self.final
        self.final = []
        for i in range(len(selector)):
            if self.increasemin <= selector[i]["increasepc"] < self.increasemax and selector[i]["currentprice"] < selector[i]["opening"]:
                self.final.append(selector[i])

    def vol(self):#交易量
        selector = self.final
        self.final = []
        for i in xrange(len(selector)):
            hisinfo = self.db.info.find({"name": selector[i]["name"], "time": {"$lt": self.today}}).sort("time", pymongo.DESCENDING).skip(1).limit(self.volcountday)
            vollist = []
            try:
                for j in hisinfo:
                    vollist.append(j["vol"])
                if selector[i]["vol"] < min(vollist) * self.volamplitude and selector[i]["vol"] > vollist[0] * self.vollastamplitude:
                    # selector[i]["weight"].append(selector[i]["vol"]/vollist[0])
                    self.final.append(selector[i])
            except:
                pass

    def hisincrease(self):
        selector = self.final
        self.final = []
        for i in xrange(len(selector)):
            hisinfo = self.db.info.find({"name": selector[i]["name"], "time": {"$lt": self.today}}).sort("time", pymongo.DESCENDING).limit(self.hisincreasecountday)
            hisincreaseday = 0
            try:
                for j in hisinfo:
                    if j["increasepc"] >= 0:
                        hisincreaseday += 1
                if hisincreaseday <= self.hisincreasedaymax:
                    self.final.append(selector[i])
            except:
                pass

    def currentprice(self):#股价
        selector = self.final
        self.final = []
        for i in xrange(len(selector)):
            hisinfo = self.db.info.find({"name": selector[i]["name"], "time": {"$lt": self.today}}).sort("time", pymongo.DESCENDING).skip(1).limit(self.pricecountday)
            pricelist = []
            highlist = []
            lowlist = []
            try:
                for j in hisinfo:
                    if j["currentprice"] != 0:
                        pricelist.append(j["currentprice"])
                        highlist.append(j["highest"])
                        lowlist.append(j["lowest"])
                if selector[i]["currentprice"] > min(lowlist) and self.priceincreasesmall * 0.01 <= (selector[i]["currentprice"] - min(pricelist)) / min(pricelist) <= self.priceincreasebig * 0.01 and selector[i]["currentprice"] <= self.pricecontrol:
                    # selector[i]["weight"].append((selector[i]["currentprice"] - min(pricelist)) / min(pricelist))
                    self.final.append(selector[i])
            except:
                pass

    def countfinanwerght(self):#算权重分
        selector = self.final
        self.final = []
        for i in range(len(selector)):
            try:
                selector[i]["finalweight"] = sum(selector[i]["weight"])
                self.final.append(selector[i])
            except:
                pass
        self.final.sort(key=lambda x: x["finalweight"], reverse=True)
        selector = self.final
        self.final = []
        print len(selector)
        if len(selector) <= self.showcount:
            for i in range(len(selector)):
                self.final.append(selector[i])
                print selector[i]["name"], selector[i]["weight"], selector[i]["finalweight"], 7700 / len(selector) / selector[i]["currentprice"]
        else:
            for i in range(self.showcount):
                self.final.append(selector[i])
                print selector[i]["name"], selector[i]["weight"], selector[i]["finalweight"], 7700 / self.showcount / selector[i]["currentprice"]

    def showfinal(self):
        self.funtioncontry()
        selector = self.final
        final = []
        for i in range(len(selector)):
            final.append(selector[i]["name"])
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
                    nextday = self.db.info.find({"name": i["name"], "time": {"$gte": self.today}}).sort("time").limit(self.holdday).skip(self.skipday)
                asd = []
                for y in nextday:
                    asd.append(y)
                try:
                    if asd[0]["vol"] == 0 or asd[self.holdday - 1]["vol"] == 0 or asd[self.holdday - 2]["vol"] == 0 or asd[self.holdday - 3]["vol"] == 0 or asd[self.holdday - 4]["vol"] == 0 or asd[0]["vol"] == 0:
                        print asd[0]["name"] + " cant buy"
                    else:
                        bomeng = self.bomeng + 1
                        holddayindex = self.holdday - 1
                        if (asd[holddayindex]["opening"] - asd[holddayindex]["yesterdayclose"]) / asd[holddayindex]["yesterdayclose"] < 0.098:
                            if asd[holddayindex]["opening"] * bomeng <= asd[holddayindex]["highest"]:
                                shouyi += (((asd[holddayindex]["opening"] * bomeng - asd[0]["opening"]) / asd[0]["opening"]) * 100 - 0.5) / self.holdday
                                final.append((asd[0]["name"], round((asd[holddayindex]["opening"] * bomeng - asd[0]["opening"]) / asd[0]["opening"] * 100 - 0.5, 3)))
                            else:
                                shouyi += (((asd[holddayindex]["currentprice"] - asd[0]["opening"]) / asd[0]["opening"]) * 100 - 0.5) / self.holdday
                                final.append((asd[0]["name"], "BF", round((asd[holddayindex]["currentprice"] - asd[0]["opening"]) / asd[0]["opening"] * 100 - 0.5, 3)))

                        else:
                            shouyi += (((asd[holddayindex]["opening"] - asd[0]["opening"]) / asd[0]["opening"]) * 100 - 0.5) / self.holdday
                            final.append((asd[0]["name"], "nobomeng", round(asd[holddayindex]["opening"] - asd[0]["opening"]) / asd[0]["opening"] * 100 - 0.5, 3))

                except:
                    print asd[0]["name"] + " pass"
            except IndexError:
                pass
        try:
            final.append(shouyi / len(final))
        except ZeroDivisionError:
            pass
        return final

tdb = pymongo.MongoClient()
db = tdb.stock
testinfo = db.info.find({"name": "000002"}).sort("time", pymongo.DESCENDING).limit(96).skip(0)
testday = []
for i in testinfo:
    testday.append(time.strftime('%Y-%m-%d', time.localtime(i["time"])))
testday.sort()
zongshouyi = 1
for i in testday:
    a = StockSelector(i)
    a = a.test()
    a.append(i)
    try:
        zongshouyi = round(zongshouyi + (zongshouyi * a[-2] * 0.01), 3)
        print a
    except IndexError:
        zongshouyi += 0
print zongshouyi, len(testday), round((zongshouyi - 1) / len(testday) * 100, 3)
