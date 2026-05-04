
#import warnings
#warnings.simplefilter(action='ignore', category=FutureWarning)
import requests
import json
import lxml
import lxml.html

from datetime import datetime


class requestHistory(object):
    def __init__(self, response):
        self.response = response
        self._text = None
        self._xtext = None
        self._json = {}
        self.request = None
        self.status_code = None
        self.headers = {}
        self.url = None
        self._request_status = None
        self._request_extra = {}
        self._date_made = datetime.now()#.strftime('%Y-%m-%d - %H:%M:%S')
        self._date_response = None
        self._load()
    def set_status(self, value, extra=None):
        self._request_status = value
        if extra is not None:
            self.add_extra(data=extra)
    def get_status(self):
        return self._request_status
    def add_extra(self, data):
        self._request_extra = data
    def get_extra(self):
        return self._request_extra
    def _load(self):
        if isinstance(self.response, requests.models.Response):
            self.status_code = self.response.status_code
            self.request = self.response.request
            self.headers = self.response.headers
            self.url = self.response.url
            date_response = self.headers.get('Date', None)
            if date_response:
                try:
                    date_response = datetime.strptime(date_response, '%a, %d %b %Y %H:%M:%S GMT')
                except Exception as err:
                    print(f'requestHistory._load exp {err}')
                else:
                    self._date_response = date_response
    def content(self):
        return self.text()
    def text(self):
        if not self._text:
            self._text = self.response.text
        return self._text
    def xtext(self):
        if self._xtext is None:
            temp_text = self.text()
            if temp_text:
                try:
                    xbody = lxml.html.fromstring(temp_text)
                except Exception as err:
                    print(f'requestHistory.xtext exp - {err}')
                else:
                    if xbody is not None:
                        self._xtext = xbody
        return self._xtext
    def json(self):
        if not self._json:
            try:
                self._json = json.loads(self.text())
            except Exception as err:
                print(f'requestHistory.json exp - {err}')
        return self._json
    def __repr__(self):
        url = self.response.url
        has_history = True if self.response.history else False
        date_made = self._date_made.strftime('%Y-%m-%d - %H:%M:%S') if self._date_made else None
        date_made_header = self._date_response.strftime('%Y-%m-%d - %H:%M:%S') if self._date_response else None
        return f'<Status {self.status_code} --- {url} --- Has History - {has_history} -- Total Time {self.response.elapsed.total_seconds()} --- DateTime {date_made_header or date_made} >'



