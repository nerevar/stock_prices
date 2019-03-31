# -*- coding: utf-8 -*-

import os
import csv
import importlib
import pandas as pd
from collections import defaultdict

from lib.helpers import daterange


def load_graph_builder(name):
    module = importlib.import_module('graph_data.{}.graph'.format(name))
    return module.GraphBuilder()


def load_graph_builders(graphs_list):
    if graphs_list is None:
        graphs_list = next(os.walk('./graph_data'))[1]

    graphs = defaultdict(list)
    for graph_name in graphs_list:
        if '__' in graph_name:
            continue

        builder = load_graph_builder(graph_name)
        market_filter = builder.market_filter()
        graphs[(market_filter['engine'], market_filter['market'])].append({
            'name': graph_name,
            'builder': builder
        })

    return graphs


def load_data(engine, market, day):
    filepath = './quotes/{year}/{month}/{day}/{year}-{month}-{day}-{engine}-{market}.csv'.format(
        year=day.strftime('%Y'),
        month=day.strftime('%m'),
        day=day.strftime('%d'),
        engine=engine,
        market=market
    )
    if os.path.exists(filepath):
        return pd.read_csv(filepath)
    else:
        return None


def filter_data(df, filters):
    return df.loc[(df[list(filters)] == pd.Series(filters)).all(axis=1)]


def merge_values(date, value):
    return [date] + (list(value) if isinstance(value, (list, tuple)) else [value])


def get_timestamp(day):
    # TODO: utc -> moscow time
    return int(day.timestamp()) * 1000


def calc_value(df, builder, day):
    df_filtered = filter_data(df, builder.quote_filter())
    if df_filtered.shape[0] >= 1:
        value = builder.get_value(df_filtered)
        return merge_values(get_timestamp(day), value)
    else:
        return None


def save_values(name, values, clear=False):
    filepath = './graph_data/{}/values.csv'.format(name)
    outfile = open(filepath, 'a' if os.path.exists(filepath) and not clear else 'w')
    writer = csv.writer(outfile)

    for row in values:
        writer.writerow(row)
    outfile.close()


def graphs_builder(args):
    graph_builders = load_graph_builders(args.graphs)

    if args.dateend:
        dates = daterange(args.date, args.dateend)
    else:
        dates = [args.date]

    results = defaultdict(list)
    for day in dates:
        for (engine, market), builders in graph_builders.items():
            data = load_data(engine, market, day)
            if data is None:
                continue
            for builder in builders:
                result = calc_value(data, builder['builder'], day)
                if result is not None:
                    results[builder['name']].append(result)

    for name, values in results.items():
        save_values(name, values, args.clear)

    print(results)
