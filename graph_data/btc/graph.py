from datetime import datetime


class GraphBuilder(object):
    date_field = 'timestamp'
    value_field = 'close (USD)'

    def market_filter(self):
        return {
            'engine': 'nasdaq',
            'market': 'BTC'
        }

    def get_values(self, df):
        df['date_field'] = df[self.date_field].apply(
            lambda x: int(datetime.strptime(x, '%Y-%m-%d').timestamp()) * 1000
        )
        return df[['date_field', self.value_field]].values.tolist()
