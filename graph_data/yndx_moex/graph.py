class GraphBuilder(object):
    def market_filter(self):
        return {
            'engine': 'stock',
            'market': 'shares'
        }

    def quote_filter(self):
        return {
            'BOARDID': 'TQBR',
            'SECID': 'YNDX'
        }

    def get_value(self, df):
        quote = df.iloc[0]
        return float(quote.get('CLOSE'))
