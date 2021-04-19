import os
import json
import logging
import datetime
from dateutil.relativedelta import relativedelta
from flask import Flask, render_template, request, flash, redirect, make_response
from fincore.db.models import Tradable, session
from correlations import Correlations
from auth import FlaskAuth

app = Flask(__name__, template_folder="static/templates")

# Set app secret key for message flashing:
app.secret_key = os.urandom(24)

# Initialize Logging:
logging.basicConfig(level=logging.INFO)
log = logging.getLogger('finserver')

class Helpers(object):
    @classmethod
    def getdaysession(cls, tradable, date):
        ''' Get's the prices for the given tradable on the given day
        '''
        query = session.execute('''
            SELECT time, close FROM price WHERE request_id IN (
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
        prices, times = zip(*[(float(v), t) for (t, v) in sorted(query)])
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



@app.route('/login', methods=['GET', 'POST'])
def login():
    ''' Login Endpoint API
    '''
    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        auth = FlaskAuth.authenticate(username, password)
        if auth:
            response = make_response()
            for cookie, value in auth.cookies.iteritems():
                response.set_cookie(cookie, value)

            response.headers['location'] = '/'

            flash('Credential Accepted', 'success')
            return response, 302
        else:
            flash('Incorrect Username/Password', 'error')
            return redirect('/login')

@app.route('/logout')
def logout():
    ''' Login Endpoint API
    '''
    # Do deauthentication:
    FlaskAuth.deauthenticate()

    # Make response & drop all cookies:
    response = make_response()
    for cookie, value in request.cookies.iteritems():
        response.set_cookie(cookie, '')
    response.headers['location'] = '/login'

    flash('Successfully Logged Out', 'info')
    return response, 302

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

@app.route('/correlation')
def correlation():
    '''
    '''
    tradables = session.query(Tradable).all()
    tradables.sort(key=lambda t: t.name)
    return render_template('correlation.html', tradables=tradables)


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


@app.route('/api/v1/correlation')
def correlationapi():
    ''' API For getting prices on a given day
    '''
    symbols = request.args.getlist('symbols[]')

    # Make correlation matrix:
    correlations = Correlations.matrix(symbols)

    return json.dumps({
        'correlations': correlations,
        'symbols': symbols,
    }), 200


# Setup authentication:
app.before_request(FlaskAuth.checkauth)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
