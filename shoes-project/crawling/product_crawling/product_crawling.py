# 1. products.txt 파일에서 product url을 list 형태로 얻는다.
# 2. for문을 이용해서 list를 순환하면서 셀레니움을 이용해서 각 product url로 접근한다.
# 3. csv 형태로 crawling_data에 데이터를 저장한다.
# 3-1. 이미지, 이름, 발매가, 최근 시세(최근 10번의 가격 평균) 데이터를 받는다.
# 3-2. 이미지를 resizing 한다.
# 3-3. 이미지 색상 군집화를 통해서 가장 많이 분포된 색 두가지를 데이터에 추가한다.
# 3-4. resized 이미지를 흑백처리 한다.
# 3-4. 크기조정/흑백 img, name, og_price, resell_price, color1, color2 를 crawling_data에 추가한다. 
import numpy as np
import cv2
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import urllib.request
import csv

products = []

columns = ["product_id", "img_path","brand", "name", "color1", "color2", "price_og", "price_resell"]

with open('crawling\product_crawling\product_data.csv', 'w',newline='') as f: 
      
    # using csv.writer method from CSV package 
    write = csv.writer(f)
    write.writerow(columns)


driver = webdriver.Chrome()

#######
email = ""
password = ""
#######
login_url = "https://kream.co.kr/login"

driver.get(login_url)

# 이메일 작성
driver.find_element(By.XPATH, '//*[@id="wrap"]/div[2]/div[1]/div/div[1]/div/input').send_keys(email)
time.sleep(0.5)
# 비밀번호 작성
driver.find_element(By.XPATH, '//*[@id="wrap"]/div[2]/div[1]/div/div[2]/div/input').send_keys(password)
time.sleep(0.5)
# 로그인 클릭
driver.find_element(By.XPATH, '//*[@id="wrap"]/div[2]/div[1]/div/div[3]/a').click()

time.sleep(2)
'''
'''
with open('crawling\\url_crawling\\products.txt', 'r') as file:    
    line = None    # 변수 line을 None으로 초기화
    while line != '':
        line = file.readline().split(" ")
        print(line)
        for product_url in line:
            print("product", product_url)
            driver.get(product_url)

            # 신발의 번호를 product_id 변수에 저장함.
            product_id = product_url[-5:]

            # 이미지 받아서 변수에 저장 | XPATH 사용
            try:
                img = driver.find_element(By.XPATH, '//*[@id="wrap"]/div[2]/div[1]/div/div[1]/div[2]/div[1]/div/div/div/div[1]/div/div/div/div/div/picture/img')
                img_url = img.get_attribute('src')
                # print("이미지 url:\n",img_url)
            # 신발사진이 하나인 경우는 위 XPATH와 달라서 오류가 남.
            # 그래서 try except 문으로 해결함.
            except:
                img = driver.find_element(By.XPATH, '//*[@id="wrap"]/div[2]/div[1]/div/div[1]/div[2]/div[1]/div/div/div/picture/img')
                img_url = img.get_attribute('src')
                # print("이미지 url:\n",img_url)
                

            # 이미지 전처리
            # 사이즈 줄이기 + 흑백으로 만들기.
            # channel 한개로 군집화를 진행할 것이다.
            # 색상 정보는 따로 저장할 것이다.
            resp = urllib.request.urlopen(img_url)
            image = np.asarray(bytearray(resp.read()), dtype='uint8')
            image = cv2.imdecode(image, cv2.IMREAD_COLOR)
            image = cv2.resize(image, (256,256), interpolation=cv2.INTER_AREA)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


            # 전처리된 이미지 이미지 폴더에 저장
            img_path = 'crawling\\product_crawling\\image\\' + product_id + ".jpg"
            cv2.imwrite(img_path, image)


            # 이름 변수 받기 | XPATH 사용
            brand = driver.find_element(By.XPATH, '//*[@id="__layout"]/div/div[2]/div[1]/div/div[2]/div/div[1]/div[1]/div/div/a').text
            name = driver.find_element(By.XPATH, '//*[@id="__layout"]/div/div[2]/div[1]/div/div[2]/div/div[1]/div[1]/div/p[2]').text
            # print("브랜드: \n", brand, "\n신발명: \n",name)

            # 색상 변수 받기
            colors = driver.find_element(By.XPATH, '//*[@id="__layout"]/div/div[2]/div[1]/div/div[2]/div/div[2]/div/dl/div[3]/dd').text
            color =  colors.split('/')
            # print("색상: \n", color[:2])

            # 정가 변수 받기 | XPATH 사용
            try:
                price_og = driver.find_element(By.XPATH, '//*[@id="__layout"]/div/div[2]/div[1]/div/div[2]/div/div[2]/div/dl/div[4]/dd').text
                price_og = int(price_og[:-1].replace(",", ""))
            except:
                price_og = driver.find_element(By.XPATH, '//*[@id="__layout"]/div/div[2]/div[1]/div/div[2]/div/div[2]/div/dl/div[4]/dd').text
                price_og = int(price_og.split("약 ")[1].split("원")[0].replace(",",""))
               
            # print("정가: \n" ,price_og)

            # 최근 거래가 받기(로그인 필요함) | XPATH 사용  
            price1 = driver.find_element(By.XPATH,'//*[@id="panel1"]/div/table/tbody/tr[1]/td[2]').text
            price1 = int(price1.split("원")[0].replace(",", ""))

            price2 = driver.find_element(By.XPATH,'//*[@id="panel1"]/div/table/tbody/tr[2]/td[2]').text
            price2 = int(price2.split("원")[0].replace(",", ""))

            price3 = driver.find_element(By.XPATH,'//*[@id="panel1"]/div/table/tbody/tr[3]/td[2]').text
            price3 = int(price3.split("원")[0].replace(",", ""))

            price4 = driver.find_element(By.XPATH,'//*[@id="panel1"]/div/table/tbody/tr[4]/td[2]').text
            price4 = int(price4.split("원")[0].replace(",", ""))

            price5 = driver.find_element(By.XPATH,'//*[@id="panel1"]/div/table/tbody/tr[5]/td[2]').text
            price5 = int(price5.split("원")[0].replace(",", ""))

            prices = np.array([price1,price2,price3,price4,price5])
            AVG = int(np.mean(prices))

            # print("최근 5회 거래 평균가:\n", AVG)


            # columns = ["product_id", "img_path","brand", "name", "color1", "color2", "price_og", "price_resell"]
            with open('crawling\product_crawling\product_data.csv', "a", newline='') as f:
                write = csv.writer(f)

                write.writerow([product_id, img_path, brand,  color[0], color[1], price_og, AVG])

            time.sleep(2)