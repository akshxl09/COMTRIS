from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import requests, time, sys, os, datetime
import numpy as np
from db_init import Mongo
sys.path.insert(0,'../../../../COMTRIS_AI/src')
from preprocessor import RegexPreprocessor

def selenium_crawler(url, category):
    db = Mongo()
    RP = RegexPreprocessor()

    chrome_options = webdriver.ChromeOptions()
    #chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(os.environ['COMTRIS_CHROME_DRIVER_PATH'], chrome_options=chrome_options)

    #다나와 구매후기 페이지로 이동
    driver.get(url)
    time.sleep(np.random.randint(5,7))
    
    if category == "구매후기":
        db_result = db.cursor()['master_config'].find_one({'key':'review_cnt'})
    elif category == "조립갤러리":
        db_result = db.cursor()['master_config'].find_one({'key':'gallery_cnt'})    
    cnt = db_result['value']


    while True:
        try:
            driver.find_element_by_xpath('//*[@id="contents_pc26"]/div/div[4]/div[%s]/a' %cnt).send_keys(Keys.CONTROL + '\n') #구매후기 클릭, 새 창으로 띄워서 클릭
        except:
            target = driver.find_element_by_xpath('//*[@id="danawa_warp"]/div[4]/div[2]/button') #다음에 읽을 구매후기가 로딩되지 않았다면 스크롤 버튼 클릭
            driver.execute_script('arguments[0].click();', target)
            continue

        recent_time = datetime.datetime.now()
        db.cursor()['master_config'].update_one({'key':'recent_time'}, {'$set':{'value':recent_time }})

        time.sleep(np.random.randint(5,7))
        driver.switch_to.window(driver.window_handles[1]) #새 탭으로 이동

        html = driver.page_source
        soup = BeautifulSoup(html,"html.parser")

        list_ = soup.find("div", attrs={'class':'detail_spec'}).find("tbody").findAll("tr")
        shop_date = soup.find("div",attrs={'class':'ds_info'}).find('span')

        document={}
        original={}

        for j in list_:
            name = j.find("th")
            value = j.find("a")
            if name.text =='CPU':
                cpu = RP.cpu(value.text)
                if cpu:
                    document['CPU']=cpu
                    original['CPU']=value.text
                else:
                    break
            elif name.text =='메인보드':
                mb = RP.mb(value.text)
                if mb:
                    document['M/B']=mb
                    original['M/B']=value.text
                else:
                    break
            elif name.text =='그래픽카드':
                vga = RP.vga(value.text)
                if vga:
                    document['VGA']=vga
                    original['VGA']=value.text
                else:
                    break
            elif name.text =='메모리':
                ram = RP.ram(value.text)
                if ram:
                    document['RAM']=ram
                    original['RAM']=value.text
                else:
                    break
            elif name.text =='SSD':
                ssd = RP.ssd(value.text)
                if ssd:
                    document['SSD']=ssd
                    original['SSD']=value.text
                else:
                    break
            elif name.text =='파워':
                power = RP.power(value.text)
                if power:
                    document['POWER']=power
                    original['POWER']=value.text
                else:
                    break

        driver.close() #현재 탭 종료
        driver.switch_to.window(driver.window_handles[0]) #부모 탭으로 이동

        cnt+=1
        if category == "구매후기":
            db.cursor()['master_config'].update_one({'key':'review_cnt'},{'$set':{'value':cnt}})
        elif category == "조립갤러리":
            db.cursor()['master_config'].update_one({'key':'gallery_cnt'},{'$set':{'value':cnt}})

        if 'CPU' in document and 'M/B' in document and 'VGA' in document and 'RAM' in document and 'SSD' in document and 'POWER' in document:
            tmp = shop_date.text[:-1].replace('.','-')
            document['shop_date'] = datetime.datetime.strptime(tmp, '%Y-%m-%d' ) #구매날짜 넣어주기
            document['crawl_date'] = datetime.datetime.now() #크롤링한 시간 넣어주기
            document['original']=original
            if category == "구매후기":
                db.cursor()['review'].insert_one(document)
            elif category == "조립갤러리":
                db.cursor()['gallery'].insert_one(document)

        