import requests
from flask import request, redirect, flash, session


class FlaskAuth(object):
    @classmethod
    def checkauth(cls):
        ''' Check User Authentication
        '''
        path = request.path
        if path.startswith('/static') or path.startswith('/login') or path.startswith('/logout'):
            return
        else:
            # Restrict All Other Endpoints:
            if not cls.authenticated():
                print 'Warning: Unauthenicated User Attempted To Access Resource: %s' % path
                flash('Login Required', 'error')
                return redirect('/login')

    @classmethod
    def authenticate(cls, username, password):
        '''
        '''
        try:
            data = {'username': username, 'password': password}
            response = requests.post('http://localhost:5003/api/login', data=data, cookies=request.cookies)
            if response.json().get('user'):
                return response
            else:
                False
        except:
            # RMK: Might not be running auth server in this case
            return None

    @classmethod
    def deauthenticate(cls):
        '''
        '''
        try:
            return requests.post('http://localhost:5003/api/logout', cookies=request.cookies).json()
        except:
            # RMK: Might not be running auth server in this case
            return None

    @classmethod
    def authenticated(cls):
        '''
        '''
        try:
            response = requests.get('http://localhost:5003/api/authenticated', cookies=request.cookies).json()
            return response.get('user')
        except:
            # RMK: Might not be running auth server in this case
            return None
