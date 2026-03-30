import asyncio
from time import perf_counter
import logging

from parsers.catalog_parser import CatalogParser
from parsers.card_parser import CardParser
from xlsx_processing.xlsx_formatter import XLSXFormatter
from xlsx_processing.xlsx_selection import filter_xlsx

logging.basicConfig(
    level=logging.INFO,
    format='[{asctime}] #{levelname:4} {name}:{lineno} - {message}',
    style='{'
)
logger = logging.getLogger(__name__)


async def main(query: str):
    card_parser = CardParser()
    xlsx_fmt = XLSXFormatter()

    catalog_parser = CatalogParser(card_parser)
    data = await catalog_parser.parse_catalog(query)

    out_xlsx_path = xlsx_fmt.generate_file(data)
    filter_xlsx(out_xlsx_path)


if __name__ == '__main__':
    start = perf_counter()

    try:
        asyncio.run(main('пальто из натуральной шерсти'))

    except Exception as err:
        logger.error(err, exc_info=True)

    finally:
        end = perf_counter() - start
        print('парсинг данных завершился за {:.0f}м {:.2f}с'.format(end // 60, end % 60))
