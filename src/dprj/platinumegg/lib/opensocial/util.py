# -*- coding: utf-8 -*-

import datetime
import settings_sub

from platinumegg.lib import timezone, cache
from platinumegg.lib.redis import config
import cgi
import sys
from oauth import oauth
import deploy_info
from platinumegg.lib.dbg import DbgLogger
from platinumegg.lib.apperror import AppError
from importlib import import_module
from platinumegg.lib.thread import ThreadMethod, ThreadResult
import settings
from django.db import connections
from mako.lookup import TemplateLookup
from platinumegg.lib.strutil import StrUtil
from platinumegg.lib.pljson import Json
from random import randint
import platinumegg
import os
import urllib2
import httplib
import time
from platinumegg.lib.compression import to62Decimal
from mako import exceptions
import socket
import random
from platinumegg.lib.opensocial.useragent import BrowserType
from platinumegg.lib.opensocial.useragent import UserAgent
from StringIO import StringIO

g_osa_util_import_time = datetime.datetime.now(timezone.UTC())
g_default_encoding = None
g_now_diff = 0

def set_default_encoding(enc = 'utf-8'):
    """defaultencoding を 変更します. 参考URL: http://blog.livedoor.jp/matssaku/archives/50525168.html
    ローカルで試したところ、この処理には3秒くらいかかる.
    1回呼び出したら、その設定を使いまわす感じで...
    """
    global g_default_encoding
    if g_default_encoding == enc:
        return
    stdin = sys.stdin
    stdout = sys.stdout
    reload(sys)
    getattr(sys, 'setdefaultencoding')(enc)
    sys.stdin = stdin
    sys.stdout = stdout
    g_default_encoding = enc
set_default_encoding()

def set_local_now_diff(delta):
    global g_now_diff
    g_now_diff = delta
    return delta

