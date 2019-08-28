import datetime
from dateutil.relativedelta import relativedelta
from flask import Flask, render_template
from .fincore.db.models import Tradable, session

app = Flask(__name__, template_folder="static/templates")

@app.route('/')
def index():
    ''' Home Page Endpoint
    '''
    tradables = session.query(Tradable).all()
    tradables.sort(key=lambda t: t.name)
    gigabytes = memoryused()
    return render_template('index.html', tradables=tradables, gigabytes=gigabytes)

@app.route('/tradable/<int:id>')
def tradable(id):
    tradable = session.query(Tradable).get(id)
    dates = [(d, d.strftime('%B %d, %Y')) for d in reversed(getdates(tradable.id))]
    return render_template('tradable.html', tradable=tradable, dates=dates)

@app.route('/tradable/<int:id>/<datestr>')
def daysession(id, datestr):
    ''' Displays a day session of prices
    '''
    tradable = session.query(Tradable).get(id)
    date = datetime.datetime.strptime(datestr, '%Y-%m-%d')
    prices, timestamps = getdaysession(tradable, date)
    times = [ts.strftime('%H:%M') for ts in timestamps]
    return render_template(
        'daysession.html',
        tradable=tradable,
        prices=prices,
        times=times,
        date=date.strftime('%B %d, %Y')
    )


def getdaysession(tradable, date):
    '''
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
    prices, times = zip(*[(float(v), t) for (v, t) in query])
    return prices, times



def getdates(tradableid):
    ''' For the given tradable, get the dates that that tradable has data for
    '''
    query = session.execute('''
        SELECT DATE(time) FROM price
        WHERE request_id IN (
            SELECT id FROM price_request WHERE tradable_id = %s
        ) GROUP BY DATE(time);
    ''' % tradableid)
    return [date for (date,) in query]

def memoryused():
    ''' Get's the amount of memory used in GB
    '''
    query = session.execute("SELECT pg_database_size('options');")
    memory = [byts for (byts,) in query][0]
    gigabytes = memory / (1000. ** 3)
    return round(gigabytes, 2)
