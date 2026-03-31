import asyncio
import logging

import aiohttp

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

    async def card_parse(self, article_id: int) -> dict[str, str]:
        """
        Метод для извлечения детальных данных о товаре
        :param article_id: артикль товара
        :return: словарь с данными
        """
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

    async def get_card_json(self, article_id: int) -> tuple[int | None, dict]:
        """
        Метод для получения деталей о товаре
        :param article_id: артикль товара
        :return: кортеж bucket_id, словарь с данными
        """
        vol = article_id // 100000
        part = article_id // 1000

        possible_urls = [self.api_url_form.format(buck_id, vol, part, article_id) for buck_id in range(1, 44)]
        bucket_id, card_json = await self.find_media_url(possible_urls)

        return bucket_id, card_json

    async def find_media_url(self, urls) -> tuple[int | None, dict]:
        """
        Метод для поиска корректной ссылки на товар (card.json)
        :param urls: список ссылок которые нужно проверить
        :return: кортеж из корректного bucket_id и тела ответа с деталями о товаре
        """
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
                        logger.error(err, exc_info=True)
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
            logger.warning('не удалось найти найти url {}'.format('\n'.join(urls)))
            return None, dict()

    @staticmethod
    def get_image_links(bucket_id: int | str, article_id: int, count: int) -> str:
        """
        Метод для генерации ссылок на медиа-файлы
        :param bucket_id: id хранилища WB
        :param article_id: артикль товара
        :param count: кол-во картинок
        :return: ссылки через запятую
        """
        if not bucket_id:
            return 'не удалось извлечь ссылки'

        url_form = 'https://basket-{:02d}.wbbasket.ru/vol{}/part{}/{}/images/big/{}.webp'
        vol = article_id // 100000
        part = article_id // 1000
        result = []
        for i in range(1, count + 1):
            result.append(url_form.format(bucket_id, vol, part, article_id, i))

        return ', '.join(result)
