# -*- coding: utf-8 -*-
import os
import sys
import time
import traceback
import threading
from urlparse import urljoin
from django.db import close_connection

import settings_sub
from platinumegg.lib.http.request import HttpRequest
from platinumegg.lib.http.response import HttpResponse
from platinumegg.lib.apperror import AppError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.lib.dbg import DbgLogger

class MainThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.error_response = None
        self.handler = None
        self.is_end = False
    
    @property
    def ret(self):
        if self.handler.response.isEnd:
            return self.handler.response
        else:
            return None
    
    def run(self):
        self.is_end = False
        try:
            handler = self.handler
            django_request = self.handler.request.django_request
            try:
                handler()
            except:
                self.error_response = handler.__class__.makeErrorResponse(django_request)
        finally:
            close_connection()
        self.is_end = True
    
class TimerThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.timeout_time = 5
    
    def run(self):
        time.sleep(self.timeout_time)

class RequestHandler:
    """ ハンドラ.
    """
    
    def __init__(self):
        pass
    
    def initialize(self, request, response):
        """Initializes this request handler with the given Request and Response."""
        self.request = request
        self.response = response
    
    def redirect(self, uri, permanent=False, innor=True):
        """リダイレクト.
        Args:
            permanent    301でリダイレクトするときはTrueを指定.Falseの時は302.デフォルトはFalse.
            innor        相対パス指定の時はTrue.デフォルトはTrue.
        """
        if permanent:
            self.response.set_status(301)
        else:
            self.response.set_status(302)
        if innor:
            absolute_url = urljoin(self.request.uri, uri)
        else:
            absolute_url = uri
        self.response.clear()
        self.response.set_header('Location', str(absolute_url))
        self.response.end()
    
    @classmethod
    def get_default_status(cls):
        """デフォルトで返すHttpStatus.
        """
        return 200
    
    @classmethod
    def get_timeout_time(cls):
        """タイムアウト時間をここで設定[msec].
        0以下のときはタイムアウトをチェックしません.
        """
        return 8
    
    def write_timeout_response(self, response):
        """タイムアウトした時のレスポンス.
        """
        response.send('Timeout!!')
    
    @classmethod
    def run_to_the_end(cls, handler):
        """完了まで走る.
        """
        # メインスレッド.
        t = MainThread()
        t.handler = handler
        t.setDaemon(True)
        t.start()
        interval = 0.05
        while not (t.error_response or t.ret):
            time.sleep(interval)
            interval = 0.1
        return t.error_response or t.ret
    
    @classmethod
    def run_with_timeout(cls, handler):
        """タイムアウト設定あり.
        """
        response = None
        
        # メインスレッド.
        t = MainThread()
        t.handler = handler
        t.setDaemon(True)
        
        # タイムアウトチェック用.
        t2 = TimerThread()
        t2.setDaemon(True)
        t2.timeout_time = cls.get_timeout_time()
        t2.start()
        
        t.start()
        
        interval = 0.05
        while True:
            if not t2.isAlive():
                response =  HttpResponse(status=cls.get_default_status())
                handler.write_timeout_response(response)
                try:
                    body = ''
                    body += 'request_path:<br />%s<br />Query:<br />%s<br /><br />' % (handler.request.path, handler.request.query_string)
                    body += 'trace:<br />Timeout!!<br />%s<br />' % handler.osa_util.logger.to_string(sep='<br />')
                    body += '<br />'
                    body = body.replace('<br />', '\r\n')
                    DbgLogger.write_app_log('%s_error' % settings_sub.APP_NAME, body)
                except:
                    pass
#                now = OSAUtil.get_now()
#                print >> sys.stderr, "Timeout!! time=%s,platform_user_id=%s" % (now.strftime("%Y/%m/%d %H:%M:%S"), handler.osa_util.viewer_id)
                break
            elif t.is_end: 
                if t.ret is not None:
                    response = t.ret
                    break
                elif t.error_response is not None:
                    response = t.error_response
                    break
                else:
                    response =  HttpResponse(status=500)
                    response.end()
            time.sleep(interval)
            interval = 0.1
        return response
    
    @classmethod
    def run(cls, django_request):
        django_response = None
        try:
            handler = cls()
            handler.initialize(HttpRequest(django_request), HttpResponse(status=cls.get_default_status()))
            
            if not settings_sub.IS_LOCAL and (0 < cls.get_timeout_time()):
                response = cls.run_with_timeout(handler)
            else:
                response = cls.run_to_the_end(handler)
            
            if response is None:
                raise AppError("Response is None.")
            django_response = response.to_djangoresponse()
        except:
            django_response = cls.makeErrorResponse(django_request).to_djangoresponse()
            
        return django_response
    
    @classmethod
    def makeErrorResponse(cls, django_request):
        response = HttpResponse(status=cls.get_default_status())
        
        try:
            info = sys.exc_info()
            
            ex = '%s:%s' % (str(info[0]).replace('<', '').replace('>',''), info[1])
            trace_arr = ['%s:%s<br />- %s<br />' % (t[0], t[1], t[2]) for t in traceback.extract_tb(info[2])]
            
            arr = []
            arr.append('trace:<br />%s<br />error:%s' % (''.join(trace_arr), ex))
            arr.append('')
            arr.append('django_request.META: %s<br />' % django_request.META)
            arr.append(OSAUtil.makeRequestInfo(HttpRequest(django_request), sep='<br />'))
            
            body = '<br />'.join(arr).replace('<br />', '\r\n')
            
            response.send(body)
            
            if settings_sub.IS_LOCAL:
                pass
            else:
                try:
                    # ここでException吐くとレスポンス返さなくなっちゃうので.
                    dir_path = settings_sub.ERR_LOG_PATH
                    open(os.path.join(dir_path, 'unknown_error'),'w').write(body)
                except Exception, e:
                    response.clear()
                    response.send(str(e))
        except Exception, e:
            response.clear()
            response.send(str(e))
        
        return response
    
    
