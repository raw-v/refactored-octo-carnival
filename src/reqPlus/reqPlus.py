import logging


from requests.structures import CaseInsensitiveDict
import requests
#import httpx as requests
import json
import time
import sys
import lxml
import lxml.html





from .utils.exceptions import(
    expInvalidRequest,
    expInvalidRequestsResponse,
    invalidCredentials,
    userNotFound,
    captchaWrong,
    expMaxRetries,
    expSpecialTimeOut
)


from .utils.requestPlus import(
    requestHistory
)

#import urllib

class dynamicObj(object):
    def __init__(self, **kwg):
        self.__dict__.update(**kwg)
    def __repr__(self):
        return str(self.__dict__)


class reqResponses(object):
    def __init__(self, requests_item):
        self.__dict__.update(**requests_item)
    def __repr__(self):
        temp = '\n'.join(f'{k} - {v}' for k, v in self.__dict__.items())
        return temp
        return str(self.__dict__)



class oi(object):
    def __init__(self, data):
        self.data = data
        self.r = reqResponses(requests_item=self.data)
    def add(self, chave, valor):
        self.data.update({chave:valor})
    @property
    def reqs(self):
        return reqResponses(requests_item=self.data)





logger = logging.getLogger(f'{__name__}.cornomanso')





class reqPlus(object):
    def __init__(self, proxies={}, timeout=30, default_useragent=None, verify=True):
        self.proxies = proxies
        self.timeout = timeout
        self._session = None
        self._requests = {}
        self._cur_state = None
        self._default_useragent = default_useragent if default_useragent else 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0'
        self._verify = verify
        self._connection_state = 'close'
        logger.debug(f"startado {self.__class__.__qualname__} com proxies = {self.proxies} e timeout = {self.timeout}")
        self._logger = self.config_logger()
    def config_logger(self):
        return logger.getChild(self.__class__.__name__)
    @property
    def logger(self):
        return self._logger
    @property
    def _responses(self):
        return reqResponses(requests_item=self._requests)
    def set_current_state(self, value):
        self._cur_state = value
    @property
    def current_state(self):
        return self._cur_state
    def close_session(self):
        if self._session:
            self._session.close()
    def connection_session_keep(self):
        self._connection_state = 'keep-alive'
        if self._session:
            self._session.headers.update({'Connection': self._connection_state})
    def connection_session_close(self):
        self._connection_state = 'close'
        if self._session:
            self._session.headers.update({'Connection': self._connection_state})
    def new_session(self, ua=False):
        self._new_session(ua=ua)
    def _new_session(self, ua=False):
        temp = requests.Session()
        #temp = requests.Client()
        temp.proxies = self.proxies
        temp.verify = self._verify
        temp.headers.update({'Connection': self._connection_state})
        self._session = temp
        self._requests = {}
        if ua is not False:
            if type(ua) == str:
                self._default_useragent = ua
    def gen_headers(
        self,
        *args,
        **kwgs
    ):
        return self._gen_headers(*args, **kwgs)
    def _gen_headers(self,
        origin=None,
        referer=None,
        ua=None,
        bearer=None,
        **kwgs
    ):
        temp_headers = {
            'User-Agent': self._default_useragent if not ua else ua,
            'Connection': self._connection_state
        }
        if origin is not None:
            temp_headers.update(
                {
                    'Origin': origin
                }
            )
        if referer is not None:
            temp_headers.update(
                {
                    'Referer': referer
                }
            )
        if bearer is not None:
            temp_headers.update(
                {
                    'Authorization': f'Bearer {bearer}'
                }
            )
        temp_headers.update(**kwgs)
        return temp_headers
    def _add_request(self, name, response):
        try:
            temp_request = requestHistory(response=response)
            if temp_request:
                self._requests.update(
                    {
                        name: temp_request
                    }
                )
                return temp_request
        except Exception as err:
            print(f'reqPlus._add_request exp - {err}')
        return False
    def get_request(
        self,
        name,
        request_status=None,
        status_code=None
    ):
        temp_response = self._get_request(name=name)
        if temp_response:
            if request_status is not None:
                if temp_response.get_status() == request_status:
                    return temp_response
            elif status_code is not None:
                if temp_response.status_code == status_code:
                    return temp_response
            else:
                return temp_response
        return False
    def _get_request(self, name):
        return self._requests.get(name, False)
    def _make_call(self, 
        url, 
        headers, 
        data=None, 
        json=None, 
        files=None,
        method=None, 
        _allow_redirect=False,
        _auto_retry=False,
        _auto_retry_max=False,
        _auto_retry_status_code=[],
        _retries=0,
        _caller=None,
        _delay=False,
        _use_session=True,
        _use_proxy=True,
        _raise_me=False,
        **kwgs
    ):
        caller = sys._getframe(1).f_code.co_name if not _caller else _caller
        self.set_current_state(value=caller)
        should_raise_max_retries = False
        should_raise = None
        repeat_me = False
        response = None
        is_ok = False
        try:
            method = method.upper() if method else 'POST' if (data or json) else 'GET'
            if _delay is not False:
                logger.debug(f'sleep called {_delay}')
                time.sleep(_delay)
            inst_request = self._session if _use_session and self._session else requests
            #print(f'metendo _make_call {caller} --- {url}')
            headers_incase = CaseInsensitiveDict(headers)
            # if 'host' not in headers_incase:
            #     url_parsed = urllib.parse.urlparse(url)
            #     if url_parsed.hostname:
            #         print(f'update HOST ---- {url_parsed.hostname}')
            #         headers.update({'Host': url_parsed.hostname})
            proxy_use = {}
            if _use_proxy:
                if isinstance(_use_proxy, bool):
                    if _use_proxy is True:
                        proxy_use = self.proxies
                elif isinstance(_use_proxy, dict):
                    proxy_use = _use_proxy
            log_url = url
            prms = kwgs.get('params', {})
            prms_str = '&'.join(f'{k}={v}' for k,v in prms.items())
            log_url += f'?{prms_str}'
            logger.debug(f'{method} [{caller}] {log_url} {proxy_use} -- {_retries}')
            use_timeout = kwgs.pop('timeout', self.timeout)
            temp = inst_request.request(
                method=method, 
                url=url, 
                headers=headers, 
                json=json, 
                data=data, 
                files=files,
                # timeout=self.timeout, 
                timeout=use_timeout,
                proxies=proxy_use,
                verify=self._verify, 
                allow_redirects=_allow_redirect,
                **kwgs
            )
        except requests.exceptions.Timeout as err_timeout1:
            repeat_me = True
            should_raise = expSpecialTimeOut(f'travo - {err_timeout1}')
            logger.error(f'timeout request {err_timeout1}')
        except Exception as err:
            repeat_me = True
            should_raise = expInvalidRequest(f'reqPlus._make_call exp - {err}')
            logger.error(f'reqPlus._make_call exp - {err}')
        else:
            if isinstance(temp, requests.models.Response):
                response = self._add_request(
                    name=caller,
                    response=temp
                )
                if response.status_code not in _auto_retry_status_code:
                    is_ok = True
                    return response
                else:
                    repeat_me = True
        finally:
            if is_ok:
                return response
            if should_raise:
                if _raise_me or not _auto_retry or repeat_me is False:
                    raise should_raise
            if _retries >= _auto_retry_max:
                raise expMaxRetries(response)
            logger.debug(f'[{caller}] going to retry -- reason --> CHINA ---  current try ({_retries})')
            return self._make_call(
                url=url,
                headers=headers,
                data=data,
                json=json,
                files=files,
                method=method,
                _allow_redirect=_allow_redirect,
                _auto_retry=_auto_retry,
                _auto_retry_max=_auto_retry_max,
                _auto_retry_status_code=_auto_retry_status_code,
                _retries=_retries+1,
                _caller=caller,
                _delay=_delay,
                _use_session=_use_session,
                _use_proxy=_use_proxy,
                _raise_me=_raise_me,
                **kwgs
            )
