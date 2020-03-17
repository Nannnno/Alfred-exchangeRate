# -*- coding: utf-8 -*-
import sys
import sqlite3
import urllib,urllib2
import json
import time, datetime
from workflow import Workflow3, ICON_WEB, web

reload(sys)
sys.setdefaultencoding('utf8')

# Debit currency  扣款币种
# Trading currencies  交易币种
# ICON_DEFAULT = 'icon.png'

#连接数据库 创建表
def connSqlite():
    try:
        conn = sqlite3.connect('exchange.db')
        cu = conn.cursor()

        # create_tb_cmd='''
        # CREATE TABLE rate
        # (
        # baseCurrency TEXT,
        # transactionCurrency TEXT,
        # exchangeRate REAL,
        # updatetime TEXT,
        # );
        # '''

        cu.execute('create table exchange (baseCurrency TEXT, transactionCurrency TEXT, exchangeRate REAL, updatetime TEXT)')
        conn.commit()
        cu.close()
        conn.close()
    except:  
        cu.close()
        conn.commit()
        conn.close()
        #print "Create table failed"  
        title = '连接数据库失败了~'
        subtitle = 'sqlite3哦'
        return False

# 插入汇率数据
def insertRate(updateTime, baseCurrency, transactionCurrency, exchangeRate):
    try:
        conn = sqlite3.connect('exchange.db')
        cursor = conn.cursor()

        sql = '''
        INSERT INTO exchange (baseCurrency, transactionCurrency, updateTime, exchangeRate) VALUES (?,?,?,?)
        '''
        cursor.execute(sql,(baseCurrency, transactionCurrency, updateTime, exchangeRate))

        conn.commit()
        cursor.close()
        conn.close()
        return True
    except:
        cursor.close()
        conn.commit()
        conn.close()
        #print "insert false"
        title = '插入数据库失败了~'
        subtitle = '不知道为啥...'
        return False

# 从数据库获取汇率
def getRate(baseCurrency, transactionCurrency):
    try:
        conn = sqlite3.connect('exchange.db')
        conn.row_factory = dict_factory
        cu = conn.cursor()
        cu.execute('select * from exchange where baseCurrency=? AND transactionCurrency=?', (baseCurrency,transactionCurrency))
        res = cu.fetchone()
        cu.close()
        conn.close()
        return res
    except:
        cu.close()
        conn.commit()
        conn.close()
        title = '获取数据库数据失败了~'
        subtitle = '不知道为啥..'
        #print "get rate false"
        return False

# 更新汇率数据
def updateRate(updateTime,baseCurrency,transactionCurrency,exchangeRate):
    conn = sqlite3.connect('exchange.db')
    cursor = conn.cursor()
    try:        
        cursor.execute('UPDATE exchange SET exchangeRate = ?,updateTime = ? WHERE baseCurrency = ? AND transactionCurrency = ?',(exchangeRate ,updateTime, baseCurrency, transactionCurrency))
        cursor.close()
        conn.commit()
        conn.close()
        return True
    except:
        try:
            cursor.execute('insert into exchange (baseCurrency, transactionCurrency, updateTime, exchangeRate) values ('+baseCurrency+','+transactionCurrency+','+updateTime+','+exchangeRate+')')
            cursor.close()
            conn.commit()
            conn.close()
            return True
        except:
            cursor.close()
            conn.commit()
            conn.close()
            #print "update rate false"
            title = '更新数据库汇率失败囖~'
            subtitle = '不知道为啥'
            return False

# 数据库数据取出格式转换工厂方法
def dict_factory(cursor, row):  
    d = {}  
    for idx, col in enumerate(cursor.description):  
        d[col[0]] = row[idx]  
    return d  

