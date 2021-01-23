from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import requests, time, random, sys, os
from db_init import Mongo
sys.path.insert(0,'../../../../COMTRIS_AI/src')
from preprocessor import RegexPreprocessor

db = Mongo()
RP = RegexPreprocessor()

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(os.environ['COMTRIS_CHROME_DRIVER_PATH'], chrome_options=chrome_options)

#다나와 구매후기 페이지로 이동
driver.get('http://pc26.danawa.com/bbs/?controller=boardReview&methods=reviewList')
db_result = db.cursor()['master_config'].find_one({'key':'selenium_cnt'})
cnt = db_result['value']

while True:
    time.sleep(random.randrange(3,6))
    try:
        driver.find_element_by_xpath('//*[@id="contents_pc26"]/div/div[4]/div[%s]/a' %cnt).send_keys(Keys.CONTROL + '\n') #구매후기 클릭, 새 창으로 띄워서 클릭
    except:
        target = driver.find_element_by_xpath('//*[@id="danawa_warp"]/div[4]/div[2]/button') #다음에 읽을 구매후기가 로딩되지 않았다면 스크롤 버튼 클릭
        driver.execute_script('arguments[0].click();', target)
        continue

    time.sleep(5)
    driver.switch_to.window(driver.window_handles[1]) #새 탭으로 이동

    html = driver.page_source
    soup = BeautifulSoup(html,"html.parser")

    list_ = soup.find("tbody").findAll("tr")

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
    db.cursor()['master_config'].update_one({'key':'selenium_cnt'},{'$set':{'value':cnt}})

    if 'CPU' in document and 'M/B' in document and 'VGA' in document and 'RAM' in document and 'SSD' in document and 'POWER' in document:
        document['original']=original
        db.cursor()['pc_selenium'].insert_one(document)
        #print(document) #DB에 넣는걸로 수정
        #print(cnt)