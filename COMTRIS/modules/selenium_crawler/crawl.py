import sys
sys.path.insert(0,'../../../../COMTRIS_AI/src')
import requests
import time
import os
import datetime
import numpy as np
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from db_init import Mongo
from regex_processor import RegexPreprocessor

def selenium_crawler(url, category):
    db = Mongo()
    RP = RegexPreprocessor()

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(os.environ['COMTRIS_CHROME_DRIVER_PATH'], chrome_options=chrome_options)

    #다나와 구매후기 페이지로 이동
    driver.get(url)
    time.sleep(np.random.randint(3,5))
    
    if category == "구매후기":
        db_result = db.cursor()['master_config'].find_one({'key':'review_cnt'})
    elif category == "조립갤러리":
        db_result = db.cursor()['master_config'].find_one({'key':'gallery_cnt'})    
    cnt = db_result['value'] #읽은 위치 가져오기

    while True:
        try:
            driver.find_element_by_xpath('//*[@id="contents_pc26"]/div/div[4]/div[%s]/a' %cnt).send_keys(Keys.CONTROL + '\n') #구매후기 클릭, 새 창으로 띄워서 클릭
        except:
            target = driver.find_element_by_xpath('//*[@id="danawa_warp"]/div[4]/div[2]/button') #다음에 읽을 구매후기가 로딩되지 않았다면 스크롤 버튼 클릭
            driver.execute_script('arguments[0].click();', target)
            continue

        time.sleep(np.random.randint(3,5))
        driver.switch_to.window(driver.window_handles[1]) #새 탭으로 이동

        cnt+=1
        current_url = driver.current_url
        if category == "구매후기":
            db.cursor()['master_config'].update_one({'key':'review_cnt'},{'$set':{'value':cnt}}) #cnt 갱신
            idx = current_url.find("reviewSeq")+10
            id_result = db.cursor()['review'].find_one({'id':current_url[idx:]})

        elif category == "조립갤러리":
            db.cursor()['master_config'].update_one({'key':'gallery_cnt'},{'$set':{'value':cnt}}) #cnt 갱신
            idx = current_url.find("NumberSeq")+10
            id_result = db.cursor()['gallery'].find_one({'id':current_url[idx:]})
        
        if id_result: #db에 이미 존재하는 값이면
            driver.close() #현재 탭 종료
            driver.switch_to.window(driver.window_handles[0]) #부모 탭으로 이동
            continue

        html = driver.page_source
        soup = BeautifulSoup(html,"html.parser")
        
        try:
            list_ = soup.find("div", attrs={'class':'detail_spec'})
            table = list_.find("tbody").findAll("tr") #테이블 찾기
            shop_date = list_.find("div",attrs={'class':'ds_info'}).find('span') #구매날짜 찾기
        except:
            driver.close() #현재 탭 종료
            driver.switch_to.window(driver.window_handles[0]) #부모 탭으로 이동
            continue



        document={}
        original={}

        flag = 1
        for j in table:
            name = j.find("th")
            value = j.find("a")
            if name.text =='CPU':
                cpu = RP.cpu(value.text)
                original['CPU']=value.text
                document['CPU']=cpu
                if not cpu:
                    flag = 0            
            elif name.text =='메인보드':
                mb = RP.mb(value.text)
                original['M/B']=value.text
                document['M/B']=mb
                if not mb:
                    flag = 0
            elif name.text =='그래픽카드':
                vga = RP.vga(value.text)
                original['VGA']=value.text
                document['VGA']=vga 
                if not vga:
                    flag = 0           
            elif name.text =='메모리':
                ram = RP.ram(value.text)
                original['RAM']=value.text
                document['RAM']=ram
                if not ram:
                    flag = 0            
            elif name.text =='SSD':
                ssd = RP.ssd(value.text)
                original['SSD']=value.text
                document['SSD']=ssd
                if not ssd:
                    flag = 0
            elif name.text =='파워':
                power = RP.power(value.text)
                original['POWER']=value.text
                document['POWER']=power
                if not power:
                    flag = 0


        driver.close() #현재 탭 종료
        driver.switch_to.window(driver.window_handles[0]) #부모 탭으로 이동

        if 'CPU' not in document or 'M/B' not in document or 'VGA' not in document or 'RAM' not in document or 'SSD' not in document or 'POWER' not in document:
            flag = 0

        tmp = shop_date.text[:-1].replace('.','-')
        document['shop_date'] = datetime.datetime.strptime(tmp, '%Y-%m-%d' ) #구매날짜 넣어주기
        document['crawl_date'] = datetime.datetime.now() #크롤링한 시간 넣어주기
        document['original'] = original
        document['pass'] = flag
        document['id'] = current_url[idx:]
        if category == "구매후기":
            db.cursor()['review'].insert_one(document)
        elif category == "조립갤러리":
            db.cursor()['gallery'].insert_one(document)