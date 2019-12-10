import datetime
import pandas as pd
from fincore.db.models import Tradable, session, engine


class Helpers(object):
    @classmethod
    def getprices(cls, symbols):
        '''
        '''
        today = datetime.date.today()
        cutoff = today - datetime.timedelta(days=150)

        # Get a list of tradables:
        tradables = session.query(Tradable).filter(Tradable.name.in_(symbols)).all()

        # Construct SQL Query:
        query = '''
            SELECT close, time, tradable_id FROM price
                JOIN price_request
                ON price.request_id = price_request.id
                WHERE tradable_id in (%s) AND price.time >= '%s';
        ''' % (
            ', '.join([str(tradable.id) for tradable in tradables]),
            cutoff.strftime('%Y-%m-%d 00:00:00.000000'),
        )

        # Do Prices table query:
        print 'Querying Prices Table...'
        prices = pd.read_sql(query, engine).sort_values('time')
        prices['time'] = pd.to_datetime(prices['time'])

        # Split query into separate series:
        series = {}
        for tradable in tradables:
            tprices = prices[prices.tradable_id == tradable.id]
            tprices.index = tprices.time
            series[tradable.name] = tprices.close

        return pd.DataFrame(series)


class Correlations(object):
    @classmethod
    def matrix(cls, symbols):
        ''' Get the Correlation Matrix
        '''
        prices = Helpers.getprices(symbols)
        corrs = prices.corr().round(2)
        return corrs.values.tolist()
