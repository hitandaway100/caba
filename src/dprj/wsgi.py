# -*- coding: utf-8 -*-
import os, sys
try:
    sys.path.append(os.path.dirname(__file__))
    sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
    os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
    import django.core.handlers.wsgi
except:
    sys.excepthook(*(sys.exc_info()))
    raise
    
def application(environ, start_response):
    django_application = django.core.handlers.wsgi.WSGIHandler()
    return django_application(environ, start_response)
