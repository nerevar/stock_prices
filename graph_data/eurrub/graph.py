class GraphBuilder(object):
    def market_filter(self):
        return {
            'engine': 'currency',
            'market': 'selt'
        }

    def quote_filter(self):
        return {
            'BOARDID': 'CETS',
            'SHORTNAME': 'EURRUB_TOD'
        }

    def get_value(self, df):
        quote = df.iloc[0]
        return float(quote.get('CLOSE'))
