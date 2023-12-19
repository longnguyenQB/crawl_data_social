from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import requests
from urllib.request import urlopen
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import urllib.request
from threading import Thread
from itertools import islice

def chunk(arr_range, arr_size):
    arr_range = iter(arr_range)
    return iter(lambda: tuple(islice(arr_range, arr_size)), ())


def download_img( driver, by_locator, path, index, type):
    try:
        url = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located(by_locator)).get_attribute("src")
        # url = self.driver.find_element(By.XPATH, by_locator).get_attribute("src")
        # urllib.request.urlretrieve(url, path)
        
        img_data = requests.get(url).content
        with open(path + f'/{index}_{type}.jpg', 'wb') as handler:
            handler.write(img_data)
    except:
        pass


def multi_tiktok(i):
    options = Options()
    options.add_argument("start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])

    driver = webdriver.Chrome(options=options)
    # Change the tiktok link
    driver.get("https://www.tiktok.com/@papayaho.cat")
    download_img(driver=driver, by_locator=(By.XPATH, '//img[@id="captcha-verify-image"]'), path="D:/Project/Test selenium/img", index = i, type = "captcha_verify_image")
    download_img(driver=driver, by_locator=(By.XPATH, '//img[@class="captcha_verify_img_slide react-draggable sc-VigVT ggNWOG"]'), path="D:/Project/Test selenium/img", index = i, type = "captcha_verify_img_slide")


sessions = list(chunk(arr_range=range(112,300),
                                                arr_size=5))

print(sessions)

for index_session in range(len(sessions)):
    threads = []
    for i in sessions[index_session]:
        threads.append(Thread(target=multi_tiktok, args=(i,)))
    for thread in threads:
        if not thread.is_alive():
            thread.start()
    for thread in threads:
        thread.join()