class OSAUtil:
    """アプリ内の共通処理をまとめたクラス.
    """
    KEY_VIEWER_ID = 'opensocial_viewer_id'
    KEY_OWNER_ID = 'opensocial_owner_id'
    KEY_APP_ID = 'opensocial_app_id'
    
    URL_QUERY_SIGNED = 'signed'
    
    SUPPORT_BROWSER = (
        BrowserType.IPHONE,
#        BrowserType.IPAD,
#        BrowserType.IPOD,
        BrowserType.ANDROID,
#        BrowserType.INTERNETEXPROLER,
#        BrowserType.INTERNETEXPROLER_11_OVER,
#        BrowserType.FIREFOX,
#        BrowserType.CHROME,
#        BrowserType.OPERA,
#        BrowserType.SAFARI,
    )
    PC_SUPPORT_BROWSER = (
        BrowserType.IPHONE,
        BrowserType.IPAD,
        BrowserType.IPOD,
        BrowserType.ANDROID,
        BrowserType.INTERNETEXPROLER,
        BrowserType.INTERNETEXPROLER_11_OVER,
        BrowserType.FIREFOX,
        BrowserType.CHROME,
#        BrowserType.OPERA,
        BrowserType.SAFARI,
    )
    
    @property
    def handler(self):
        return self.__handler
    @property
    def request(self):
        return self.handler.request
    @property
    def response(self):
        return self.handler.response
    @property
    def logger(self):
        return self.__logger
    
    def __init__(self, handler, appparam, is_pc=False):
        self.__handler = handler
        self.appparam = appparam
        self.__is_pc = is_pc
        
        self.__logger = DbgLogger()
        self.init_time = OSAUtil.get_now(timezone.TZ_DB)
        
        self.oauth_token = None
        self.bearer_token = None
        
        if settings_sub.IS_BENCH:
            # 負荷テスト中は適当なユーザー選択.
            self.owner_id = OSAUtil.makeBenchUserID()
        else:
            self.owner_id = self.request.get(OSAUtil.KEY_OWNER_ID, '')
        
        self.viewer_id = str(self.request.get(OSAUtil.KEY_VIEWER_ID, self.owner_id))
        
        if handler.is_pc:
            self.useragent = UserAgent.make(self.request.useragent, OSAUtil.PC_SUPPORT_BROWSER)
        else:
            self.useragent = UserAgent.make(self.request.useragent, OSAUtil.SUPPORT_BROWSER)
        
        if self.useragent and settings_sub.IS_DEV:
            self.logger.trace('useragent:is_smartphone:%s' % self.useragent.is_smartphone())
            self.logger.trace('useragent:is_pc:%s' % self.useragent.is_pc())
            self.logger.trace('useragent:is_ios:%s' % self.useragent.is_ios())
            self.logger.trace('useragent:is_android:%s' % self.useragent.is_android())
            self.logger.trace('useragent:os:%s(ver:%s)' % (self.useragent.browser, self.useragent.version or 'x.x.x'))
        
        self.is_new_session = False
        if settings_sub.IS_BENCH:
            self.session = "DSession:%s" % self.viewer_id
            self.is_direct_access = True
            self.is_admin_access = self.session is None
            self.is_dbg_user = True
            self.is_dbg = settings_sub.IS_LOCAL
        else:
            self.session = self.__checkSession()
            self.is_direct_access = not self.request.django_request.META.has_key('Authorization')
            self.is_admin_access = self.session is None
            
            self.is_dbg_user = True
            if settings_sub.IS_LOCAL:
                pass
            elif self.request.remote_addr in self.appparam.developer_ip:
                pass
            elif self.viewer_id in self.appparam.developer_id:
                pass
            else:
                self.is_dbg_user = False
            self.is_dbg = settings_sub.IS_DEV and self.is_dbg_user
        
        self.tasks = {}
        self.write_enc = 'utf-8'
        
        self.cls_platform_api = None
        
        self.oauth_request = None
        self.auth_token_args = None
        self.consumer = oauth.OAuthConsumer(self.appparam.consumer_key, self.appparam.consumer_secret)
        
        self.__initPlatform()
    
    def deleteSession(self):
        client = OSAUtil.get_cache_client()
        key = '%s##%s' % (self.viewer_id, self.session)
        client.delete(key)
    
    def __checkSession(self):
        """リクエストヘッダのAuthorizationを探す.
        あったら:
            セッションを発行
            セッションをキーにして
                oauthを保存.
            cookieにセッションを設定.
        無かったら
            cookieからセッションを取得.
            保存してあるoauthを取得.
        """
        session = None
        self.auth_token_args = None
        try:
            client = OSAUtil.get_session_client()
            pre_session = client.get(self.viewer_id, namespace='session')
            
            prefix = None
            if self.__is_pc:
                req_session = self.request.get('_session')
                prefix = 'pc'
            else:
                req_session = self.request.cookies.get('session')
                prefix = 'sp'
            
            if pre_session and prefix != pre_session[:len(prefix)]:
                pre_session = None
            
            if self.request.headers.has_key('Authorization'):
                if pre_session:
                    if pre_session == req_session:
                        session = req_session
                    else:
                        client.delete('%s##%s' % (self.viewer_id, pre_session))
                
                if session is None:
                    session = '%s%s' % (prefix, OSAUtil.makeSessionID())
                    self.logger.trace('new session! %s' % session)
                    self.is_new_session = True
                
                key = '%s##%s' % (self.viewer_id, session)
                
                self.response.set_cookie('session', session, domain=self.request.domain)
                client.set(self.viewer_id, session, namespace='session')
                
                oauth_request = oauth.OAuthRequest.from_request(
                    self.request.method,
                    self.request.url,
                    headers = self.request.django_request.META,
                    query_string = self.request.query_string
                )
                self.oauth_request = oauth_request
                if oauth_request.parameters.has_key('oauth_token'):
                    self.auth_token_args = {
                        'oauth_token' : oauth_request.get_parameter('oauth_token'),
                        'oauth_token_secret' : oauth_request.get_parameter('oauth_token_secret'),
                    }
                    client.set(key, self.auth_token_args)
                elif not self.__is_pc:
                    return None
            else:
                if not req_session or req_session != pre_session:
                    self.logger.trace('session is None.')
                    return None
                key = '%s##%s' % (self.viewer_id, req_session)
                self.auth_token_args = client.get(key)
                if not self.auth_token_args:
                    self.logger.trace('authorize is None.')
                    if not self.__is_pc:
                        return None
                client.ttl(key)
                session = req_session
            if self.auth_token_args:
                self.logger.trace('auth_token_args=%s' % str(self.auth_token_args))
                self.oauth_token = oauth.OAuthToken(
                    self.auth_token_args['oauth_token'],
                    self.auth_token_args['oauth_token_secret'],
                )
        except:
            session = None
            raise
        
        return session
    
    def __initPlatform(self):
        """プラットフォームの準備.
        """
        platform_type = self.appparam.platform_type
        packagename = 'platinumegg.lib.platform.%s' % platform_type
        self.cls_platform_api = import_module('%s.api' % packagename).ApiRequestMaker
        self.mod_platform_link = import_module('%s.links' % packagename).Links
    
    def __getRequestInfo(self, sep='\n'):
        """ リクエスト情報をいろいろ文字列として取得.デバッグ用
        """
        if not self.is_dbg_user:
            return ''
        
        return OSAUtil.makeRequestInfo(self.request, sep, self.init_time)
    
    @staticmethod
    def makeRequestInfo(request, sep='\n', init_time=None):
        """ リクエスト情報をいろいろ文字列として取得.デバッグ用
        """
        init_time = init_time or OSAUtil.get_now()
        logs = [
            'deploy_info.USERNAME:%s' % deploy_info.USERNAME,
            'deploy_info.TIME:%s' % deploy_info.TIME,
            'request time: %s' % init_time.astimezone(timezone.TZ_DEFAULT),
            'remote_addr:%s' % request.remote_addr,
            'method:%s uri:%s' % (request.method, request.uri),
        ]
        
        # header:
        logs.append('request headers:')
        logs.extend(['\t%s: %s' % (k,v) for k,v in request.headers.items()])
        
        # query.
        logs.append('request querys:')
        logs.extend(['\t%s: %s' % (k,v) for k,v in request.body.items()])
        
        # cookie.
        logs.append('request cookies:')
        logs.extend(['\t%s: %s' % (k,v) for k,v in request.cookies.items()])
        
        return sep.join(logs)
    
    def getElpsedTime(self):
        """ リクエスト受付からの経過時間を返す(deltatime)
        """
        end_time = OSAUtil.get_now(timezone.TZ_DB)
        delta = end_time - self.init_time
        return delta
    
    def checkOAuth(self):
        """OAuthチェック.
        """
        request = self.request
        authorization = 'null'
        http_url = request.url
        
        if self.oauth_request:
            try:
                authorization = request.headers['Authorization']
                self.logger.trace('oauth_request:%s' % self.oauth_request.to_url())
                
                sig = self.oauth_request.get_parameter('oauth_signature')
                sig_build = oauth.OAuthSignatureMethod_HMAC_SHA1().build_signature(self.oauth_request, self.consumer, self.oauth_token)
                
                self.logger.trace('sig      :%s' % sig)
                self.logger.trace('sig_build:%s' % sig_build)
                if sig == sig_build:
                    self.logger.trace('sig_check_ok?:True')
                else:
                    self.logger.trace('sig_check_ok?:False')
                    raise oauth.OAuthError('sig check error!!')
            except:
                self.deleteSession()
                raise
            
        self.logger.trace('http_url:' + http_url)
        self.logger.trace('authorization:' + authorization)
    
    def checkUser(self):
        """ユーザチェック.
        """
        if self.is_admin_access and (not self.is_dbg_user):
            raise AppError('permission error. remote_addr:%s' % self.request.remote_addr)
        self.logger.trace(self.__getRequestInfo())
        self.logger.trace('is_direct_access:%s' % self.is_direct_access)
        self.logger.trace('is_admin_access:%s' % self.is_admin_access)
        self.logger.trace('is_dbg:%s' % self.is_dbg)
        self.logger.trace('is_dbg_user:%s' % self.is_dbg_user)
        self.logger.trace('viewer_id:%s' % self.viewer_id)
    
    #=======================================================================
    # platform API.
    def httpopen(self, uri, body, http_method, headers, key_file=None, timeout=None):
        """ HTTPメソッド(GET, POST)を指定して http通信
        """
        is_ssl = uri.find('https://') == 0
        
        req = urllib2.Request(uri, body, headers)
        req.get_method = lambda: http_method
        
        self.logger.trace('selector:%s' % req.get_selector())
        
        timeout = timeout or socket._GLOBAL_DEFAULT_TIMEOUT
        if is_ssl:
            connection = httplib.HTTPSConnection(req.get_host(), key_file=key_file, timeout=timeout)
        else:
            connection = httplib.HTTPConnection(req.get_host(), timeout=timeout)
        connection.request(http_method, req.get_selector(), body, headers)
        response = connection.getresponse()
        
        self.logger.trace('httpopen status:%s' % response.status)
        self.logger.trace('httpopen headers:%s' % response.getheaders())
        
        if not response.status in (200,201,202):
            connection.close()
            raise urllib2.HTTPError(uri, response.status, response.reason, response.getheaders(), None)
        
        response_body = response.read()
        try:
            self.logger.trace('httpopen response_body:%s' % response_body)
        except UnicodeDecodeError:
            self.logger.trace('httpopen response_body:binary..')
            pass
        stream = StringIO(response_body)
        connection.close()
        
        return stream
    
    def addApiRequest(self, key, api_request):
        """APIリクエストを実行して追加.
        """
        if api_request is None:
            return
        elif key is not None:
            self.tasks[key] = api_request
        api_request.start()
    
    def makeApiRequest(self, apiname, requestdata):
        """Apiリクエスト作成.
        """
        return self.cls_platform_api.makeApiRequest(apiname, self, requestdata)
    
    def addThreadMethod(self, key, method, *args, **kwargs):
        """ 指定メソッドを別スレッドで実行する.
        メソッドの実行結果を知らなくてよい場合は key に None を入れる.
        """
        self.addApiRequest(key, ThreadMethod(method, *args, **kwargs))
    
    def getThreadResult(self):
        dest = {}
        for key, task in self.tasks.iteritems():
            task.join()
            dest[key] = ThreadResult(task.result, task.error)
        self.tasks = {}
        return dest
    
    #=======================================================================
    # make url.
    def __insertDefaultQuery(self, src):
        dest = src
        if self.is_direct_access:
            dest = OSAUtil.addQuery(dest, OSAUtil.KEY_APP_ID, self.appparam.app_id)
            dest = OSAUtil.addQuery(dest, OSAUtil.KEY_OWNER_ID, self.viewer_id)
        return dest
    
    def makeLinkUrl(self, url, do_quote=True):
        """ページ遷移用url.
        """
        url = self.__insertDefaultQuery(url)
        return self.mod_platform_link.makeLinkUrl(self, url, do_quote)
    
    def makeLinkUrlActivity(self, callback_url):
        """アクティビティ送信用url.
        """
        callback_url = self.__insertDefaultQuery(callback_url)
        return self.mod_platform_link.makeLinkUrlActivity(self, callback_url)
    
    def makeLinkUrlInvite(self, callback_url, body):
        """招待ページurl.
        """
        callback_url = self.__insertDefaultQuery(callback_url)
        return self.mod_platform_link.makeLinkUrlInvite(self, callback_url, body)
    
    def makeLinkUrlDiary(self, callback_url=None, subject=None, body=None, image_url=None):
        """日記投稿用URL.
        """
        callback_url = self.__insertDefaultQuery(callback_url)
        return self.mod_platform_link.makeLinkUrlDiary(self, callback_url, subject, body, image_url)
    
    def makeLinkUrlLocation(self, callback_url, location_type='cell'):
        """位置情報取得用URL.
        """
        callback_url = self.__insertDefaultQuery(callback_url)
        return self.mod_platform_link.makeLinkUrlLocation(self, callback_url, location_type)
    
    def makeLinkUrlAbsolute(self, url):
        """ 絶対パスでURLを作る.
        """
        url = self.__insertDefaultQuery(url)
        return self.mod_platform_link.makeLinkUrlAbsolute(self, url)
    
    def makeLinkUrlRedirect(self, src):
        """ リダイレクト用URLの作成.
        """
        src = self.__insertDefaultQuery(src)
        return self.mod_platform_link.makeLinkUrlRedirect(self, src)
    
    def makeLinkUrlBinary(self, src, do_quote=False):
        """リンク先がバイナリデータ(flash,画像等)のURL
        """
        src = self.__insertDefaultQuery(src)
        return self.mod_platform_link.makeLinkUrlBinary(self, src, do_quote)
    
    def makeLinkUrlSwfEmbed(self, src):
        """ページ内埋め込みFlashのURL.
        """
        src = self.__insertDefaultQuery(src)
        return self.mod_platform_link.makeLinkUrlSwfEmbed(self, src)
    
    #=======================================================================
    # output.
    template_dir = os.path.join(os.path.dirname(platinumegg.__file__), 'app/%s/templates' % settings_sub.APP_NAME)
    template_lockup = TemplateLookup(directories=[template_dir], output_encoding='utf-8', input_encoding='utf-8', encoding_errors='replace')
    
    def get_outputhtml(self, filename, template_values, quiet=True):
        """ filename は templates ディレクトリからの相対パスになります.
        """
