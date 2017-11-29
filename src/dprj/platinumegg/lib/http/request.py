# -*- coding: utf-8 -*-
import urllib

class HttpRequest:
    """Httpリクエスト.
    """
    
    def __init__(self, django_request):
        self.__django_request = django_request
        
        headers = {}
        headers.update(self.django_request.META)
        if not self.django_request.META.has_key('Authorization'):
            oauthquerys = []
            for k in self.body.keys():
                if k.find('oauth') == 0:
                    oauthquerys.append('%s=%s' % (k, urllib.quote(self.body[k])))
            if 0 < len(oauthquerys):
                headers['Authorization'] = 'OAuth %s' % ','.join(oauthquerys)
        self.__headers = headers
        
        arr = self.host.split(':')
        self.__domain = arr[0]
    
    @property
    def django_request(self):
        return self.__django_request
    
    @property
    def is_secure(self):
        return self.django_request.is_secure()
    
    @property
    def headers(self):
        return self.__headers
    
    @property
    def method(self):
        return self.django_request.method
    
    @property
    def host(self):
        return self.django_request.get_host()
    
    @property
    def domain(self):
        return self.__domain
    
    @property
    def hostname(self):
        return self.headers.get('SERVER_NAME', '')
    
    @property
    def port(self):
        return self.headers.get('SERVER_PORT', '')
    
    @property
    def path(self):
        return self.django_request.path
    
    @property
    def url_head(self):
        return '%s://%s' % ('https' if self.is_secure else 'http', self.host)
    
    @property
    def uri(self):
        return '%s%s' % (self.url_head, self.django_request.get_full_path())
    
    @property
    def url(self):
        return '%s%s' % (self.url_head, self.path)
    
    def get(self, key, d=None):
        return self.body.get(key, d)
    
    @property
    def body(self):
        return self.django_request.REQUEST
    
    @property
    def files(self):
        return self.django_request.FILES
    
    @property
    def query_string(self):
        return self.headers.get('QUERY_STRING', '')
    
    @property
    def useragent(self):
        return self.headers.get('HTTP_USER_AGENT', '')
    
    @property
    def remote_addr(self):
        return self.headers.get('REMOTE_ADDR', '')
    
    @property
    def remote_host(self):
        return self.headers.get('REMOTE_HOST', '')
    
    @property
    def cookies(self):
        return self.django_request.COOKIES
