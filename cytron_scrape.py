from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pandas as pd

# inital URL
url = "https://www.cytron.io/index.php?route=product/search&search=all&search=all&sort=p.number_sales&order=DESC"

# webdriver setup
options = Options()
options.headless = True
browser = webdriver.Firefox(executable_path = '/usr/bin/geckodriver', options = options)
browser.get(url)

name = []
price = []
page_num = 1
attempts = 5

while True:
    timeout = 30

    try:
        name_present = EC.presence_of_all_elements_located((By.CLASS_NAME, "name"))
        WebDriverWait(browser, timeout).until(name_present)
        name_raw = browser.find_elements_by_class_name("name")
    except TimeoutException:
        print("====== TimeoutException ======")
        continue

    try:
        price_present = EC.presence_of_all_elements_located((By.CLASS_NAME, "price"))
        WebDriverWait(browser, timeout).until(price_present)
        price_raw = browser.find_elements_by_class_name("price")
    except TimeoutException:
        print("====== TimeoutException ======")
        continue

    print(f">>>>>> Page {page_num} loaded")

    for i in range(attempts):
        try:
            name_raw = browser.find_elements_by_class_name("name")
            price_raw = browser.find_elements_by_class_name("price")
            for i in range(0, len(name_raw)):
                name.append(name_raw[i].text)
                price.append(price_raw[i].text)
            break
        except StaleElementReferenceException as stale:
            print(stale)

    assert(len(name_raw) == len(price_raw))
    print(f"================ Page {page_num} extracted =================")

    try:
        next_present = EC.presence_of_element_located((By.LINK_TEXT, ">"))
        WebDriverWait(browser, timeout).until(next_present)
        browser.find_element_by_link_text(">").click()
    except TimeoutException:
        print(f"###### Element not found, scrape complete after {page_num} pages ######")
        break
    except StaleElementReferenceException:
        next_present = EC.presence_of_element_located((By.LINK_TEXT, ">"))
        WebDriverWait(browser, timeout).until(next_present)
        browser.find_element_by_link_text(">").click()

    print(">>>>>> Loading next page")

    page_num += 1

browser.close()

name_price = {'Item':name, 'Price':price}
data_frame = pd.DataFrame(name_price, columns=['Item', 'Price'])
data_frame.to_csv('cytron_io.csv')
