# python main.py graphs --date 2018-01-01 --dateend 2019-05-10 --graphs gruzovichkov_moex --clear


class GraphBuilder(object):
    value_field = 'CLOSE'

    def market_filter(self):
        return {
            'engine': 'stock',
            'market': 'shares'
        }

    def quote_filter(self):
        return {
            'BOARDID': 'TQTF',
            'SECID': ['SBMX', 'FXRL'],
        }

    def get_value(self, df):
        result = []
        filters = self.quote_filter()
        for name in filters['SECID']:
            value = df.loc[df['SECID'] == name][self.value_field]
            result.append(float(value) if len(value) else None)
        return result
