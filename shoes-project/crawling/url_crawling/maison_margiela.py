from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time

driver = webdriver.Chrome()

# kream 나이키 product url 크롤링
driver.get("https://kream.co.kr/brands/maison%20margiela/")


time.sleep(0.5)
# 카테고리 필터 클릭
driver.find_element(By.XPATH, '//*[@id="__layout"]/div/div[2]/div/div[2]/div[2]/div[1]/div[2]').click()
# 신발 필터 클릭
driver.find_element(By.XPATH, '//*[@id="__layout"]/div/div[2]/div/div[2]/div[2]/div[1]/div[2]/div[2]/ul/li[1]/a').click()
time.sleep(0.5)
# 성별 필터 클릭
driver.find_element(By.XPATH, '//*[@id="__layout"]/div/div[2]/div/div[2]/div[2]/div[1]/div[4]').click()
time.sleep(0.5)
# 남성필터 클릭
driver.find_element(By.XPATH, '//*[@id="__layout"]/div/div[2]/div/div[2]/div[2]/div[1]/div[4]/div[2]/ul/li[1]').click()
time.sleep(0.5)


products = []


body = driver.find_element(By.CSS_SELECTOR ,'body')

# pagedown을 통해서 창을 내리고 새로운 신발이 뜨게함
# test로 10번 반복함 
for cnt in range(10):
    for i in range(9):
        body.send_keys(Keys.PAGE_DOWN)  
    time.sleep(3)

elements = driver.find_elements(By.CLASS_NAME, 'item_inner')	#class 속성으로 접근
for elem in elements:
    products.append(elem.get_attribute('href'))

time.sleep(3)

