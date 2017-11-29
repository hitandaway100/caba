# -*- coding: utf-8 -*-

from django.http.response import HttpResponse as DjangoHttpResponse,\
    HttpResponsePermanentRedirect, HttpResponseRedirect


class HttpResponse:
    """Httpレスポンス.
    """
    
    def __init__(self, body=None, status=200):
        self.__status = status
        self.__headers = {}
        self.__end = False
        self.__cookies = {}
        self.clear()
        if body:
            self.write(body)
    
    @property
    def status(self):
        return self.__status
    @property
    def isEnd(self):
        return self.__end
    
    def set_status(self, status):
        """ステータスを設定.
        """
        self.__status = status
    
    def write(self, body):
        """Bodyを書き込む.
        """
        self.__body += body
    
    def end(self):
        """Bodyを書き込む.
        """
        if self.isEnd:
            raise "The response of the end already."
        self.__end = True
    
    def send(self, body=None):
        """Bodyを書き込む.
        """
        if body:
            self.write(body)
        self.end()
    
    def clear(self):
        self.__body = ''
        self.__end = False
    
    def set_header(self, name, value):
        """ヘッダを設定.
        """
        self.__headers[name.lower()] = value
    
    def set_cookie(self, name, value, expires=None, domain=None):
        """クッキーを設定.
        """
        self.__cookies[name.lower()] = (value, expires, domain)
    
    def remove_header(self, name):
        """ヘッダを削除.
        """
        key = name.lower()
        if self.__headers.has_key(key):
            del self.__headers[key]
    
    def to_djangoresponse(self):
        """django用のレスポンス.
        """
        content_type = self.__headers.get('content-type', 'text/plain')
        self.set_header('content-length', str(len(self.__body)))
        django_response = DjangoHttpResponse(self.__body, content_type=content_type, status=self.status)
        for k, v in self.__headers.items():
            django_response[k] = v
        if self.status == 301:
            django_response = HttpResponsePermanentRedirect(django_response.get('location'))
        elif self.status == 302:
            django_response = HttpResponseRedirect(django_response.get('location'))
        for k, arr in self.__cookies.items():
            v, expires, domain = arr
            django_response.set_cookie(k, v, expires=expires, domain=domain)
        return django_response
