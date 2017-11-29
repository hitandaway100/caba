# -*- coding: utf-8 -*-
from defines import Defines
from platinumegg.lib.opensocial.util import OSAUtil


class FromPageUtil(object):
    """どこから来たか.
    """
    
    def __init__(self):
        self.__name = None
        self.__args = None
        self.__string = None
    
    @property
    def name(self):
        return self.__name
    
    @property
    def args(self):
        return self.__args
    
    def __getitem__(self, key):
        if key in ('name', 'args'):
            return getattr(self, key)
        else:
            return None
    
    def __str__(self):
        if self.__string is None:
            if self.name:
                arr = [self.name]
                args = self.args
                if args:
                    arr.extend(args)
                self.__string = '__'.join(arr)
            else:
                self.__string = ''
        return self.__string
    
    def get(self, key, default=None):
        return self[key]
    
    def setParams(self, name, value=None):
        if value is not None:
            if isinstance(value, (list, tuple)):
                value = [str(v) for v in value]
            else:
                value = [str(value)]
        self.__name = name
        self.__args = value
        self.__string = None
    
    def setParamsByString(self, s):
        name = None
        value = None
        if s:
            arr = s.split('__')
            if arr and arr[0]:
                name = arr[0]
                if 1 < len(arr):
                    value = arr[1:]
                self.__string = s
        self.__name = name
        self.__args = value
    
    def addQuery(self, url):
        name = self.name
        if name:
            str_from_page = '%s' % self
            return OSAUtil.addQuery(url, Defines.URLQUERY_FROM, str_from_page)
        else:
            return url
