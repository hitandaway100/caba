# -*- coding: utf-8 -*-
from importlib import import_module
from platinumegg.lib.apperror import AppError

class AppParam:
    
    platform_type = None
    app_id = None
    consumer_key = ''
    consumer_secret = ''
    developer_ip = []
    developer_id = []
    sandbox = False
    
    URL_API_REST = ''
    URL_API_BANK = ''
    URL_API_OAUTH = ''
    URL_STATIC = ''
    URL_CACHE = ''
    
    @staticmethod
    def create(platformtype, app_id):
        
        try:
            config = import_module('platinumegg.lib.platform.%s.config' % platformtype)
            urls = import_module('platinumegg.lib.platform.%s.urls' % platformtype)
        except ImportError:
            raise AppError(u'このプラットフォームﾘは認められません:%s' % platformtype)
        
        params = config.applications.get(app_id, None)
        if params is None:
            raise AppError(u'このｱﾌﾟﾘは認められません:%s' % app_id)
        
        ins = AppParam()
        ins.platform_type = platformtype
        ins.app_id = app_id
        
        for k,v in params.items():
            setattr(ins, k, v)
        
        keys = (
            'URL_API_REST',
            'URL_API_BANK',
            'URL_API_OAUTH',
            'URL_STATIC',
            'URL_CACHE',
        )
        if ins.sandbox:
            formatstr = '%s_SANDBOX'
        else:
            formatstr = '%s_RELEASE'
        for key in keys:
            setattr(ins, key, getattr(urls, formatstr % key, ''))
        
        return ins
