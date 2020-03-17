# -*- coding: utf-8 -*-
import sys
import urllib2
from bs4 import BeautifulSoup
from workflow import Workflow3, ICON_WEB, web

reload(sys)
sys.setdefaultencoding('utf8')

def scrapeDC(html):
    soup = BeautifulSoup(html,"lxml") 
    res = soup.select('#baseCurrency')
    return res

def scrapeTC(html):
    soup = BeautifulSoup(html,"lxml") 
    res = soup.select('#transactionCurrency')

    return res

def main(wf):
    query = wf.args[0].strip().replace("\\", "")
    inputData = query.split();

    try:
        #html = urllib2.urlopen('http://www.unionpayintl.com/cardholderServ/serviceCenter/rate?language=cn').read()

        url = r'http://www.unionpayintl.com/cardholderServ/serviceCenter/rate?language=cn'
        headers = {"User-Agent":"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Mobile Safari/537.36"}
        request = urllib2.Request(url,headers=headers)#Request参数有三个，url,data,headers,如果没有data参数，那就这样的写法
        html = urllib2.urlopen(request).read()

        if inputData[0] == 'dc':
            data = scrapeDC(html)

        if inputData[0] == 'tc':
            data = scrapeTC(html)

        for i in data:
            try:
                tmpData = i.text.split(',')

                wf.add_item(
                    title= tmpData[0],
                    subtitle= tmpData[1],
                    arg=tmpData[0],
                    valid=True, 
                    icon="icon.png"
                )
            except:
                tmpData = i.text

                wf.add_item(
                    title = tmpData,
                    subtitle = "(づ￣ 3￣)づ😘",
                    arg=0,
                    valid=True, 
                    icon="icon.png"
                )

    except Exception as e:
        print(e)
        wf.add_item(
            title = 'hlist dc/tc (扣款币种/交易币种)',
            subtitle = "(づ￣ 3￣)づ😘",
            arg=0,
            valid=True, 
            icon="icon.png"
        )

        
    
    wf.send_feedback()


if __name__ == '__main__':
    wf = Workflow3()
    sys.exit(wf.run(main))
