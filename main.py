from selenium import webdriver
from time import sleep
from selenium.webdriver.chrome.options import Options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
#for Ubuntu driver = webdriver.Chrome('/usr/bin/chromedriver',chrome_options=chrome_options)

driver = webdriver.Chrome(chrome_options=chrome_options)
driver.get("https://brickseek.com/deals/")
driver.implicitly_wait(3)
filter = driver.find_element_by_xpath("//select[@id='banner-sort']/option[@value='newest']").click()

# https://brickseek.com/deals/?sort=newest&pg=59

# get number of pages
number_pages = int(driver.find_element_by_class_name('total').text)
print(number_pages)

for page in range(1,number_pages+1):
    driver.get(f'https://brickseek.com/deals/?sort=newest&pg={page}')
    sleep(2)
    # scrape page
    deals = driver.find_elements_by_class_name('item-list__item')
    for deal in deals:
        title = deal.find_element_by_class_name('item-list__title')
        print(title.text)

driver.close()