import json
import urllib.request
from bs4 import BeautifulSoup
import csv
import time
import numpy as np
import pandas as pd
#import chromedriver_binary # nopa
from selenium import webdriver
from io import StringIO
import boto3
import s3fs
from fake_useragent import UserAgent
import subprocess
import shutil
import os

BUCKET_NAME = 'realmadridsite'
BUCKETNAME = 'realmadridsite'
FILENAME = "news.csv"
KEYNAME = "news.csv"

BIN_DIR = "/tmp/bin"
CURR_BIN_DIR = os.getcwd() + "/bin"

def _init_bin(executable_name):
    start = time.clock()
    if not os.path.exists(BIN_DIR):
        print("Creating bin folder")
        os.makedirs(BIN_DIR)
    print("Copying binaries for " + executable_name + " in /tmp/bin")
    currfile = os.path.join(CURR_BIN_DIR, executable_name)
    newfile = os.path.join(BIN_DIR, executable_name)
    shutil.copy2(currfile, newfile)
    print("Giving new binaries permissions for lambda")
    os.chmod(newfile, 0o775)
    elapsed = time.clock() - start
    print(executable_name + " ready in " + str(elapsed) + "s.")

print('Loading function')

def lambda_handler(event, context):
    _init_bin("headless-chromium")
    _init_bin("chromedriver")
    csv_list = [] 

    #file = "./news.csv"
    #f = open(file, 'w',encoding='utf_8_sig')
    #writer = csv.writer(f, lineterminator='\n')
    
    #def get_yahoo_news():
        # ヘッドラインニュースのタイトル格納用リスト
        #news_data = []
    
        # urlの指定
    url = 'https://follow.yahoo.co.jp/themes/051839da5a7baa353480'
    
    #browser = webdriver.Chrome(executable_path='./chromedriver.exe')
    options = webdriver.ChromeOptions()
    #options.binary_location = "/tmp/bin/headless-chromium"だとエラーとなる
    options.binary_location = "/tmp/bin/headless-chromium"
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--single-process")
    options.add_argument('--disable-dev-shm-usage')
 
    driver = webdriver.Chrome(
        #executable_path="./bin/chromedriver",
        #executable_path="./tmp/bin/chromedriver"だとエラーとなる
        executable_path="/tmp/bin/chromedriver",
        chrome_options=options
    )
    
    # ページにアクセス
    
    driver.get(url)
    
    driver.find_element_by_css_selector('#wrapper > section.content > a').click()
    
    time.sleep(3)
    
    driver.find_element_by_css_selector('#wrapper > section.content > a').click()
    
    time.sleep(3)
    
    driver.find_element_by_css_selector('#wrapper > section.content > a').click()
    
    time.sleep(3)
    
    driver.find_element_by_css_selector('#wrapper > section.content > a').click()
    
    time.sleep(3)
    
    #htmlの取得
    #html = urllib.request.urlopen(url)
    html = driver.page_source.encode('utf-8')
    
    # htmlパース
    soup = BeautifulSoup(html, "html.parser")
    
    #links = soup.find_all("a")
    
    #for a in links:
        #href = a.attrs['href']
        #text = a.text
        #print(text, href) 
    
    li_list = soup.select('#wrapper > section.content > ul > li:nth-child(n) > a.detailBody__wrap > div.detailBody__cnt > p.detailBody__ttl')
    print(li_list)
    for li in li_list:
        print("li: ", li.string)
        csv_list.append(li.string)
       
        
    
    #csv_list.append('/n')
    links = soup.select('#wrapper > section.content > ul > li:nth-child(n) > a.detailBody__wrap')
    
    for link in links:
        print('link:',link.get('href'))
        csv_list.append(link.get('href'))
        
        
        #for t in range(21):
            #for i in soup.find_all('#wrapper > section.content > ul > li:nth-child('+str(t)+') > a.detailBody__wrap'):
                #news_data.append(i)
        #wrapper > section.content > ul > li:nth-child(1) > a.detailBody__wrap > div.detailBody__cnt > p.detailBody__ttl
    
    
    #if __name__ == '__main__':
        #main()
    print(csv_list)
    #csv_list = np.array(csv_list).reshape(2,int((len(csv_list)/2))
    
    csv_list = np.array(csv_list).reshape(2,100)
    
    #csv_list = pickle.dumps(csv_list)
    #csv_list = json.dumps(csv_list)
    #csv_list = csv_list.decode()
    csv_list = pd.DataFrame(csv_list)
    print(type(csv_list))
    
    def write_df_to_s3(csv_list):
   
        csv_buffer = StringIO()
        csv_list.to_csv(csv_buffer,index=False,encoding='utf-8-sig')
        s3_resource = boto3.resource('s3')
        s3_resource.Object('realmadridsite','news.csv').put(Body=csv_buffer.getvalue())

    write_df_to_s3(csv_list)
   
    #def write_df_to_s3(csv_list):
   
        #csv_buffer = StringIO()
        #df.to_csv(csv_buffer,index=False,encoding='utf-8-sig')
        #s3_resource = boto3.resource('s3')
        #s3_resource.Object('BUCKETNAME','KEYNAME').put(Body=csv_buffer.getvalue())
   

    
   # s3 = boto3.resource('s3')

    #bucket = s3.Bucket(BUCKET_NAME)

    #FILE_CONTENTS = csv_list

    #ret = bucket.put_object( 
        #ACL='private', 
        #Body=FILE_CONTENTS,
        #Key=FILENAME
        #ContentType='text/csv'
    #)

    #return ret
    #print(csv_list)
    #writer.writerows(csv_list)
        # ファイル破損防止のために閉じますs
    #f.close()
