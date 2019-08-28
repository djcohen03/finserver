import json
import datetime
from dateutil.relativedelta import relativedelta
from flask import Flask, render_template
from .fincore.db.models import Tradable, session

app = Flask(__name__, template_folder="static/templates")

class Helpers(object):
    @classmethod
    def getdaysession(cls, tradable, date):
        ''' Get's the prices for the given tradable on the given day
        '''
        query = session.execute('''
            SELECT close, time FROM price WHERE request_id IN (
                SELECT id FROM price_request WHERE tradable_id = %s
            )
            AND time > '%s'
            AND time < '%s';
        ''' % (
            tradable.id,
            date.strftime('%Y-%m-%d'),
            (date + relativedelta(days=1)).strftime('%Y-%m-%d'),
        ))
        # Unpack the query results:
        prices, times = zip(*[(float(v), t) for (v, t) in query])
        return prices, times

    @classmethod
    def getdates(cls, tradableid):
        ''' Get the available dates for the given tradable
        '''
        query = session.execute('''
            SELECT DATE(time) FROM price
            WHERE request_id IN (
                SELECT id FROM price_request WHERE tradable_id = %s
            ) GROUP BY DATE(time);
        ''' % tradableid)
        # Unpack the query results:
        return sorted([date for (date,) in query])

    @classmethod
    def memoryused(cls):
        ''' Get's the amount of memory used in GB
        '''
        query = session.execute("SELECT pg_database_size('options');")
        memory = [byts for (byts,) in query][0]
        gigabytes = memory / (1000. ** 3)
        return round(gigabytes, 2)

    @classmethod
    def getlastclose(cls, tradable, date):
        ''' Runs a query to get the last close for the given tradable before
            the given date
        '''
        query = session.execute('''
            SELECT close, time FROM price WHERE request_id IN (
                SELECT id FROM price_request WHERE tradable_id=%s
            ) AND time < '%s' order by time desc limit 1;
        ''' % (
            tradable.id,
            date.strftime('%Y-%m-%d')
        ))
        price, time = [(float(p), t) for (p, t) in query][0]
        return price, time



@app.route('/')
def index():
    ''' Home Page Endpoint
    '''
    # Get all database tradables:
    tradables = session.query(Tradable).all()
    tradables.sort(key=lambda t: t.name)
    # Get the amount of memory used:
    gigabytes = Helpers.memoryused()
    return render_template('index.html', tradables=tradables, gigabytes=gigabytes)

@app.route('/tradable/<int:id>')
def tradable(id):
    ''' Display the information summary for the given tradable
    '''
    # Get the tradable
    tradable = session.query(Tradable).get(id)
    # Get the available dates for this tradable:
    dates = Helpers.getdates(tradable.id)
    dates.reverse()
    return render_template('tradable.html', tradable=tradable, dates=dates)


# MARK: Api Endpoints:
@app.route('/api/v1/tradable/<int:id>/<datestr>')
def daysession(id, datestr):
    ''' API For getting prices on a given day
    '''
    tradable = session.query(Tradable).get(id)
    date = datetime.datetime.strptime(datestr, '%Y-%m-%d')
    prices, timestamps = Helpers.getdaysession(tradable, date)
    times = [ts.strftime('%H:%M') for ts in timestamps]
    lastprice, _ = Helpers.getlastclose(tradable, date)
    return json.dumps({
        'tradable': tradable.name,
        'date': datestr,
        'prices': prices,
        'times': times,
        'lastprice': lastprice
    }), 200
