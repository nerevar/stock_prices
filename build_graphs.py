import os
import importlib
import pandas as pd
from datetime import datetime
from collections import defaultdict


def load_graph_builder(name):
    module = importlib.import_module('graph_data.{}.graph'.format(name))
    return module.GraphBuilder()


def load_graph_builders():
    graphs = {}
    for folder in next(os.walk('./graph_data'))[1]:
        if '__' in folder:
            continue
        graphs[folder] = load_graph_builder(folder)

    return graphs


def load_data(engine, market, day):
    # day = datetime.strptime(date, DATE_FORMAT)
    filepath = './quotes/{year}/{month}/{day}/{year}-{month}-{day}-{engine}-{market}.csv'.format(
        year=day.strftime('%Y'),
        month=day.strftime('%m'),
        day=day.strftime('%d'),
        engine=engine,
        market=market
    )
    return pd.read_csv(filepath)


def filter_data(df, filters):
    return df.loc[(df[list(filters)] == pd.Series(filters)).all(axis=1)]


def merge_values(date, value):
    return [date] + (list(value) if isinstance(value, (list, tuple)) else [value])


def calc_value(df, builder):
    df_filtered = filter_data(df, builder.quote_filter())
    date = builder.get_date(df_filtered)
    value = builder.get_value(df_filtered)
    return merge_values(date, value)


def main():
    graph_builders = load_graph_builders()

    results = {}
    graph_builders_by_market = defaultdict(list)
    for name, builder in graph_builders.items():
        results[name] = []
        market_filter = builder.market_filter()
        graph_builders_by_market[(market_filter['engine'], market_filter['market'])].append({
            'name': name,
            'builder': builder
        })

    for day in [datetime(2019, 3, 5), datetime(2019, 3, 6)]:
        for (engine, market), builders in graph_builders_by_market.items():
            data = load_data(engine, market, day)
            for builder in builders:
                result = calc_value(data, builder['builder'])
                results[builder['name']].append(result)

    print(results)

if __name__ == "__main__":
    main()
