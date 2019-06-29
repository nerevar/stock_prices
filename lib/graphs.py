# -*- coding: utf-8 -*-

import os
import csv
import json
import pytz
import importlib
import pandas as pd
from datetime import datetime
from collections import defaultdict

from lib.helpers import daterange
from lib.nasdaq_downloader import get_filepath as get_nasdaq_filepath
from lib.moex_downloader import get_filepath as get_moex_filepath


class BaseGraph(object):
    @staticmethod
    def date_to_timestamp(date):
        dt = datetime.strptime(date, '%Y-%m-%d') if type(date) == str else date

        dt = dt \
            .replace(tzinfo=pytz.UTC) \
            .astimezone(pytz.timezone('Europe/Moscow'))
        return int(dt.timestamp()) * 1000


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
    if engine == 'nasdaq':
        filepath = get_nasdaq_filepath(market)
    else:
        filepath = get_moex_filepath(engine, market, day)

    if os.path.exists(filepath):
        return pd.read_csv(filepath)
    else:
        return None


def build_filters_string(filters):
    """Формирует строку для Pandas query, для фильтрации нужной ценной бумаги"""
    parts = []
    for key, value in filters.items():
        if isinstance(value, (list, tuple)):
            parts.append('({key} in {value})'.format(key=key, value=json.dumps(value, ensure_ascii=False)))
        else:
            parts.append('({key} == "{value}")'.format(key=key, value=value))
    return ' and '.join(parts)


def merge_values(date, value):
    return [date] + (list(value) if isinstance(value, (list, tuple)) else [value])


def calc_daily_value(df, builder, day):
    """Вычисляет точку графика `builder` за день `day` по данным из таблицы `df`
    Возвращает [timestamp, значение графика[, значение 2 графика[, значение 3 графика]]]"""
    filters_string = build_filters_string(builder.quote_filter())
    df_filtered = df.query(filters_string)

    if df_filtered.shape[0] >= 1:
        value = builder.get_value(df_filtered)
        return merge_values(BaseGraph.date_to_timestamp(day), value)
    else:
        return None


def calc_batch_values(df, builder):
    """Пересчитывает сразу весь график `builder` по данным из таблицы `df`"""
    return builder.get_values(df)


def save_values(name, values, clear=False):
    filepath = './graph_data/{}/values.csv'.format(name)
    outfile = open(filepath, 'a' if os.path.exists(filepath) and not clear else 'w')
    writer = csv.writer(outfile)

    for row in values:
        writer.writerow(row)
    outfile.close()


def graphs_builder(args):
    graph_builders = load_graph_builders(args.graphs)
    results = defaultdict(list)

    if args.dateend:
        dates = daterange(args.date, args.dateend)
    else:
        dates = [args.date]

    # days iterator for moex graphs
    for day in dates:
        for (engine, market), builders in graph_builders.items():
            if engine not in ['stock', 'currency']:
                continue
            data = load_data(engine, market, day)
            if data is None:
                continue
            for builder in builders:
                result = calc_daily_value(data, builder['builder'], day)
                if result is not None:
                    results[builder['name']].append(result)

    # batch graph builder for nasdaq graphs
    for (engine, market), builders in graph_builders.items():
        if engine != 'nasdaq':
            continue
        data = load_data(engine, market, None)
        if data is None:
            continue
        for builder in builders:
            for value in calc_batch_values(data, builder['builder']):
                results[builder['name']].append(value)

    for name, values in results.items():
        save_values(name, values, args.clear)

    print('got data for graphs: {}'.format(results.keys()))
