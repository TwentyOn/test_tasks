import asyncio
import random
import traceback
import urllib.parse
from urllib.parse import urlparse
from time import sleep, perf_counter
import logging

import aiohttp
import requests

from xlsx_formatter import XLSXFormatter
from get_cookie import get_cookie_string


logging.basicConfig(level=logging.INFO, format='[{asctime}] #{levelname:4} {name}:{lineno} - {message}', style='{')
logger = logging.getLogger(__name__)


class CardParser:
    """
    Парсер для извелчения детальной информации по каждой карточке товара
    """

    def __init__(self):
        self.api_url_form = 'https://basket-{:02d}.wbbasket.ru/vol{}/part{}/{}/info/ru/card.json'
        self.headers = {
            'refer': 'https://www.wildberries.ru/catalog/874597327/detail.aspx?size=1317986564',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'sec-ch-ua': 'Not(A:Brand";v="8", "Chromium";v="144", "YaBrowser";v="26.3", "Yowser";v="2.5',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': "Windows"
        }

    async def card_parse(self, article_id) -> dict:
        result = {}
        bucket_id, card_json = await self.get_card_json(article_id)

        description = card_json.get('description', 'описание не указано')

        options = card_json.get('options', [])
        specifications = map(lambda op_item: (op_item['name'], op_item['value']), options)
        specifications = map(lambda op_item: ': '.join(op_item), specifications)
        specifications = '\n'.join(specifications) if specifications else 'характеристики не найдены'

        image_count = card_json.get('media', dict()).get('photo_count', 0)
        image_links = self.get_image_links(bucket_id, article_id, image_count)

        result['description'] = description
        result['image_links'] = image_links
        result['specifications'] = specifications

        return result

    async def get_card_json(self, article_id, retry=3):
        vol = article_id // 100000
        part = article_id // 1000

        possible_urls = [self.api_url_form.format(buck_id, vol, part, article_id) for buck_id in range(1, 44)]
        bucket_id, card_json = await self.find_media_url(possible_urls)

        return bucket_id, card_json

    async def find_media_url(self, urls):
        async with aiohttp.ClientSession() as session:
            semaphore = asyncio.Semaphore(10)

            async def check_url(url, bucket_ind) -> None | tuple[int, dict]:
                async with semaphore:
                    try:
                        async with session.get(url, headers=self.headers, timeout=5) as resp:
                            if resp.status == 200:
                                content = await resp.json()
                                return bucket_ind, content
                            return None
                    except Exception as err:
                        print(traceback.format_exc())
                        print(url)
                        return None

            tasks = []
            for ind, url in enumerate(urls, start=1):
                task = asyncio.create_task(check_url(url, ind))
                tasks.append(task)

            for coro in asyncio.as_completed(tasks):
                result = await coro
                if result:
                    # Отмена остальных задач
                    for task in tasks:
                        task.cancel()
                    return result
            print('не удалось найти карту', urls)
            return None, dict()

    @staticmethod
    def get_image_links(bucket_id, article_id, count):
        if not bucket_id:
            return 'не удалось извлечь ссылки'

        url_form = 'https://basket-{:02d}.wbbasket.ru/vol{}/part{}/{}/images/big/{}.webp'
        vol = article_id // 100000
        part = article_id // 1000
        result = []
        for i in range(1, count + 1):
            result.append(url_form.format(bucket_id, vol, part, article_id, i))

        return ', '.join(result)


