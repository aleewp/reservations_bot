# Std Lib
import datetime as dt
import os
import logging

from retrying import retry
import requests

LOG = logging.getLogger(os.path.splitext(os.path.basename(__file__))[0])


class BaseWrapper(object):

    def __init__(self, should_retry=True, backoff_ratio=5000, max_retries=10):
        '''
        Basic wrapper for sending requests, automatically hand retries, backoff for API calls
        
        Attributes
        -----------
            retry: bool
                If true, retry requests if failed
            backoff_ratio: int
                Base backoff ratio, subsequent retries will be made after sleeping this multiple
            max_retries: int
                The maximum number of times a request should be retried
        '''
        self.should_retry = should_retry
        self.backoff_ratio = backoff_ratio
        self.retries = max_retries
        self.headers = None

    def _retry_handler(self, e):
        '''
        Handler to only retry on specific exceptions. Can be extended by subclasses for more
        specific logic
        '''
        if self.retry_requests:
            return True
        else:
            return False

    def request(self, method:str, url:str,  **kwargs):
        '''
        Essentially a wrapper for request function that adds retry logic, instead of wrapping each call
        
        Parameters
        ----------
        method : str
            the method (ex. get/delete/patch/post)
        url : str
            request url
        '''
        @retry(stop_max_attempt_number=self.retries, wait_exponential_multiplier=self.backoff_ratio,
               retry_on_exception=self._retry_handler)
        def _request():
            headers = kwargs.pop('headers', self.headers)
            r = requests.request(method, url, headers=headers, **kwargs)
            return r
        return _request()

    def get(self, *args, **kwargs):
        '''
        Wrapper for requests.get
        '''
        return self.request('GET', *args, **kwargs)

    def delete(self, *args, **kwargs):
        '''
        Wrapper for requests.delete
        '''
        return self.request('DELETE', *args, **kwargs)

    def patch(self, *args, **kwargs):
        '''
        Wrapper for requests.patch
        '''
        return self.request('PATCH', *args, **kwargs)

    def post(self, *args, **kwargs):
        '''
        Wrapper for requests.post
        '''
        return self.request('POST', *args, **kwargs)

    def put(self, *args, **kwargs):
        '''
        Wrapper for requests.put
        '''
        return self.request('PUT', *args, **kwargs)

    def head(self, *args, **kwargs):
        '''
        Wrapper for requests.head
        '''
        return self.request('HEAD', *args, **kwargs)

    def options(self, *args, **kwargs):
        '''
        Wrapper for requests.options
        '''
        return self.request('OPTIONS', *args, **kwargs)