#        content_type = 'application/xhtml+xml'
        content_type = 'text/html'
        template_values['encode'] = self.write_enc
        #
        if self.is_dbg:
            try:
                dbnames = [settings.DB_DEFAULT, settings.DB_READONLY]
                for name in dbnames:
                    self.logger.trace('querys:%s' % name)
                    querys = connections[name].__getattribute__('queries')
                    for query in querys:
                        sql = query['sql']
                        if name == settings.DB_READONLY and (sql.find('UPDATE') == 0 or sql.find('INSERT') == 0):
                            self.logger.error('cant update db=%s sql=%s' % (name, sql))
                        self.logger.trace('  time:%s query:%s' % (query['time'], sql))
            except:
                pass
        #
        delta = self.getElpsedTime()
        self.logger.trace('elapsed time: %d.%06d sec.' % (delta.seconds, delta.microseconds)) # osa_util を init してからの経過時間.
        end_time = OSAUtil.get_now(timezone.TZ_DB)
        delta = end_time - g_osa_util_import_time
        self.logger.trace('elapsed time(import): %d.%06d sec.' % (delta.seconds, delta.microseconds)) # osa_util.py を import してからの経過時間.
        
        if self.is_dbg:
            log = OSAUtil.htmlEncode(self.logger.to_string())
            log = log.replace('\n', '___BR___')
            if settings_sub.IS_LOCAL:
                template_values['dbg_print_log'] = '<span style="font-size: x-small;">' + OSAUtil.htmlEncode(log).replace('___BR___', '<br />') + '</span>'
            else:
                template_values['dbg_print_log'] = OSAUtil.htmlEncode(log).replace('___BR___', '\n')
        
        self.response.set_header('Content-Type', content_type + '; charset=' + self.write_enc)
        try:
            template = OSAUtil.template_lockup.get_template(filename)
            return template.render_unicode(**template_values).encode(self.write_enc, 'replace'), content_type
        except:
            if not quiet:
                self.logger.write_error(exceptions.text_error_template().render_unicode().encode(self.write_enc, 'replace'))
                raise
            elif settings_sub.IS_DEV:
                return exceptions.text_error_template().render_unicode().encode(self.write_enc, 'replace'), content_type
            else:
                return None, None
    
    def write_html(self, filename, template_values, quiet=True):
        """ html書き込み.
        """
        html, _ = self.get_outputhtml(filename, template_values, quiet=quiet)
        if html is not None:
            self.response.send(html)
        else:
            self.response.set_status(500)
            self.response.end()
    
    def write_swf(self, swfdata, nocache=False):
        """ swfのﾊﾞｲﾅﾘデータを出力するだけ.
        """
        if settings_sub.IS_LOCAL and self.request.get('_sql') == '1':
            # sql が見たいんです！
            raise AppError('sql disp mode')
        
        if nocache:
            self.response.set_header('Expires', 'Thu, 01 Jan 1970 00:00:00 GMT, -1')
            self.response.set_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.response.set_header('Pragma', 'no-cache')
        self.response.set_header('Content-Type', 'application/x-shockwave-flash')
        self.response.send(swfdata)
    
    def write_simple_swf(self, filename, nocache):
        """ バイナリ操作とかせずに、ただのFlashファイルを書き出すだけ.
        """
        f = open(filename, 'rb')
        swfData = f.read()
        f.close()
        self.write_swf(swfData, nocache)
    
    GIF_1X1_TRANSPARENT_DATA = (
          "\x47\x49\x46\x38\x39\x61\x01"
        + "\x00\x01\x00\x80\xff\x00\xff\xff\xff\x00\x00\x00\x21\xf9"
        + "\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01"
        + "\x00\x00\x02\x02\x44\x01\x00\x3b"
    )
    def write_gif_data(self, data=None):
        """ gif画像.
        """
        if data is None:
            data = OSAUtil.GIF_1X1_TRANSPARENT_DATA
        
        nocache = False
        if nocache:
            self.response.set_header('Expires', 'Thu, 01 Jan 1970 00:00:00 GMT, -1')
            self.response.set_header('Cache-Control', 'private, no-cache=Set-Cookie, no-cache, no-store, proxy-revalidate')
            self.response.set_header('Pragma', 'no-cache')
        self.response.set_header('Content-Type', 'image/gif')
        self.response.send(data)
    
    def write_jpeg_data(self, data):
        """JPEG画像
        """
        nocache = False
        if nocache:
            self.response.set_header('Expires', 'Thu, 01 Jan 1970 00:00:00 GMT, -1')
            self.response.set_header('Cache-Control', 'private, no-cache=Set-Cookie, no-cache, no-store, proxy-revalidate')
            self.response.set_header('Pragma', 'no-cache')
        self.response.set_header('Content-Type', 'image/jpeg')
        self.response.send(data)
        
    def write_png_data(self, data):
        """PNG画像
        """
        nocache = False
        if nocache:
            self.response.set_header('Expires', 'Thu, 01 Jan 1970 00:00:00 GMT, -1')
            self.response.set_header('Cache-Control', 'private, no-cache=Set-Cookie, no-cache, no-store, proxy-revalidate')
            self.response.set_header('Pragma', 'no-cache')
        self.response.set_header('Content-Type', 'image/png')
        self.response.send(data)
    
    def write_json_data(self, json_data, filename=None):
        """json
        """
        self.response.set_header('Content-Type', 'application/json; charset=utf-8')
        if filename is not None:
            self.response.set_header('Content-Disposition', "attachment; filename=" + filename)
        self.response.send(json_data)
    
    def write_json_obj(self, json_obj, filename=None):
        """json.
        """
        json_data = StrUtil.to_s(Json.encode(json_obj))