class CatalogParser:
    """Парсер каталога товаров по телу поискового запроса"""

    def __init__(self, card_parser: CardParser):
        self.card_parser = card_parser
        self.api_url_form = 'https://www.wildberries.ru/__internal/u-search/exactmatch/ru/common/v18/search?ab_testing=false&appType=1&curr=rub&dest=123585581&hide_vflags=4294967296&lang=ru&page={}&query={}&resultset=catalog&sort=popular&spp=30&suppressSpellcheck=false'
        self.api_headers = {
            'authority': 'www.wildberries.ru',
            'method': 'GET',
            'scheme': 'https',
            'accept': '*/*',
            'accept-encoding': 'json',
            'accept-language': 'ru,en;q=0.9',
            'deviceid': 'site_aa794f41ab3441ed8c0f2471f2d477cd',
            'priority': 'u=1, i',
            'referer': 'https://www.wildberries.ru/catalog/0/search.aspx?search=%D0%BF%D0%B0%D0%BB%D1%8C%D1%82%D0%BE%20%D0%B8%D0%B7%20%D0%BD%D0%B0%D1%82%D1%83%D1%80%D0%B0%D0%BB%D1%8C%D0%BD%D0%BE%D0%B9%20%D1%88%D0%B5%D1%80%D1%81%D1%82%D0%B8',
            'sec-ch-ua': '"Not(A:Brand";v="8", "Chromium";v="144", "YaBrowser";v="26.3", "Yowser";v="2.5"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 YaBrowser/26.3.0.0 Safari/537.36,',
            'x-queryid': 'qid88197475177428503120260328064413',
            'x-requested-with': 'XMLHttpRequest',
            'x-spa-version': '14.3.2',
            'x-userid': '0'
        }

        self.empty_item_placeholder = 'не найдено'

    async def parse_catalog(self, query, page=1):
        parsed_data = []
        encoded_query = urllib.parse.quote(query)

        cookie_url = urlparse(self.api_url_form)
        cookie_url = cookie_url._replace(path='', query='')
        cookie = get_cookie_string(cookie_url.geturl())
        self.api_headers['cookie'] = cookie
        self.api_headers[
            'path'] = '/__internal/u-search/exactmatch/ru/common/v18/search?ab_testing=false&appType=1&curr=rub&dest=-1257786&hide_vflags=4294967296&inheritFilters=false&lang=ru&query={}&resultset=catalog&sort=popular&spp=30&suppressSpellcheck=false'.format(
            encoded_query)
        self.api_headers['referer'] = 'https://www.wildberries.ru/catalog/0/search.aspx?search={}'.format(encoded_query)

        logger.info('парсинг каталога...')
        while True:
            page_url = self.api_url_form.format(page, encoded_query)
            response = requests.get(page_url, headers=self.api_headers)
            products = response.json()
            times = []
            for i, item in enumerate(products['products']):
                start_time = perf_counter()
                item_data = {}

                article_id = item['id']
                print('https://www.wildberries.ru/catalog/{}/detail.aspx'.format(article_id), i + 1)
                name = item.get('name', 'нет имени')
                quantity = item.get('totalQuantity', self.empty_item_placeholder)
                price = self.__get_price(item)
                sizes = self.__get_sizes(item)
                seller_name = item.get('supplier', self.empty_item_placeholder)
                seller_link = self.__get_seller_link(item)
                rating = item.get('nmReviewRating', self.empty_item_placeholder)
                rating_count = item.get('feedbacks', self.empty_item_placeholder)

                card_data = await self.card_parser.card_parse(article_id)

                item_data['card_link'] = 'https://www.wildberries.ru/catalog/{}/detail.aspx'.format(article_id)
                item_data['article'] = article_id
                item_data['name'] = name
                item_data['price'] = price
                item_data.update(card_data)
                item_data['seller_name'] = seller_name
                item_data['seller_link'] = seller_link
                item_data['sizes'] = sizes
                item_data['quantity'] = quantity
                item_data['rating'] = rating
                item_data['rating_count'] = rating_count

                parsed_data.append(item_data)
                print('время: {:.2f}с'.format(perf_counter() - start_time))
                times.append(perf_counter() - start_time)

            page += 1
            print('среднее время на элемент: {}с'.format(sum(times) / len(times)))
            print(
                'прогресс: {}/{} ({:.2f}%)'.format(len(parsed_data), products['total'],
                                                   len(parsed_data) / products['total'] * 100))

            if len(parsed_data) == 100:
                return parsed_data

            sleep(random.uniform(0.5, 2.0))

    def __get_price(self, catalog_item):
        price = catalog_item.get('sizes')
        price = price[0] if price else dict()
        price = price.get('price', dict())
        price = price.get('product')
        price = price // 100 if price else self.empty_item_placeholder

        return price

    def __get_sizes(self, catalog_item):
        sizes = catalog_item.get('sizes', dict(name=self.empty_item_placeholder))
        sizes = ', '.join(size_item['name'] for size_item in sizes)

        return sizes

    def __get_seller_link(self, catalog_item):
        link_form = 'https://www.wildberries.ru/seller/{}'
        seller_id = catalog_item.get('supplierId')

        if seller_id:
            return link_form.format(seller_id)

        return self.empty_item_placeholder


def get_image_links(bucket_id, article_id, count):
    url_form = 'https://basket-{:02d}.wbbasket.ru/vol{}/part{}/{}/images/big/{}.webp'
    vol = article_id // 100000
    part = article_id // 1000
    result = []
    for i in range(1, count + 1):
        result.append(url_form.format(bucket_id, vol, part, article_id, i))

    return ', '.join(result)


async def main(query):
    card_parser = CardParser()
    xlsx_fmt = XLSXFormatter()

    pars = CatalogParser(card_parser)
    data = await pars.parse_catalog(query)

    xlsx_fmt.generate_file(data, 'aboba')


if __name__ == '__main__':
    start = perf_counter()
    try:
        asyncio.run(main('пальто из натуральной шерсти'))
    except Exception as err:
        print(traceback.format_exc())
    finally:
        end = perf_counter() - start
        print('парсинг данных завершился за {:.0f}м {:.2f}с'.format(end // 60, end % 60))
