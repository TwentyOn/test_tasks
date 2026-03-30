import pandas as pd
import os


def filter_xlsx(filename: str):
    if not os.path.exists(filename):
        print(f'фильтрация не удалась: {filename} не найден')

    df = pd.read_excel(filename)
    filter_condition = (
            (df['характеристики'].str.contains('Страна производства: Россия')) &
            (df['рейтинг'] >= 4.5) &
            (df['цена'] <= 10000)
    )

    f = df[filter_condition]

    f['артикул'] = f['артикул'].astype(str)
    f.to_excel(f'selection_{filename}', index=False, engine_kwargs={'options': {'strings_to_urls': False}})
