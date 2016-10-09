# -*- coding:utf-8 -*-

import time
import getbidprice
import selectstockday#时用
# from scrapy import cmdline
#
# cmdline.execute('/Users/weekendlu/SpiderProject/tcstock/scrapy crawl tcstock'.split())

# testday = '2016-07-03'
now = int(time.time() / 1000) * 1000 + 77000
testday = time.strftime('%Y-%m-%d', time.localtime(now))
goodstock = selectstockday.StockSelector(testday)
goodstock = goodstock.showfinal()
finallist = []
for i in range(len(goodstock)):
    goodprice = getbidprice.Strategy(goodstock[i], testday)
    goodprice = goodprice.getbidprice()
    finallist.append(goodprice)
for i in finallist:
    print i
