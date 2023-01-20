from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time

def url_crawling(url:str, n:int) -> None:
    """
    url에서 n 개(40의 배수로 끊김) 만큼의 product_url을 받아서 파일에 저장함.
    """
    n = n//40 - 1
    
    driver = webdriver.Chrome()

    # kream 나이키 product url 크롤링
    driver.get(url)


    category_list  = []

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
    for cnt in range(n):
        for i in range(9):
            try:
                body.send_keys(Keys.PAGE_DOWN)  
            except:
                continue
        time.sleep(3)

    elements = driver.find_elements(By.CLASS_NAME, 'item_inner')	#class 속성으로 접근
    for elem in elements:
        products.append(elem.get_attribute('href'))
        
    
    time.sleep(1)

    print(len(products))

    f = open('crawling\\url_crawling\\products.txt', 'a')
    f.write(' '.join(products))
    f.close()

    print("end")