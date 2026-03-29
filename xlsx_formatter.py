import xlsxwriter

class XLSXFormatter:
    def __init__(self):
        self.document = xlsxwriter.Workbook('text.xlsx')
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
            "характеристики", "продавец", "ссылка на продавца", "размеры", "остатки", "рейтинг", "кол-во отзывов"
        ]
        self.__write_header(headers)

        for i, item in enumerate(data, start=1):
            for j, k in enumerate(item):
                val = item[k]
                self.sheet.write_string(i, j, str(val))

        self.document.close()