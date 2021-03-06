from brandmapping import id_to_brand
from selenium import webdriver
import time
from selenium.webdriver.chrome.options import Options
import atexit
from pymongo import MongoClient
from bs4 import BeautifulSoup
import requests
import datetime


class Item:
    def __init__(self, name, current_price, previous_price, store_brand, image_url):
        self.name = name
        self.current_price = current_price
        self.previous_price = previous_price
        self.store_brand = store_brand
        self.image_url = image_url
        self.discount = round((1 - current_price / previous_price) * 100)
        self.date = datetime.datetime.utcnow()

    def to_document(self):
        return dict(
            name=self.name,
            current_price=self.current_price,
            previous_price=self.previous_price,
            store_brand=self.store_brand,
            image_url=self.image_url,
            discount=self.discount,
            date=self.date
        )


def exit_handler(driver):
    print('closed ')
    driver.close()


def insert_to_database(items):
    client = MongoClient('localhost', 27017)
    db = client['brickseek_test']
    deals = db.deals
    for item in items:
        deals.update_one({"name": item.name}, {"$set": item.to_document()}, upsert=True)


def main_selenium():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    # for Ubuntu
    # driver = webdriver.Chrome('/usr/bin/chromedriver',chrome_options=chrome_options)

    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.get("https://brickseek.com/deals/?sort=newest")
    driver.implicitly_wait(3)
    # filter = driver.find_element_by_xpath("//select[@id='banner-sort']/option[@value='newest']").click()

    # atexit.register(exit_handler,driver)

    # get number of pages
    number_pages = int(driver.find_element_by_class_name('total').text)
    print(number_pages)
    items = []

    for page in range(1, number_pages + 1):
        print(page)
        driver.get(f'https://brickseek.com/deals/?sort=newest&pg={page}')
        time.sleep(2)
        # scrape page
        deals = driver.find_elements_by_class_name('item-list__item')
        for deal in deals:
            # get title
            title = deal.find_element_by_class_name('item-list__title').text
            # get current price
            current_dollar = deal.find_elements_by_class_name('price-formatted__dollars')[0].text
            current_dollar = int(current_dollar.replace(',', ''))

            current_cents = float(deal.find_elements_by_class_name('price-formatted__cents')[0].text)
            current_price = current_dollar + current_cents / 100
            # get previous price
            previous_dollar = deal.find_elements_by_class_name('price-formatted__dollars')[1].text
            previous_dollar = int(previous_dollar.replace(',', ''))

            previous_cents = float(deal.find_elements_by_class_name('price-formatted__cents')[1].text)
            previous_price = previous_dollar + previous_cents / 100

            # get store brand
            id = deal.find_element_by_class_name('item-list__store').get_attribute('data-store-type')
            store_brand = id_to_brand[id] if id in id_to_brand else 'none'

            # image url
            image_url = deal.find_element_by_class_name('item-list__image-container') \
                .find_element_by_tag_name('img').get_attribute('src')

            # format_data = f'{title} {current_price} {previous_price} {store_brand} {image_url}'
            # print(format_data)

            item = Item(title, current_price, previous_price, store_brand, image_url)
            items.append(item)

    insert_to_database(items)
    exit_handler(driver)


def main():
    page_link = 'https://brickseek.com/deals/?sort=newest'
    page_response = requests.get(page_link, timeout=5)
    page_content = BeautifulSoup(page_response.content, "html.parser")
    number_pages = int(page_content.find(class_='total').text)
    items = []

    for page in range(1, number_pages + 1):
        print(page)

        page_link = f'https://brickseek.com/deals/?sort=newest&pg={page}'
        page_response = requests.get(page_link, timeout=5)
        page_content = BeautifulSoup(page_response.content, "html.parser")
        time.sleep(2)
        deals = page_content.find_all(class_='item-list__item')
        for deal in deals:
            # get title
            title = deal.find(class_='item-list__title').text
            # get current price
            current_dollar = deal.find_all(class_='price-formatted__dollars')[0].text
            current_dollar = int(current_dollar.replace(',', ''))
            current_cents = float(deal.find_all(class_='price-formatted__cents')[0].text)
            current_price = current_dollar + current_cents / 100

            # get previous price
            previous_dollar = deal.find_all(class_='price-formatted__dollars')[1].text
            previous_dollar = int(previous_dollar.replace(',', ''))

            previous_cents = float(deal.find_all(class_='price-formatted__cents')[1].text)
            previous_price = previous_dollar + previous_cents / 100

            # get store brand
            id = deal.find(class_='item-list__store')['data-store-type']
            store_brand = id_to_brand[id] if id in id_to_brand else 'none'

            # image url
            image_url = deal.find(class_='item-list__image-container') \
                .find('img')['src']

            # format_data = f'{title} {current_price} {previous_price} {store_brand} {image_url}'
            # print(format_data)

            item = Item(title, current_price, previous_price, store_brand, image_url)
            items.append(item)

    insert_to_database(items)


if __name__ == "__main__":
    start = time.time()
    main()
    end = time.time()
    print('Completed in:', end - start)
