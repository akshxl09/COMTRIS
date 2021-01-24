import sys
sys.path.insert(0, '../../../../COMTRIS_AI/src')
import requests
import re
import datetime
import os
from pymongo import *
from bs4 import BeautifulSoup
from preprocessor import RegexPreprocessor



header = {
            "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5)\
            AppleWebKit 537.36 (KHTML, like Gecko) Chrome",
            "Accept":"text/html,application/xhtml+xml,application/xml;\
            q=0.9,imgwebp,*/*;q=0.8"
        }
class crawler:
    # 생성자
    def __init__(self, url):
        super(crawler, self).__init__()
        self.url = url
        self.page_num = 1 # 처음 페이지 넘버는 1로 초기화
        self.domain = self.url.split('/')[0] + '//' + self.url.split('/')[2]
        
        driver = requests.get(self.url, verify = False, headers = header)
        html = driver.content.decode('euc-kr', 'replace') # encoding to korean
        # 한글 깨짐 방지, https://blog.naver.com/PostView.nhn?blogId=redtaeung&logNo=221904432971    
        # utf-8이 아닌 euc-kr 변경시 작동 되었다.
        page = BeautifulSoup(html, 'html.parser')
        self.page = page

    
    
    # get page
    def getPage(self): # crawler 객체의 url에 요청
        driver = requests.get(self.url, verify = False, headers = header)
        html = driver.content.decode('euc-kr', 'replace') # encoding to korean
        # 한글 깨짐 방지, https://blog.naver.com/PostView.nhn?blogId=redtaeung&logNo=221904432971    
        # utf-8이 아닌 euc-kr 변경시 작동 되었다.
        page = BeautifulSoup(html, 'html.parser')
        return page
    def getURL(self):
        return self.url
    def getDomain(self):
        return self.domain
    
    

class crawler_danawa(crawler):
    def __init__(self, url):
        super().__init__(url)
    
    def getDate(self, index):
        return self.page.select('.setpc_bbs_tbl>tbody>tr>.date')[index].text
    def getName(self, index):
        return self.page.select('.setpc_bbs_tbl>tbody>tr>.name')[index].text
    def getTitle(self, index):
        return self.page.select('.setpc_bbs_tbl>tbody>tr>.title')[index].text.strip()
    def getAverPrice(self, index):
        return self.page.select('.setpc_bbs_tbl>tbody>tr>.aver_price')[index].text
    def getStatus(self, index):
        return self.page.select('.setpc_bbs_tbl>tbody>tr>.status')[index].text
    def getLink(self, index):
        return self.page.select('.setpc_bbs_tbl>tbody>tr>.title a')[index]['href']
    def getRowsToNumber(self):
        return len(self.page.select('.setpc_bbs_tbl>tbody>tr'))

class crawler_danawa_pc(crawler): # db 관리 포함
    def __init__(self, url):
        super().__init__(url)
        # db
        self.myclient = MongoClient(os.environ["COMTRIS_MONGODB_URI"]) # mongodb의 port의 기본값은 27017, 일단 로컬로
        #self.db_comtris = MongoClient('mongodb://%s:%s@%s' %(MONGO_ID, MONGO_PW, MONGO_HOST)
        self.db = self.myclient['COMTRIS']
        self.col = self.db["pc_quote"]
    # DB methods
    def insert_one(self, document):
        self.col.insert_one(document) # self.col에 삽입

    # 소멸자
    def __del__(self):
        self.myclient.close()

    def getRows(self):
        rows = self.page.select('.tbl_t3>tbody>tr>.tit')
        print("rows = ", rows)
        print("len(rows) = ", len(rows))
    
    def getKey(self):
        self.keys = []
        temp_key = list(map(lambda page:page.text, self.page.select('.tbl_t3>tbody>tr>.srt')))
        for i in temp_key:
            if(i == 'CPU'):
                self.keys.append("CPU")
            elif(i == '메인보드'):
                self.keys.append('M/B')
            elif(i == '메모리'):
                self.keys.append('RAM')
            elif(i == '그래픽카드'):
                self.keys.append('VGA')
            elif(i == 'SSD'):
                self.keys.append('SSD')
            elif(i == '파워'):
                self.keys.append('POWER')
            else :
                self.keys.append(i)
        return self.keys

    def getDict(self, keys, id):
        print("getDict")
        result = {'id':id} # id 추가하여 초기화
        price = {}
        original = {}
        RP = RegexPreprocessor() # 정규식 객체

        for idx, key in enumerate(keys):
            value = self.page.select('.tbl_t3>tbody>tr>.tit')[idx].text
            value = value.strip().split('\n')
            aver_price = self.page.select('.tbl_t3>tbody>tr>.prc')[idx].text
            # print("_id = ", id, "idx = ", idx, "key = ", key, "value = ", value[0], aver_price, "원")

            if key == "CPU":
                cpu = RP.cpu(value[0])# 세이프업 때문에 0으로 함
                if cpu:
                    original["CPU"] = value[0]
                    result["CPU"]=cpu
                    price.update({key : aver_price})
                else : 
                    print("정규식에 맞지 않음-cpu")
                    return 0
            elif key == "M/B":
                mb = RP.mb(value[0])# 세이프업 때문에 0으로 함
                if mb:
                    original["M/b"] = value[0]
                    result["M/B"]=mb
                    price.update({key : aver_price})
                else : 
                    print("정규식에 맞지 않음-mb")
                    return 0
            elif key == "RAM":
                ram = RP.ram(value[0])# 세이프업 때문에 0으로 함
                if ram:
                    original["RAM"] = value[0]
                    result["RAM"]=ram
                    price.update({key : aver_price})
                else : 
                    print("정규식에 맞지 않음-ram")
                    return 0
            elif key == "SSD":
                ssd = RP.ssd(value[0])# 세이프업 때문에 0으로 함
                if ssd:
                    original["SSD"] = value[0]
                    result["SSD"]=ssd
                    price.update({key : aver_price})
                else : 
                    print("정규식에 맞지 않음-ssd")
                    return 0
            elif key == "VGA":
                vga = RP.vga(value[0])# 세이프업 때문에 0으로 함
                if vga:
                    original["VGA"] = value[0]
                    result["VGA"]=vga
                    price.update({key : aver_price})
                else : 
                    print("정규식에 맞지 않음-vga")
                    return 0
            elif key == "POWER":
                power = RP.power(value[0])# 세이프업 때문에 0으로 함
                if power:
                    original["POWER"] = value[0]
                    result["POWER"]=power
                    price.update({key : aver_price})
                else : 
                    print("정규식에 맞지 않음-power")
                    return 0


        # 구매 날짜 긁기 -> date type으로 변경
        shop_date = re.search("\d{4}.\d{2}.\d{2}\s\s\d{2}:\d{2}", self.page.select('.u_info>.date')[0].text).group()
        shop_year = int(shop_date[0:4].strip())
        shop_month = int(shop_date[5:7].strip())
        shop_day = int(shop_date[8:10].strip())
        shop_date = datetime.datetime(shop_year, shop_month, shop_day)
        crawl_date = datetime.datetime.now()
        result.update({'id' : id, 'original':original, 'price' : price, "crawl_date" : crawl_date, 'shop_date' : shop_date})
  
        return result
    def KeysValidation(self, keys):
        flag = True # 문제 없음
        empty_part = []
        for require in ["CPU", "M/B", "RAM", "SSD", "VGA", "POWER"]:
            if require not in keys:
                flag = False # 문제 있음(부품 없음)
                empty_part.append(require)
        return flag
