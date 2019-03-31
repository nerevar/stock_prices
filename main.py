#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
from datetime import datetime

from lib.helpers import DATE_FORMAT
from lib.helpers import configure_logging
from lib.downloader import downloader
from lib.graphs import graphs_builder


def parse_args():
    parser = argparse.ArgumentParser(description='MOEX quotes downloader and graphs')
    subparsers = parser.add_subparsers(title='subcommands', dest='sub')

    download_parser = subparsers.add_parser('download', help='download quotes')
    download_parser.add_argument(
        '--engine',
        default='stock',
        choices=['stock', 'currency', 'nasdaq'],
        help='Доступные торговые системы: "stock, currency, nasdaq" https://iss.moex.com/iss/engines.xml',
    )
    download_parser.add_argument(
        '--market',
        required=True,
        # choices=['shares', 'bonds', 'index', 'selt'],
        help='Доступные рынки MOEX: "index, shares, bonds, selt" https://iss.moex.com/iss/engines/stock/markets.xml',
    )
    download_parser.add_argument(
        '--date',
        required=True,
        type=lambda d: datetime.strptime(d, DATE_FORMAT),
        help='Дата, за которую скачивать котировки в формате YYYY-MM-DD',
    )
    download_parser.add_argument(
        '--dateend',
        type=lambda d: datetime.strptime(d, DATE_FORMAT),
        help='Дата окончания диапазона дат [date, dateend] в формате YYYY-MM-DD',
    )
    download_parser.add_argument(
        '--save-raw-xml',
        action='store_true',
        help='Сохранять ли исходные XML файлы',
    )
    download_parser.set_defaults(fn=downloader)

    graphs_parser = subparsers.add_parser('graphs', help='build graphs')
    graphs_parser.add_argument(
        '--date',
        required=True,
        type=lambda d: datetime.strptime(d, DATE_FORMAT),
        help='Дата, за которую строить графики в формате YYYY-MM-DD',
    )
    graphs_parser.add_argument(
        '-g',
        '--graphs',
        '--graph',
        nargs='*',
        help='Названия графиков, которые пересчитать (английские названия папок). По-умолчанию — все.',
    )
    graphs_parser.add_argument(
        '-c',
        '--clear',
        action='store_true',
        help='Очищать ли предыдущие данные',
    )
    graphs_parser.add_argument(
        '--dateend',
        type=lambda d: datetime.strptime(d, DATE_FORMAT),
        help='Дата окончания диапазона дат [date, dateend] в формате YYYY-MM-DD',
    )
    graphs_parser.set_defaults(fn=graphs_builder)

    return parser.parse_args()


if __name__ == "__main__":
    configure_logging()
    args = parse_args()
    args.fn(args)
