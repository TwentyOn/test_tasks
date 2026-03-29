import asyncio
import random
import time
import traceback
import urllib.parse
from time import sleep

import aiohttp
import requests
from requests.exceptions import ReadTimeout
from xlsx_formatter import XLSXFormatter

api_url_form = 'https://www.wildberries.ru/__internal/u-search/exactmatch/ru/common/v18/search?ab_testing=false&appType=1&curr=rub&dest=123585581&hide_vflags=4294967296&lang=ru&page={}&query={}&resultset=catalog&sort=popular&spp=30&suppressSpellcheck=false'
api__url_headers = {
    'authority': 'www.wildberries.ru',
    'method': 'GET',
    'path': '/__internal/u-search/exactmatch/ru/common/v18/search?ab_testing=false&appType=1&curr=rub&dest=-1257786&hide_vflags=4294967296&inheritFilters=false&lang=ru&query=%D0%BF%D0%B0%D0%BB%D1%8C%D1%82%D0%BE+%D0%B8%D0%B7+%D0%BD%D0%B0%D1%82%D1%83%D1%80%D0%B0%D0%BB%D1%8C%D0%BD%D0%BE%D0%B9+%D1%88%D0%B5%D1%80%D1%81%D1%82%D0%B8&resultset=catalog&sort=popular&spp=30&suppressSpellcheck=false',
    'scheme': 'https',
    'accept': '*/*',
    'accept-encoding': 'json',
    'accept-language': 'ru,en;q=0.9',
    'cookie': '_wbauid=881974751774285031; x_wbaas_token=1.1000.c4aa4909cd4d4840ae01780704311326.MTV8NDUuODguMjAyLjEyMXxNb3ppbGxhLzUuMCAoV2luZG93cyBOVCAxMC4wOyBXaW42NDsgeDY0KSBBcHBsZVdlYktpdC81MzcuMzYgKEtIVE1MLCBsaWtlIEdlY2tvKSBDaHJvbWUvMTQ0LjAuMC4wIFlhQnJvd3Nlci8yNi4zLjAuMCBTYWZhcmkvNTM3LjM2fDE3NzU3MjM4MDh8cmV1c2FibGV8MnxleUpvWVhOb0lqb2lJbjA9fDB8M3wxNzc1MTE5MDA4fDE=.MEQCIEMHQJpjKj9MGMVNT+HT2udACR2B+OjlrHYA6cfR6F+aAiBWAiGHaRg0nCZParTXemyj6bl4jW4TNRf0WAjq/wo4eQ==; _cp=1; feedbacks_link_accepted=1',
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

    async def get_card_json(self, article_id, retry=3):
        vol = article_id // 100000
        part = article_id // 1000

        possible_urls = [self.api_url_form.format(buck_id, vol, part, article_id) for buck_id in range(1, 44)]
        bucket_id, card_json = await self.find_media_url(possible_urls)

        return bucket_id, card_json

    async def find_media_url(self, urls):
        async with aiohttp.ClientSession() as session:
            semaphore = asyncio.Semaphore(10)

            async def check_url(url, ind):
                async with semaphore:
                    try:
                        async with session.get(url, headers=self.headers, timeout=5) as resp:
                            if resp.status == 200:
                                content = await resp.json()
                                return ind, content
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
            return 'None3', dict()


class CatalogParser:
    """Парсер каталога товаров по телу поискового запроса"""

    def __init__(self, card_parser: CardParser):
        self.card_parser = card_parser
        self.api_url_form = 'https://www.wildberries.ru/__internal/u-search/exactmatch/ru/common/v18/search?ab_testing=false&appType=1&curr=rub&dest=123585581&hide_vflags=4294967296&lang=ru&page={}&query={}&resultset=catalog&sort=popular&spp=30&suppressSpellcheck=false'
        self.api_headers = {
            'authority': 'www.wildberries.ru',
            'method': 'GET',
            'path': '/__internal/u-search/exactmatch/ru/common/v18/search?ab_testing=false&appType=1&curr=rub&dest=-1257786&hide_vflags=4294967296&inheritFilters=false&lang=ru&query=%D0%BF%D0%B0%D0%BB%D1%8C%D1%82%D0%BE+%D0%B8%D0%B7+%D0%BD%D0%B0%D1%82%D1%83%D1%80%D0%B0%D0%BB%D1%8C%D0%BD%D0%BE%D0%B9+%D1%88%D0%B5%D1%80%D1%81%D1%82%D0%B8&resultset=catalog&sort=popular&spp=30&suppressSpellcheck=false',
            'scheme': 'https',
            'accept': '*/*',
            'accept-encoding': 'json',
            'accept-language': 'ru,en;q=0.9',
            'cookie': '_wbauid=881974751774285031; x_wbaas_token=1.1000.c4aa4909cd4d4840ae01780704311326.MTV8NDUuODguMjAyLjEyMXxNb3ppbGxhLzUuMCAoV2luZG93cyBOVCAxMC4wOyBXaW42NDsgeDY0KSBBcHBsZVdlYktpdC81MzcuMzYgKEtIVE1MLCBsaWtlIEdlY2tvKSBDaHJvbWUvMTQ0LjAuMC4wIFlhQnJvd3Nlci8yNi4zLjAuMCBTYWZhcmkvNTM3LjM2fDE3NzU3MjM4MDh8cmV1c2FibGV8MnxleUpvWVhOb0lqb2lJbjA9fDB8M3wxNzc1MTE5MDA4fDE=.MEQCIEMHQJpjKj9MGMVNT+HT2udACR2B+OjlrHYA6cfR6F+aAiBWAiGHaRg0nCZParTXemyj6bl4jW4TNRf0WAjq/wo4eQ==; _cp=1; feedbacks_link_accepted=1',
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

    async def parse_catalog(self, query, page=1):
        parsed_data = []
        encoded_query = urllib.parse.quote(query)

        while True:
            page_url = self.api_url_form.format(page, encoded_query)
            response = requests.get(page_url, headers=self.api_headers)
            products = response.json()

            for i, item in enumerate(products['products']):
                card_parse_start = time.perf_counter()
                item_data = {}
                article_id = item['id']
                print('https://www.wildberries.ru/catalog/{}/detail.aspx'.format(article_id), i + 1)
                name = item.get('name', 'нет имени')

                price = item.get('sizes')
                price = price[0] if price else dict()
                price = price.get('price', dict())
                price = price.get('product')
                price = price // 100 if price else 'бесценно'

                sizes = item.get('sizes', dict(name='размеры не указаны'))
                sizes = ', '.join(size_item['name'] for size_item in sizes)

                seller_name = item.get('supplier', 'продавец не указан')
                seller_link = item.get('supplierId')
                seller_link = 'https://www.wildberries.ru/seller/{}'.format(
                    seller_link) if seller_link else 'не указано'

                quantity = item.get('totalQuantity', 'неизвестно')
                rating = item.get('nmReviewRating', 'неизвестно')
                rating_count = item.get('feedbacks', 'неизвестно')

                bucket_id, card_json = await self.card_parser.get_card_json(article_id)
                description = card_json.get('description', 'описание не указано')

                specifications = card_json.get('options', [])
                specifications = [': '.join((op_item['name'], op_item['value'])) for op_item in specifications]
                specifications = '\n'.join(specifications) if specifications else 'характеристики не указаны'

                image_count = card_json.get('media', dict()).get('photo_count', 0)
                image_links = self.get_image_links(bucket_id, article_id, image_count)

                item_data['card_link'] = 'https://www.wildberries.ru/catalog/{}/detail.aspx'.format(article_id)
                item_data['article'] = article_id
                item_data['name'] = name
                item_data['price'] = price
                item_data['description'] = description
                item_data['image_links'] = image_links
                item_data['specifications'] = specifications
                item_data['seller_name'] = seller_name
                item_data['seller_link'] = seller_link
                item_data['sizes'] = sizes
                item_data['quantity'] = quantity
                item_data['rating'] = rating
                item_data['rating_count'] = rating_count

                print('card parse end', time.perf_counter() - card_parse_start)
                parsed_data.append(item_data)

            if len(parsed_data) == products['total']:
                XLSXFormatter().generate_file(parsed_data)
                break

            page += 1
            print(
                'кол-во данных спаршено: {}/{} ({:.2f}%)'.format(len(parsed_data), products['total'],
                                                                 len(parsed_data) / products['total'] * 100))
            sleep(random.uniform(0.5, 2.0))

    def get_image_links(self, bucket_id, article_id, count):
        url_form = 'https://basket-{:02d}.wbbasket.ru/vol{}/part{}/{}/images/big/{}.webp'
        vol = article_id // 100000
        part = article_id // 1000
        result = []
        for i in range(1, count + 1):
            result.append(url_form.format(bucket_id, vol, part, article_id, i))

        return ', '.join(result)


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
    pars = CatalogParser(card_parser)
    data = await pars.parse_catalog('пальто из натуральной шерсти')


start = time.perf_counter()
try:
    asyncio.run(main('пальто из натуральной шерсти'))
except Exception as err:
    print(traceback.format_exc())
finally:
    end = time.perf_counter() - start
    print('парсинг данных завершился за {:.0f}м {:.2f}с'.format(end // 60, end % 60))
