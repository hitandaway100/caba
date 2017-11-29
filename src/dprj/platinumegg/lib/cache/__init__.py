# -*- coding: utf-8 -*-
from importlib import import_module

def _load_backend():
    import settings_sub
    backend = getattr(settings_sub, 'CACHE_BACKEND', 'base')
    mod = import_module('platinumegg.lib.cache.%s' % backend)
    return mod.Client
Client = _load_backend()

def cache_function(func):
    import functools
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        kwargs['cacheclient'] = Client()
        return func(*args, **kwargs)
    return wrapper
