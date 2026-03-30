import time
from time import sleep
import urllib.parse
from collections import defaultdict

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
        self.driver: WebDriver|None = None

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

    def _parse_article(self) -> str:
        article_elem = self.driver.find_element(By.CLASS_NAME, 'cellValue--hHBJB')
        article_elem = article_elem.find_element(By.TAG_NAME, 'span')
        return article_elem.text

    def _parse_title(self) -> str:
        title_elem = self.driver.find_element(By.CLASS_NAME, 'productTitle--lfc4o')
        return title_elem.text

    def _parse_price(self) -> str:
        try:
            price_elem = self.driver.find_element(By.CLASS_NAME, 'priceBlockFinalPrice--iToZR')
            return price_elem.text
        except:
            return 'Нет в наличии'

    def _parse_seller_info(self) -> tuple[str, str | None]:
        try:
            seller_elem = self.driver.find_element(By.CSS_SELECTOR, '.sellerInfoButtonLink--RoLBz')
            seller_name = seller_elem.find_element(By.CLASS_NAME, 'sellerInfoNameDefaultText--qLwgq').text
            seller_link = seller_elem.get_attribute('href')
            return seller_name, seller_link
        except:
            seller_elem = self.driver.find_element(By.CLASS_NAME, 'sellerInfoDefaultNameText--FNDfM')
            return seller_elem.text, 'нет ссылки'

    def _parse_rating_info(self) -> list[str]:
        rating = self.driver.find_element(By.CSS_SELECTOR, 'span[class*="productReviewRating"]')
        r = rating.text.split(' · ')
        if len(r) == 2:
            return r
        else:
            return rating.text.split()

    def _parse_description_view(self) -> tuple[str, defaultdict[str, list[tuple]]]:
        specifications = defaultdict(list)

        description_btn = self.driver.find_element(By.CSS_SELECTOR, '.btnDetail--im7UR')
        description_btn.click()
        try:
            description_section = self.driver.find_element(By.ID, 'section-description')
            description_txt = '\n'.join(item.text for item in description_section.find_elements(By.TAG_NAME, 'p'))
        except:
            description_txt = 'нет описания'

        spec_section_elem = self.driver.find_element(By.CSS_SELECTOR,
                                                     'section[data-testid="product_additional_information"]')
        spec_tables = spec_section_elem.find_elements(By.TAG_NAME, 'table')

        for table in spec_tables:
            header = table.find_element(By.TAG_NAME, 'caption').text
            rows = table.find_elements(By.TAG_NAME, 'tr')
            for row in rows:
                key = row.find_element(By.CSS_SELECTOR, 'th > span > span').text
                value = row.find_element(By.CSS_SELECTOR, 'td > div').text
                specifications[header].append((key, value))
        # description_close_btn = self.driver.find_element(By.CLASS_NAME, 'popup__close')
        # description_close_btn.click()

        return description_txt, specifications

    def _parse_images_view(self) -> str:
        images_div = self.driver.find_element(By.CSS_SELECTOR, 'div[class*="miniaturesSwiper"]')
        images_elems = images_div.find_elements(By.TAG_NAME, 'img')
        image_src = [img.get_attribute('src') for img in images_elems]
        return ', '.join(image_src)

    def _parse_media_view(self) -> str:
        media_elem = self.driver.find_element(By.CLASS_NAME, 'mediaSlider--k1JWH')
        media_elem.click()
        images_div = self.driver.find_element(By.CLASS_NAME, 'miniaturesWrapper--Yw0YN')
        images_src = [img.get_attribute('src') for img in images_div.find_elements(By.TAG_NAME, 'img')]
        return ', '.join(images_src)

    def _parse_sizes_info(self) -> str:
        sizes_elem = self.driver.find_element(By.CLASS_NAME, 'sizesWrap--X6cGL')

        more_button = sizes_elem.find_elements(By.CLASS_NAME, 'sizesListItemMore--ywCYB')
        if more_button:
            more_button.pop().click()
            sleep(.3)

        sizes = sizes_elem.find_elements(By.CLASS_NAME, 'sizesListItem--QcbQx')
        sizes = [item.find_element(By.CSS_SELECTOR, 'button > span').text for item in sizes]
        sizes = ', '.join(sizes)
        return sizes

    def parse_card(self, card_url):
        result = {}
        print(card_url)
        self.driver.get(card_url)
        wait = WebDriverWait(self.driver, 15)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'sellerWrap--U2QVn')))
        sleep(1)
        print(self.driver.requests)

        article = self._parse_article()
        title = self._parse_title()
        price = self._parse_price()
        seller_name, seller_link = self._parse_seller_info()
        rating, review_cnt = self._parse_rating_info()
        sizes = self._parse_sizes_info()
        description, specifications = self._parse_description_view()
        # image_links = self._parse_media_view()
        image_links = self._parse_images_view()

        result['link'] = card_url
        result['article'] = article
        result['title'] = title
        result['price'] = price
        result['description'] = description
        result['image_links'] = image_links
        result['specifications'] = specifications
        result['seller_name'] = seller_name
        result['seller_link'] = seller_link
        result['sizes'] = sizes
        result['rating'] = rating
        result['reviews_cnt'] = review_cnt

        return result

    def run(self):
        self.get_driver(True)
        cards = self.card_parser('пальто из натуральной шерсти')
        cards = [card.get_attribute('href') for card in cards]
        cards_cnt = len(cards)

        data = []
        self.driver.set_window_size(1500, 1080)
        print('Парсинг {} карточек...'.format(cards_cnt))
        start_time = time.perf_counter()
        for ind, url in enumerate(cards, start=1):
            data.append(self.parse_card(url))
            if not ind % 10:
                print('обработано {} карточек из {} ({:.2f} %)'.format(ind, cards_cnt, ind / cards_cnt * 100))
        duration = time.perf_counter() - start_time
        print('Парсинг завершен за {}м {:.2f}c'.format(int(duration // 60), duration % 60))
        file = XLSXFormatter()
        file.generate_file(data)


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