#        json_data = json_data.replace(': ', ':').replace(', ', ',')
#        json_data = json_data.replace('\\r', '')
        self.write_json_data(json_data, filename=None)
    
    def write_csv_data(self, csv_data, filename=None):
        """csv
        """
        self.response.set_header('Content-Type', 'text/csv')
        if filename is not None:
            self.response.set_header('Content-Disposition', "attachment; filename=" + filename)
        self.response.send(csv_data)
    
    def write_zip(self, zipdata, fileName, nocache=False):
        """ zipのﾊﾞｲﾅﾘデータを出力するだけ.
        """
        self.response.set_header('Content-Type', 'application/zip')
        self.response.set_header('Content-Disposition', "attachment; filename=" + fileName + ".zip")
        self.response.send(zipdata)
    
    #=======================================================================
    # utility.
    @staticmethod
    def htmlEncode(text):
        """ HTML上に書き出すときの変換.
        """
        return cgi.escape(text)
    
    @staticmethod
    def addQuery(url, param, value):
        """ url にクエリを1つ付け足す.
        """
        if -1 != url.find('&') or -1 != url.find('?'):
            dest = "%s&%s=%s" % (url, param, value)
        else:
            dest = "%s?%s=%s" % (url, param, value)
        return dest
    
    @staticmethod
    def addSigned(url):
        """ gifやswfのリクエスト時に opensocial_owner_id とかを付与して欲しい場合に使う.
        """
        dest = OSAUtil.addQuery(url, OSAUtil.URL_QUERY_SIGNED, 1)
        return dest
    
    @staticmethod
    def addAnchor(url, anchor):
        """ 最後に#anchorを足す.
        """
        return '%s#%s' % (url, anchor)
        
    @staticmethod
    def get_cache_client():
        """ cache.Client インスタンスを返す.
        """
        return cache.Client()
    
    @staticmethod
    def get_session_client():
        """ cache.Client インスタンスを返す.
        """
        return cache.Client(config.REDIS_SESSION)
    
    @staticmethod
    def get_now_diff():
        if not settings_sub.IS_DEV:
            return 0
        client = OSAUtil.get_cache_client()
        delta = client.get('now_diff', namespace='OSAUtil')
        if delta:
            delta = int(delta)
        else:
            delta = 0
        return set_local_now_diff(delta)
    
    @staticmethod
    def set_now_diff(delta):
        """ get_now で得られる現在時間に加える誤差の設定
        """
        client = OSAUtil.get_cache_client()
        client.set('now_diff', delta, namespace='OSAUtil')
        return set_local_now_diff(delta)
        
    @staticmethod
    def get_now(tzinfo=None):
        """tz情報付き現在時間を得る.
        """
        if tzinfo is None:
            tzinfo = timezone.TZ_DEFAULT
        return datetime.datetime.now(tzinfo) + datetime.timedelta(seconds=OSAUtil.get_now_diff())
    
    __datetimemin = datetime.datetime.strptime('19010101', '%Y%m%d')
    __datetimemax = datetime.datetime.strptime('40951231', '%Y%m%d')
    
    @staticmethod
    def get_datetime_max():
        """tz情報付きdatetime.max
        """
        return OSAUtil.__datetimemax.replace(tzinfo=timezone.TZ_DB).astimezone(timezone.TZ_DEFAULT)
    
    @staticmethod
    def get_datetime_min():
        """tz情報付きdatetime.min
        """
        return OSAUtil.__datetimemin.replace(tzinfo=timezone.TZ_DB).astimezone(timezone.TZ_DEFAULT)
    
    random.seed(socket.gethostname())
    
    @staticmethod
    def makeSessionID():
        # 適当なセッションID発行.
        int_dt = int(time.time()) % 0xffffffff
        right = randint(1,0xffffffff)
        int_id = (int_dt << 32) + right
        return to62Decimal(int_id)
    
    @staticmethod
    def makeRandomHexString(length=32):
        # 適当な16進文字列発行.
        int_dt = int(time.time()) % 0xffff
        arr = []
        for _ in xrange(length):
            v = (randint(0, 65535) * 31) + int_dt * 23
            int_dt = v % 0xffff
            arr.append('%x' % (int_dt % 0xf))
        return ''.join(arr)
    
    # ================================================================================================
    # 負荷テストの時だけ使う.
    BENCH_USER_ID_START = 10000000
    if settings_sub.IS_LOCAL:
        BENCH_USER_ID_NUM = 250
    else:
        BENCH_USER_ID_NUM = 100000
    @staticmethod
    def makeBenchUserID():
        # 負荷テスト用のダミーユーザーのIDを作る.
        return OSAUtil.BENCH_USER_ID_START + randint(0, OSAUtil.BENCH_USER_ID_NUM - 1)
    
