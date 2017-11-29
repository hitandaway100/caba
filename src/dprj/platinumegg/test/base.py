# -*- coding: utf-8 -*-
from platinumegg.lib.pljson import Json
from platinumegg.test.dummy_factory import DummyFactory
import sys
from platinumegg.lib.apperror import AppError
from platinumegg.lib.opensocial.util import OSAUtil
import urllib2
from platinumegg.lib.dbg import DbgLogger
import traceback
import settings_sub
from platinumegg.app.cabaret.util.frompage import FromPageUtil
from defines import Defines

class AppTestError(Exception):
    def __init__(self, value=u''):
        self.value = value
    def __str__(self):
        return repr(self.value)
    
class ApiTestBase(object):
    """このクラスを継承してテストを作る.
    >> python manage.py apptest echo
    ↑で実行.
    
    ****** お約束 ******
    ・get_args()をオーバーライドして引数指定する.
    ・初期化時に何かしたかったらsetUp()で.
    
    例：
    def setUp(self):
        self.__unko = randint(0, 93971)
    
    def get_args(self):
        return {
            'unko':self.__unko
        }
    ********************
    
    """
    
    def __init__(self):
        settings_sub.USE_LOCALCACHE = False
        
        self.__api_name = None
        self.response = None
        self.response_result = None
        self.__df = DummyFactory()
        
    def setUp(self):
        """初期化時に何かする.
        ダミーデータ用意したり.
        """
        pass
    def get_urlargs(self):
        """URLでAPIに送る引数.
        """
        return ''
    def get_args(self):
        """APIに送る引数.
        """
        return {}
    def get_query_params(self):
        return {}
    def get_frompagedata(self):
        return None
    
    @classmethod
    def run(cls, API):
        
        logger = DbgLogger()
        result = False
        apitest = None
        try:
            apitest = cls()
            apitest.setUp()
            
            OSAUtil.get_cache_client().flush()   # キャッシュを消しておく.
            
            apitest.__api_name = API
            print 'API name:%s' % API
            
            query_params = {
                '_test' : 1,
                OSAUtil.KEY_APP_ID:'119733',
            }
            query_params.update(apitest.get_query_params())
            frompagedata = apitest.get_frompagedata()
            if frompagedata is not None:
                frompage_name, frompage_params = frompagedata
                frompage = FromPageUtil()
                frompage.setParams(frompage_name, frompage_params)
                query_params[Defines.URLQUERY_FROM] = '%s' % frompage
            
            print 'request query_params:%s' % query_params
            args = apitest.get_args()
            print 'request args:%s' % args
            res = cls.__sendRequest('%s%s' % (API, apitest.get_urlargs()), args, query_params)
            print "response:%s" % res
            if res:
                apitest.response = Json.decode(res)
            else:
                apitest.response = {}
            
            if 'log' in apitest.response:
                print "\nLog:"
                print apitest.response['log']
            
            try:
                apitest.check()
            except AppTestError, e:
                print u'AppTestError: %s' % (e.value)
                print '!!!!!!!!!!!!!! NG !!!!!!!!!!!!!!'
            except Exception, e:
    #            print e
                info = sys.exc_info()
                print AppError.makeErrorTraceString(info)
                print '!!!!!!!!!!!!!! NG !!!!!!!!!!!!!!'
            else:
                print '============== OK =============='
                result = True
            
            apitest.finish()
        except:
            info = sys.exc_info()
            
            t = str(info[0]).replace('<', '').replace('>','')
            ex = '%s:%s' % (t, info[1])
            t_list = traceback.extract_tb(info[2])
            trace = ['%s:%s\r\n- %s' % (t[0], t[1], t[2]) for t in t_list]
            trace.append(ex)
            logger.error('\r\n'.join(trace))
            result = False
        finally:
            if apitest:
                apitest._remove_dummy_all() # 作ったダミーを削除.
            OSAUtil.get_cache_client().flush()   # キャッシュを消しておく.
        return result
    
    def check(self):
        print 'override me!'
    def finish(self):
        # チェック後にやりたいこと.
        pass
    
    def create_dummy(self, dummy_type, *args, **kwgs):
        # ダミーデータ作る.
        return self.__df.create_dummy(dummy_type, *args, **kwgs)
    def _remove_dummy_all(self):
        # ダミーデータ消す.
        self.__df.remove_dummy_all()
    
    @classmethod
    def makeRequestUrl(cls, api):
        return "/sp/%s/" % api
    
    @classmethod
    def __sendRequest(cls, api, args, query_params):
        host = "localhost:8080"
#        host = "ec2-46-51-225-216.ap-northeast-1.compute.amazonaws.com/nmh"
        url = cls.makeRequestUrl(api)
        print 'url:%s' % url
        
        method = "GET"
        data = None
        if args:
            method = "POST"
            for k,v in query_params.items():
                args[k] = v
            # app_idはクエリに付加
            url = OSAUtil.addQuery(url, OSAUtil.KEY_APP_ID, query_params[OSAUtil.KEY_APP_ID])
            if args:
                data = ''
                for k,v in args.items():
                    data = OSAUtil.addQuery(data, k, v)
                data = data[1:]
        else:
            for k,v in query_params.items():
                url = OSAUtil.addQuery(url, k, v)
        
        request_url = "http://" + host + url
        headers = {}
        
        req = urllib2.Request(request_url, data=data, headers=headers)
        req.get_method = lambda: method
        tmp = urllib2.urlopen(req)
        response = tmp.read()
        
        return response
    
    def log(self, logstr, *args):
        if args:
            logstr = logstr % args
        print "[%s]%s" % (self.__api_name, logstr)
