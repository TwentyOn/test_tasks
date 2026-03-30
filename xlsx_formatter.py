import logging
from datetime import date

import xlsxwriter

logger = logging.getLogger(__name__)


class XLSXFormatter:
    def __init__(self):
        self.document = xlsxwriter.Workbook()

    def __write_header(self, sheet, headers):
        for i, header in enumerate(headers):
            sheet.write(0, i, header)

    def __formate_specification(self, value: dict):
        spec_contet = ''
        for k, v in value.items():
            spec_contet += k + '\n'
            specs = [': '.join(s) for s in v]
            spec_contet += '\n'.join(specs) + '\n\n'

        return spec_contet

    def generate_file(self, data: list[dict], name: str = 'parsed_data.xlsx'):
        logger.info('формирование xlsx-файла...')

        if not name.endswith('.xlsx'):
            raise ValueError('некорректное имя файла')

        name, ext = name.split('.')
        filename = '{}_{}.{}'.format(name, date.today(), ext)
        self.document.filename = filename
        sheet = self.document.add_worksheet()

        headers = [
            'ссылка на товар', 'артикул', "название", "цена", "описание", "ссылки на изображения",
            "характеристики", "продавец", "ссылка на продавца", "размеры", "остатки", "рейтинг", "кол-во отзывов"
        ]
        self.__write_header(sheet, headers)

        for i, item in enumerate(data, start=1):
            for j, k in enumerate(item):
                val = item[k]
                sheet.write_string(i, j, str(val))

        self.document.close()

        return filename
