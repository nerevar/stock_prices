# -*- coding: utf-8 -*-

import os
import logging
import requests

from lib.helpers import read_last_line, DATE_FORMAT

ALPHAVANTAGE_QUOTES_URL = 'https://www.alphavantage.co/query?function={function}&symbol={symbol}' \
                          '&datatype=csv&outputsize={size}&apikey={key}'


def get_filepath(symbol):
    return './quotes/nasdaq/{symbol}/{symbol}_data.csv'.format(symbol=symbol)


def is_data_exists(symbol):
    return os.path.exists(get_filepath(symbol))


def get_alphavantage_key():
    if 'ALPHAVANTAGE_KEY' in os.environ:
        return os.environ.get('ALPHAVANTAGE_KEY')

    with open('./.alphavantage_key') as f:
        return f.read()


def hide_apikey(url):
    apikey_param = '&apikey='
    apikey_index = url.find(apikey_param)
    return url[:apikey_index + len(apikey_param)] + 'NNNNN'


def download_alphavantage_data(symbol, size='compact'):
    key = get_alphavantage_key()

    url = ALPHAVANTAGE_QUOTES_URL.format(
        function='DIGITAL_CURRENCY_DAILY' if symbol == 'BTC' else 'TIME_SERIES_DAILY_ADJUSTED',
        symbol='BTC&market=RUB' if symbol == 'BTC' else symbol,
        key=key,
        size=size
    )

    logging.debug('Request: {}'.format(hide_apikey(url)))

    r = requests.get(url)

    return r.text


def save_to_file(lines, symbol, header=None):
    filepath = get_filepath(symbol)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    outfile = open(filepath, 'a' if os.path.exists(filepath) and header is None else 'w')

    if header:
        outfile.write(header)

    for line in lines:
        outfile.write(line + '\n')

    logging.info('Saved: {} lines'.format(len(lines)))

    outfile.close()


def filter_new_lines(symbol, lines):
    filepath = get_filepath(symbol)
    last_line = read_last_line(filepath)
    return [x for x in lines if x > last_line]


def filter_dates(lines, dates):
    start = dates[0].strftime(DATE_FORMAT)
    end = dates[-1].strftime(DATE_FORMAT)
    return [x for x in lines if start <= x[:10] <= end]


def extract_csv(csv_data):
    lines = csv_data.split('\n')
    header = lines.pop(0)
    lines.sort()
    return header, lines


def get_nasdaq_data(engine, symbol, dates):
    is_file_exists = is_data_exists(symbol)

    logging.info((engine, symbol))
    csv_data = download_alphavantage_data(symbol, 'compact' if is_file_exists else 'full')

    header, lines = extract_csv(csv_data)

    logging.info('Got: {} lines'.format(len(lines)))

    # оставляем только строки за указанный диапазон дат
    lines = filter_dates(lines, dates)

    if is_file_exists:
        new_lines = filter_new_lines(symbol, lines)
        if len(new_lines):
            save_to_file(new_lines, symbol)
    else:
        save_to_file(lines, symbol, header)