# 从api获取汇率
def getRateApi(dc,tc,getRateTime):
    try:

        parameters = {'curDate':getRateTime,'baseCurrency':dc,'transactionCurrency':tc}
        # url = 'http://www.unionpayintl.com/cardholderServ/serviceCenter/rate/search'
        url = 'http://www.unionpayintl.com/cardholderServ/serviceCenter/rate/search'
        # post获取数据
        req_header = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
        'Accept':'text/html;q=0.9,*/*;q=0.8',
        'Accept-Charset':'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding':'gzip',
        'Connection':'close',
        'Referer':None #注意如果依然不能抓取的话，这里可以设置抓取网站的host
        }
        data = urllib.urlencode(parameters)
        request = urllib2.Request(url, data, req_header)
        response = urllib2.urlopen(request)
        page = response.read()
        res = json.loads(page)
        res['updateDate'] = time.localtime(res['updateDate'] / 1000)
        res['updateDate'] = time.strftime('%Y-%m-%d',res['updateDate'])
        return res
        #获取的数据格式如下
        #{u'updateUser': 55, u'transactionCurrencyOption': None, u'effectiveDate': 1523348652000, u'exchangeRate': 6.3178, u'createDate': 1523289600000, u'transactionCurrency': u'USD', u'curDate': 1523289600000, u'createUser': 55, u'exchangeRateId': 1012292, u'baseCurrency': u'CNY', u'updateDate': 1523289600000}
    except:
        title = '获取api失败了~'
        subtitle = '不知道为啥...'
        return False

def getYesterday(): 
    isWorkDay = datetime.datetime.now().weekday()
    if isWorkDay == 0:
        today=datetime.date.today()
        oneday=datetime.timedelta(days=3)
        yesterday=today-oneday
        return yesterday
    else:
        today=datetime.date.today()
        oneday=datetime.timedelta(days=1)
        yesterday=today-oneday
        return yesterday

def main(wf):
    connSqlite()
    title = 'hl 金额 扣款币种 交易币种'
    subtitle = '有点慢...😘'

    # 获取 金额 币种
    query = wf.args[0].strip().replace("\\", "")
    inputData = query.split();

    # 今天的日期年月日
    updateTime = datetime.datetime.now().strftime('%Y-%m-%d')
    # 现在的时分秒
    nowtime = datetime.datetime.now().strftime('%H:%M:%S')

    if nowtime > '17:35:00':
        getRateTime = updateTime
    else:
        getRateTime = getYesterday()
    #print(getRateTime)
    try:

        # 币种缩写大写
        dc = inputData[1].upper()
        tc = inputData[2].upper()
        dcMoney = inputData[0]
        

        values = getRate(dc,tc)

        if values:
            # 判断数据库里的数据是否需要更新(5点35网站数据应该更新了)
            if updateTime > values['updatetime']:
                rate = getRateApi(dc,tc,getRateTime)
                
                updateRate(rate['updateDate'], rate['baseCurrency'], rate['transactionCurrency'], rate['exchangeRate'])

                values = getRate(dc,tc)
                # 交易货币金额换算
                tcMoney = float(dcMoney) * (float(1) / values['exchangeRate'])

                wf.add_item(
                    title= str(tcMoney) + ' ' + values['transactionCurrency'],
                    subtitle= '1 ' + values['baseCurrency'] + ' to ' + str(1/values['exchangeRate']) + ' ' + values['transactionCurrency'],
                    arg=tcMoney,
                    valid=True,
                    #icon=ICON_DEFAULT
                )

                wf.send_feedback()

            else:
                # 交易货币金额换算
                tcMoney = float(dcMoney) * (float(1) / values['exchangeRate'])

                wf.add_item(
                    title= str(tcMoney) + ' ' + values['transactionCurrency'],
                    subtitle= '1 ' + values['baseCurrency'] + ' to ' + str(1/values['exchangeRate']) + ' ' + values['transactionCurrency'],
                    arg=tcMoney,
                    valid=True,
                    #icon=ICON_DEFAULT
                )

                wf.send_feedback()

        else:
            rate = getRateApi(dc,tc,getRateTime)
            insertRate(rate['updateDate'], rate['baseCurrency'], rate['transactionCurrency'], rate['exchangeRate'])

            tcMoney = float(dcMoney) * (float(1) / rate['exchangeRate'])
            
            wf.add_item(
                title= str(tcMoney) + ' ' + rate['transactionCurrency'],
                subtitle= '1 ' + rate['baseCurrency'] + ' to ' + str( 1 / rate['exchangeRate']) + ' ' + rate['transactionCurrency'],
                arg=tcMoney,
                valid=True,
                #icon=ICON_DEFAULT
            )

            wf.send_feedback()

    except:
        wf.add_item(
            title= title,
            subtitle= subtitle + 'last',
            arg=0,
            valid=True, 
            icon="icon.png"
        )
        wf.send_feedback()


if __name__ == '__main__':
    wf = Workflow3()
    sys.exit(wf.run(main))