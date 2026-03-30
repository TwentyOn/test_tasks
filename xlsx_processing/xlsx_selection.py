import pandas as pd
import os


def filter_xlsx(filename: str):
    """
    Логика выборки данных
    :param filename:
    :return:
    """
    if not os.path.exists(filename):
        print(f'фильтрация не удалась: {filename} не найден')

    df = pd.read_excel(filename)
    filter_condition = (
            (df['характеристики'].str.contains('Страна производства: Россия')) &
            (df['рейтинг'] >= 4.5) &
            (df['цена'] <= 10000)
    )

    filtered_pd = df[filter_condition]

    filtered_pd['артикул'] = filtered_pd['артикул'].astype(str)
    filtered_pd = filtered_pd.sort_values(['кол-во отзывов', 'рейтинг'], ascending=False)

    filtered_pd.to_excel(f'selection_{filename}', index=False, engine_kwargs={'options': {'strings_to_urls': False}})
