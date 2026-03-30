import time
from time import sleep
import urllib.parse
from collections import defaultdict

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import Keys
from selenium.webdriver.chrome.options import Options

import xlsxwriter


class Parser:
    def __init__(self):
        self.driver: WebDriver | None = None

    def get_driver(self, headless):
        """Настройка Chrome WebDriver."""
        chrome_options = Options()

        # Основные настройки
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        # User-Agent (маскируемся под реальный браузер)
        chrome_options.add_argument(
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

        if headless:
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--window-size=1920,1080')

        # Создаем драйвер
        driver = webdriver.Chrome(
            options=chrome_options
        )

        # Дополнительная маскировка
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        self.driver = driver

    def card_parser(self, query, retry=3) -> list[WebElement]:
        encoded_query = urllib.parse.quote(query)

        self.driver.get(f'https://www.wildberries.ru/catalog/0/search.aspx?search={encoded_query}')
        wait = WebDriverWait(self.driver, 15)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'product-card__link')))
        print(self.driver.get_cookies())

        global_start_time = time.perf_counter()
        sleep(1)
        heigth = self.driver.execute_script("return document.body.scrollHeight")
        c_try = 1
        test_c = 0

        print('Скролл страницы...')
        while True:
            test_c += 1

            card_div = self.driver.find_element(By.CLASS_NAME, 'product-card-list')
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'end'});", card_div)
            time.sleep(0.2)

            new_h = self.driver.execute_script("return document.body.scrollHeight")

            if test_c == 1:
                cards = self.driver.find_elements(By.CLASS_NAME, 'product-card__link')
                break

            if new_h == heigth:
                if c_try == retry:
                    cards = self.driver.find_elements(By.CLASS_NAME, 'product-card__link')
                    break
                else:
                    c_try += 1
                    self.driver.execute_script("window.scrollTo(0, 0);")

            heigth = new_h

        if cards: print(len(cards))
        duration = time.perf_counter() - global_start_time
        print('скролл страницы длился {}м {:.2f}c'.format(int(duration // 60), duration % 60))
        return cards

    def _parse_article(self, html: str) -> str:
        start = time.perf_counter()
        soup = BeautifulSoup(html, 'html.parser')
        article_elem = soup.find(class_='cellValue--hHBJB')

        if article_elem:
            span_elem = article_elem.find('span')
            if span_elem:
                print('нашел артикль за', time.perf_counter() - start)
                return span_elem.text
            else:
                return 'None'
        else:
            return 'None'

    def _parse_title(self, html: str) -> str:
        soup = BeautifulSoup(html, 'html.parser')
        title_elem = soup.find(class_='productTitle--lfc4o')
        return title_elem.get_text(strip=True) if title_elem else None


    def get_card_html(self, card_url) -> str:
        start = time.perf_counter()
        result = {}
        self.driver.set_window_size(1500, 1080)
        print(card_url)
        self.driver.get(card_url)
        wait = WebDriverWait(self.driver, 15)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'sellerWrap--U2QVn')))
        sleep(1)

        sizes_elem = self.driver.find_element(By.CLASS_NAME, 'sizesWrap--X6cGL')
        more_button = sizes_elem.find_elements(By.CLASS_NAME, 'sizesListItemMore--ywCYB')
        if more_button:
            more_button.pop().click()
            sleep(.3)
        print('загрузил html за ', time.perf_counter() - start)
        print(self._parse_article(self.driver.page_source))

        return self.driver.page_source

    def run(self):
        self.get_driver(False)
        cards = self.card_parser('пальто из натуральной шерсти')
        urls = [card.get_attribute('href') for card in cards]
        for url in urls:
            html = self.get_card_html(url)



class XLSXFormatter:
    def __init__(self):
        self.document = xlsxwriter.Workbook('../text.xlsx')
        self.sheet = self.document.add_worksheet()

    def __write_header(self, headers):
        for i, header in enumerate(headers):
            self.sheet.write(0, i, header)

    def __formate_specification(self, value: dict):
        spec_contet = ''
        for k, v in value.items():
            spec_contet += k + '\n'
            specs = [': '.join(s) for s in v]
            spec_contet += '\n'.join(specs) + '\n\n'

        return spec_contet

    def generate_file(self, data: list[dict]):
        headers = [
            'ссылка на товар', 'артикул', "название", "цена", "описание", "ссылки на изображения",
            "характеристики", "продавец", "ссылка на продавца", "размеры", "рейтинг", "кол-во отзывов"
        ]
        self.__write_header(headers)

        for i, item in enumerate(data, start=1):
            for j, k in enumerate(item):
                val = item[k]

                if k == 'specifications':
                    spec_content = self.__formate_specification(val)
                    self.sheet.write_string(i, j, spec_content)
                else:
                    self.sheet.write_string(i, j, val)

        self.document.close()


c = Parser()
c.get_driver(True)
c.run()
