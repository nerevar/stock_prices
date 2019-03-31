class GraphBuilder(object):
    def market_filter(self):
        return {
            'engine': 'stock',
            'market': 'index'
        }

    def quote_filter(self):
        return {
            'BOARDID': 'SNDX',
            'SECID': 'IMOEX'
        }

    def get_value(self, df):
        quote = df.iloc[0]
        return float(quote.get('CLOSE'))
