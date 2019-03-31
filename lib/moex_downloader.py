# -*- coding: utf-8 -*-

import os
import csv
import logging
import requests
from collections import OrderedDict
from datetime import datetime
from xml.etree import ElementTree

from lib.helpers import DATE_FORMAT

MOEX_QUOTES_URL = 'https://iss.moex.com/iss/history/engines/{engine}/markets/{market}/securities.xml' \
                  '?limit=100&date={date}&start={start}'


def get_filepath(engine, market, day):
    return './quotes/{year}/{month}/{day}/{year}-{month}-{day}-{engine}-{market}.csv'.format(
        year=day.strftime('%Y'),
        month=day.strftime('%m'),
        day=day.strftime('%d'),
        engine=engine,
        market=market
    )


def download_moex_data(engine, market, date, start=0, save_raw_xml=False):
    url = MOEX_QUOTES_URL.format(
        engine=engine,
        market=market,
        date=date,
        start=start
    )

    logging.debug('Request: {}'.format(url))

    r = requests.get(url)

    if save_raw_xml:
        with open('./downloads/moex_data_{}_{}_{}_{}.xml'.format(engine, market, date, start), 'w') as f:
            f.write(r.text)

    return r.text


def save_to_csv(quotes, engine, market, date, header_attrs=None):
    date_parsed = datetime.strptime(date, DATE_FORMAT)
    filepath = get_filepath(engine, market, date_parsed)

    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    outfile = open(filepath, 'a' if os.path.exists(filepath) and header_attrs is None else 'w')
    writer = csv.writer(outfile)

    if header_attrs:
        writer.writerow(header_attrs.keys())

    for row in quotes:
        writer.writerow(row.values())

    outfile.close()


def parse_row_attributes(root):
    TYPES_MAP = {
        'string': str,
        'date': str,
        'time': str,
        'double': float,
        'int32': int,
        'int64': int,
    }

    result = OrderedDict()
    for row in root.findall("data[@id='history']/metadata/columns/column"):
        result[row.get('name')] = TYPES_MAP.get(row.get('type'), str)

    return result


def parse_pagination(root):
    for row in root.findall("data[@id='history.cursor']/rows/row[@TOTAL]"):
        return {
            'total_items': int(row.get('TOTAL', 0)),
            'current_index': int(row.get('INDEX', 0)),
            'page_size': int(row.get('PAGESIZE', 0))
        }


def validate_float_val(quote, key):
    return quote.get(key) and quote.get(key) > 0


def validate_quote(quote, engine, market):
    if engine == 'currency' and market == 'selt':
        return validate_float_val(quote, 'VOLRUR') \
               or validate_float_val(quote, 'NUMTRADES') \
               or validate_float_val(quote, 'CLOSE')
    elif engine == 'stock' and market in ['bonds', 'shares']:
        return validate_float_val(quote, 'VOLUME') \
               or validate_float_val(quote, 'NUMTRADES') \
               or validate_float_val(quote, 'CLOSE')
    elif engine == 'stock' and market == 'index':
        return validate_float_val(quote, 'CLOSE')

    assert False, 'Unknown quote type'


def parse_quotes(root, quote_attrs):
    DEFAULT_QUOTE_ATTR_VALUE = ''

    quotes = []
    for row in root.findall("data[@id='history']/rows/row"):
        quote = OrderedDict()
        for attr_name, attr_type in quote_attrs.items():
            value = row.get(attr_name)
            quote[attr_name] = attr_type(value) if value else DEFAULT_QUOTE_ATTR_VALUE
        quotes.append(quote)
    return quotes


def parse_moex_data(xml_data):
    root = ElementTree.fromstring(xml_data)

    pagination = parse_pagination(root)
    quote_attrs = parse_row_attributes(root)
    quotes = parse_quotes(root, quote_attrs)

    return pagination, quote_attrs, quotes


def get_moex_data(engine, market, date_str, start=0, save_raw_xml=False):
    xml_data = download_moex_data(engine, market, date_str, start, save_raw_xml)
    pagination, quote_attrs, quotes = parse_moex_data(xml_data)

    valid_quotes = [q for q in quotes if validate_quote(q, engine, market)]

    if len(valid_quotes):
        save_to_csv(valid_quotes, engine, market, date_str, quote_attrs if start == 0 else None)
    else:
        if len(quotes) == 0:
            logging.error('No quotes for "{}, {}, {}, {}", pagination: {}'.format(
                engine, market, date_str, start, pagination))

    logging.debug('Got quotes: {:3d}/{:3d}, pagination: {}, params: {}, {}, {}, {}'.format(
        len(valid_quotes), len(quotes),
        '{} + {} < {}'.format(pagination['current_index'], pagination['page_size'], pagination['total_items']),
        engine, market, date_str, start))

    if pagination['current_index'] + pagination['page_size'] < pagination['total_items']:
        get_moex_data(engine, market, date_str, start + pagination['page_size'], save_raw_xml)
