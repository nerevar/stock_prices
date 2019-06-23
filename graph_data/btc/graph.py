# -*- coding: utf-8 -*-

from lib.graphs import BaseGraph


class GraphBuilder(BaseGraph):
    date_field = 'timestamp'
    value_field = 'close (USD)'

    def market_filter(self):
        return {
            'engine': 'nasdaq',
            'market': 'BTC'
        }

    def get_values(self, df):
        df['date_field'] = df[self.date_field].apply(BaseGraph.date_to_timestamp)
        return df[['date_field', self.value_field]].values.tolist()
