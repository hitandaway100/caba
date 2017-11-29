# -*- coding: utf-8 -*-

from platinumegg.lib.requesthandler import RequestHandler
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.lib.platform.parameter import AppParam
import os
import settings_sub
from platinumegg.lib.platform.types import PlatformType
from platinumegg.lib.apperror import AppError
from platinumegg.lib.url_args import UrlArgs
from platinumegg.lib.plcrypto import PLCrypto
import urllib
from platinumegg.lib.pljson import Json
import sys
import traceback
from platinumegg.lib.strutil import StrUtil
from sqlalchemy.exc import TimeoutError
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from defines import Defines
import time
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.url_maker import UrlMaker
import zlib
import binascii
from platinumegg.lib.cache.localcache import localcache
import settings_sub_props
from settings_sub_props import EnvironmentType
from platinumegg.lib.dbg import DbgLogger
import socket
from urlparse import urlparse
from platinumegg.lib.opensocial.useragent import BrowserType
from platinumegg.app.cabaret.util.apprandom import AppRandom
from platinumegg.app.cabaret.util.frompage import FromPageUtil


class BaseHandler(RequestHandler):
    
    def __init__(self):
        localcache.initCache()
        
        self.osa_util = None
        self.html_param = {}
        self.json_param = {}
        self.json_param[Defines.STATUS_KEY_NAME] = CabaretError.Code.OK
        self.json_param['result'] = {}
        self.json_result_param = self.json_param['result']
        self._api_works = {}   # APIをまとめて呼ぶために使う.
        self.appparam = None
        self.url_cgi = None
        self.__json_args = None
        self.is_pc = False
        self.is_admin = False
        self.is_rel = False
        self.__from_page = None
        self.__model_mgr = ModelRequestMgr(loginfo=self.addloginfo)
        self.__logtime = OSAUtil.get_now()
    
    @staticmethod
    def getPath(filename):
        """使用例: self.getPath('html/base.html')
        """
        return os.path.join(os.path.dirname(__file__), filename)
    
    def get_templates_folder(self):
        # 使用するテンプレートフォルダ.
        return u''
    
    def __setStaticParam(self):
        """静的ﾊﾟﾗﾒｰﾀの定義.
        """
        hostname = self.request.host
        
        urlprefix = ''
        platformtype = None
        
        _app_id = None
        
        url_media = None
        url_static = None
        
        if hostname in ('localhost:8080', '127.0.0.1:8080') or hostname.find('192.168.1.') == 0:    # ローカル環境.
            platformtype = settings_sub.LOCAL_PLATFORM
            _app_id = self.request.get(OSAUtil.KEY_APP_ID) or '127799'
        elif hostname in ('211.130.152.227'):    # 開発環境.
            urlprefix = '/%s' % settings_sub.APP_NAME
            _app_id = '127799'
        elif hostname in ('211.130.152.246',):    # PC申請環境.
            platformtype = PlatformType.DMMPC
            urlprefix = '/%s' % settings_sub.APP_NAME
            _app_id = '635899'
        elif hostname in ('211.11.100.166','10.116.41.12','10.116.41.13'):    # ステージング.
            urlprefix = '/%s' % settings_sub.APP_NAME
            _app_id = '297627'
        elif hostname in ('211.11.100.164','caba-king.jp','211.130.152.246') or hostname.find('10.116.41.') == 0 or hostname.find('vm44aa') == 0:    # 本番.
            urlprefix = '/%s' % settings_sub.APP_NAME
            _app_id = '340004'
        elif hostname in ('211.130.152.226',):    # 本番管理ツール.
            urlprefix = '/%s' % settings_sub.APP_NAME
            _app_id = '340004'
        elif settings_sub.IS_LOCAL:     # ローカル環境で実機確認する用.
            if hostname == ('%s:8080' % socket.gethostbyname(settings_sub.SERVER_HOSTNAME)):
                platformtype = settings_sub.LOCAL_PLATFORM
                _app_id = '119733'
                url_media = settings_sub.MEDIA_URL_ROOT.replace('127.0.0.1:8080', hostname)
                url_static = settings_sub.STATIC_URL_ROOT.replace('127.0.0.1:8080', hostname)
            else:
                raise CabaretError('%s illegal case (%s)' % ('hostname', hostname))
        else:
            if hostname == 'localhost:3128':
                # 踏み台サーバを使用.
                local_hostname = settings_sub.SERVER_HOSTNAME
                if local_hostname in ('vm44aa1012',):
                    # ステージング.
                    urlprefix = '/%s' % settings_sub.APP_NAME
                    _app_id = '297627'
                elif local_hostname.find('vm44aa10') == 0:
                    # 本番.
                    urlprefix = '/%s' % settings_sub.APP_NAME
                    _app_id = '340004'
                elif socket.gethostbyname(local_hostname) in ('10.166.6.134', '10.153.3.160'):
                    urlprefix = '/%s' % settings_sub.APP_NAME
                    _app_id = '127799'
                else:
                    raise CabaretError('server illegal case..')
            else:
                raise CabaretError('%s illegal case (%s)' % ('hostname', hostname))
        
        self.url_cgi = u'%s%s' % (self.request.url_head, urlprefix)
        self.url_media = url_media or settings_sub.MEDIA_URL_ROOT
        self.url_static = url_static or settings_sub.STATIC_URL_ROOT
        self.url_static_img = '%simg/' % self.url_static
        self.url_static_js = '%sjs/' % self.url_static
        self.url_static_css = '%scss/' % self.url_static
        self.url_static_effect = '%seffect/' % self.url_static
        
        urldata = urlparse(self.url_static)
        self.url_static_cgi = '%s://%s%s' % (urldata.scheme, urldata.netloc, urlprefix)
        
        self.url_admin = u'%s/mgr' % self.url_cgi
        
        self.url_effect_cgi = None
        
        if settings_sub_props.ENVIRONMENT_TYPE == EnvironmentType.RELEASE:
            self.is_rel = True
        else:
            self.is_rel = False

        urlargs = self.getUrlArgs()
        s = urlargs.get(0, "sp")
        if s == "mgr":
            self.is_pc = True
            self.url_cgi = self.url_admin
            self.is_admin = True
            platformtype = platformtype or PlatformType.DMMSP
            app_id = _app_id
        elif s == "pc":
            self.is_pc = True
            self.url_cgi = u'%s/pc' % self.url_cgi
            self.url_static_img_pc = '%spc/' % self.url_static_img
            self.url_static_img = '%ssp/' % self.url_static_img
            self.url_static_js_pc = '%spc/' % self.url_static_js
            self.url_static_js = '%ssp/' % self.url_static_js
            self.url_static_css_pc = '%spc/' % self.url_static_css
            self.url_static_css = '%ssp/' % self.url_static_css
            # LWFではなくSWFを使う場合はpc
            #self.url_static_effect = '%ssp/' % self.url_static_effect
            self.url_static_effect = '%spc/' % self.url_static_effect
            self.url_effect_cgi = '%s/pc' % self.url_static_cgi
            
            # LWFではなくSWFを使う場合はpc
            self.url_static_cgi = '%s/sp' % self.url_static_cgi
            #self.url_static_cgi = '%s/pc' % self.url_static_cgi
            platformtype = PlatformType.DMMPC
            app_id = self.request.get(OSAUtil.KEY_APP_ID)
        else:
            self.is_pc = False
            self.url_cgi = u'%s/sp' % self.url_cgi
            self.url_static_img = '%ssp/' % self.url_static_img
            self.url_static_js = '%ssp/' % self.url_static_js
            self.url_static_css = '%ssp/' % self.url_static_css
            self.url_static_effect = '%ssp/' % self.url_static_effect
            self.url_static_cgi = '%s/sp' % self.url_static_cgi
            platformtype = PlatformType.DMMSP
            app_id = self.request.get(OSAUtil.KEY_APP_ID)
        
        self.url_static_img_l = '%slarge/' % self.url_static_img
        self.url_static_img_m = '%smedium/' % self.url_static_img
        
        if settings_sub.IS_LOCAL:
            self.app_id = '297627'
        else:
            self.app_id = app_id
        self.appparam = AppParam.create(platformtype, app_id)

    def is_active_dxp(self):
        return (settings_sub_props.ENVIRONMENT_TYPE == EnvironmentType.RELEASE and Defines.DXP.ow_is_release) \
            or (settings_sub_props.ENVIRONMENT_TYPE == EnvironmentType.STAGING and Defines.DXP.ow_is_release_staging)
        
    def isUsePCEffect(self):
        if self.is_pc:
            if settings_sub.IS_LOCAL and not self.osa_util.useragent.browser in (BrowserType.FIREFOX, BrowserType.SAFARI):
                return True
            elif not self.osa_util.useragent.browser in (BrowserType.FIREFOX, BrowserType.CHROME, BrowserType.SAFARI):
                return True
        return False
    
    def getUrlEffectCgi(self):
        return self.url_effect_cgi or self.url_static_cgi
    
    def getUrlEffectStatic(self):
        if self.isUsePCEffect():
            return '%seffect/pc/' % self.url_static
        else:
            return '%seffect/sp/' % self.url_static
    
    def setDefaultParam(self):
        # クライアントに渡す値のデフォルトを定義.
        self.url_static_img = self.url_static_img_l
        # largeだけにする.
#        if not self.is_pc:
#            if self.osa_util.useragent.is_android():
#                self.url_static_img = self.url_static_img_m
#            elif self.osa_util.useragent.is_ios():
#                version = self.osa_util.useragent.version
#                if version and version < '4.0.0':
#                    self.url_static_img = self.url_static_img_m
        
        # overrideして使う.
        self.html_param['apptitle'] = settings_sub.APP_TITLE
        self.html_param['apptitle_short'] = settings_sub.APP_TITLE_SHORT
        self.html_param['app_id'] = self.appparam.app_id
        self.html_param['now']= OSAUtil.get_now()
        self.html_param['url_cgi'] = self.url_cgi
        self.html_param['url_admin'] = self.url_admin
        self.html_param['url_static'] = self.url_static
        self.html_param['url_static_img'] = self.url_static_img
        self.html_param['url_static_img_l'] = self.url_static_img_l
        self.html_param['url_static_img_m'] = self.url_static_img_m
        self.html_param['url_static_js'] = self.url_static_js
        self.html_param['url_static_css'] = self.url_static_css
        self.html_param['url_static_effect'] = self.getUrlEffectStatic()
        self.html_param['url_media'] = self.url_media
        self.html_param['viewer_id'] = self.osa_util.viewer_id
        self.html_param['is_dev'] = settings_sub.IS_DEV
        self.html_param['is_local'] = settings_sub.IS_LOCAL
        self.html_param['is_bench'] = settings_sub.IS_BENCH
        self.html_param['is_staging'] = settings_sub_props.ENVIRONMENT_TYPE in (EnvironmentType.STAGING, EnvironmentType.DEVELOP_PC_SHINSEI)
        
        table = {
            EnvironmentType.LOCAL : 'develop',
            EnvironmentType.DEVELOP : 'develop',
            EnvironmentType.STAGING : 'rel',
            EnvironmentType.RELEASE : 'rel',
            EnvironmentType.MANAGER : 'rel',
            EnvironmentType.DMMTEST : 'develop',
            EnvironmentType.DEVELOP_TAKI : 'develop',
            EnvironmentType.DEVELOP_PC : 'develop',
            EnvironmentType.DEVELOP_PC_SHINSEI : 'rel',
            EnvironmentType.RELEASE_PC : 'rel',
        }
        self.html_param['url_static_flowplayer'] = self.url_static + 'swf/flowplayer/' + table.get(settings_sub_props.ENVIRONMENT_TYPE, 'debelop')
        self.html_param['wowza_player_key'] = getattr(settings_sub,'WOWZA_PLAYER_KEY',None)
        # host.
        if self.is_pc and not self.is_admin:
            if settings_sub.IS_DEV:
                host = "sbx-osapi.dmm.com"
            else:
                host = "osapi.dmm.com"
            self.html_param['url_static_img_pc'] = self.url_static_img_pc
            self.html_param['url_static_js_pc'] = self.url_static_js_pc
            self.html_param['url_static_css_pc'] = self.url_static_css_pc
            self.html_param['osapi_global_host'] = host
            self.html_param['web_global_host'] = settings_sub.WEB_GLOBAL_HOST
        
        self.html_param['get_html_param']= self.get_html_param
        self.html_param['make_simplehtml_url']= self.make_simplehtml_url
        
        # 戻るURL.
        self.html_param['url_return'] = self.request.headers.get('referer')
        
        # dmmtop.
        if settings_sub.IS_LOCAL:
            url = self.makeAppLinkUrl(UrlMaker.top())
        elif self.is_pc:
            if settings_sub.IS_DEV:
                url = 'http://sba-netgame.dmm.com/pc/gadget/index/%s' % self.appparam.app_id
            else:
                url = 'http://www.dmm.co.jp/netgame_s/kyabaking/'
        else:
            if settings_sub.IS_DEV:
                url = 'http://sba-netgame.dmm.com/sp/gadget/index/%s' % self.appparam.app_id
            else:
                url = 'http://sp.dmm.co.jp/netgame/gadgets/index/app_id/%s' % self.appparam.app_id
#                url = 'http://www.dmm.co.jp/netgame_s/kyabaking/'
        self.html_param['url_dmm_top'] = url
        
        self.html_param['is_need_flash'] = self.isUsePCEffect()
    
    def writeAppHtml(self, htmlname, quiet=True):
        """HTML.
        """
        self.html_param['getRandN'] = lambda num: AppRandom().getIntN(num)
        self.html_param['getRandS'] = lambda vmin, vmax: AppRandom().getIntS(vmin, vmax)
        
        dirlist = self.get_templates_folder()
        if not isinstance(dirlist, (list, tuple)):
            dirlist = [dirlist]
        htmlname = htmlname + '.html'
        for dirname in dirlist:
            if os.path.exists(os.path.join(OSAUtil.template_dir, dirname + htmlname)):
                if settings_sub.IS_LOCAL and self.request.get('_test'):
                    # テンプレートのテスト.
                    self.osa_util.get_outputhtml(dirname + htmlname, self.html_param, quiet=False)
                    
                    if self.html_param.has_key('get_html_param'):
                        del self.html_param['get_html_param']
                        del self.html_param['Defines']
                        del self.html_param['ItemUtil']
                        del self.html_param['make_simplehtml_url']
                    del self.html_param['getRandN']
                    del self.html_param['getRandS']
                    self.osa_util.write_json_obj(self.html_param)
                else:
                    self.osa_util.write_html(dirname + htmlname, self.html_param, quiet=quiet)
                return
        raise CabaretError(u'ページが存在しません')
    
    def writeAppJson(self):
        """JSON.
        """
        self.osa_util.write_json_obj(self.json_param)
    
    def appRedirect(self, uri, permanent=False, innor=True):
        """リダイレクト.
        """
        if settings_sub.IS_LOCAL and self.request.get('_test'):
            _, querystring = uri.split('?', 1)
            querys = querystring.split('&')
            params = {}
            for query in querys:
                k,v = query.split('=', 1)
                params[k] = v
            params['redirect_url'] = uri
            self.osa_util.write_json_obj(params)
        else:
            self.redirect(uri, permanent, innor)
    
    def decomposeEffectPathForPC(self, effectpath):
        path_arr = effectpath.split('/')
        swf_path = '/'.join(path_arr[:-1])
        pc_effectpath = path_arr[-1]
        return '%s.swf' % swf_path, pc_effectpath
    
    def makeFlashVars(self, params):
        flashVars = ''
        for k,v in params.items():
            flashVars = OSAUtil.addQuery(flashVars, k, urllib.quote((u'%s' % v).encode('utf-8'), ''))
        return flashVars[1:]
    
    def appRedirectToEffect(self, effectpath, params=None, query_params=None):
        """演出へリダイレクト.
        """
        effectpath = '%s/%s' % (Defines.EFFECT_VERSION, effectpath)
        
        if settings_sub.IS_DEV:
            # 開発用.
            effectpath = effectpath.replace('.html', '_dev.html')
        
        if self.isUsePCEffect():
            swf_path, pc_effectpath = self.decomposeEffectPathForPC(effectpath)
            pc_params = {
                'swfPath' : swf_path,
                'flashVars' : self.makeFlashVars(params),
            }
            url = self.makeAppLinkUrlEffect(pc_effectpath, pc_params, do_compress=False)
        else:
            url = self.makeAppLinkUrlEffect(effectpath, params)
        
        if query_params:
            for k,v in query_params.items():
                url = OSAUtil.addQuery(url, k, v)
        url = u'%s#TOP' % url
        
        self.appRedirect(url)
    
    def appRedirectToEffect2(self, effectpath, dataUrl, dataBody=None):
        """演出へリダイレクト.
        """
        effectpath = '%s/%s' % (Defines.EFFECT_VERSION, effectpath)
        
        if settings_sub.IS_DEV:
            # 開発用.
            effectpath = effectpath.replace('.html', '_dev.html')
        params = {
            'dataUrl' : dataUrl,
            'dataBody' : dataBody or '',
            'topUrl' : self.makeAppLinkUrl(UrlMaker.top(), add_frompage=False),
        }
        if self.isUsePCEffect():
            swf_path, pc_effectpath = self.decomposeEffectPathForPC(effectpath)
            params['swfPath'] = swf_path
            url = self.makeAppLinkUrlEffect(pc_effectpath, params, do_compress=False)
        else:
            url = u'%s#TOP' % self.makeAppLinkUrlEffect(effectpath, params, do_compress=False)
        self.appRedirect(url)
    
    #-----------------------------------------------------------------------------
    # link url.
    def addTimeStamp(self, url):
        return OSAUtil.addQuery(url, Defines.URLQUERY_TIMESTAMP, int(time.time()))
    
    def makeAppLinkUrl(self, src_url, add_frompage=True):
        """アプリケーション内のページ遷移URLの作成.
        """
        url = src_url
        url = self.url_cgi + url
        if add_frompage:
            url = self.addFromPageToUrlQuery(url)
        return self.osa_util.makeLinkUrl(self.addTimeStamp(url))
    
    def makeAppLinkUrlAdmin(self, src_url):
        """管理ツール内のページ遷移URLの作成.
        """
        url = self.url_admin + src_url
        return url
    
    def makeAppLinkUrlBinary(self, src_url, do_quote=False, add_frompage=True):
        """ﾘｿｰｽﾍﾟｰｼﾞへの遷移(ｲﾝﾀﾗｸﾃｨﾌﾞ再生), ﾘｿｰｽの埋め込みURL(ｲﾝﾗｲﾝ再生)
        """
        url = src_url
        url = self.url_cgi + url
#        url = OSAUtil.addQuery(url, '_time', OSAUtil.get_now().microsecond / 100)
        url = OSAUtil.addSigned(url)
        if add_frompage:
            url = self.addFromPageToUrlQuery(url)
        return self.osa_util.makeLinkUrlBinary(self.addTimeStamp(url), do_quote)
    
    def makeAppLinkUrlRedirect(self, src_url, add_frompage=True):
        """リダイレクト用アプリケーション内のページ遷移URLの作成.
        """
        url = src_url
        url = self.url_cgi + url
        if add_frompage:
            url = self.addFromPageToUrlQuery(url)
        return self.osa_util.makeLinkUrlRedirect(self.addTimeStamp(url))
    
    def makeAppLinkUrlSwfEmbed(self, src_url, add_frompage=True):
        """SWF用アプリケーション内のページ遷移URLの作成.
        今はリダイレクトと一緒
        変更が必要になったらで
        """
        url = src_url
        url = self.url_cgi + url
        if add_frompage:
            url = self.addFromPageToUrlQuery(url)
        return self.osa_util.makeLinkUrlSwfEmbed(self.addTimeStamp(url))
    
    def makeAppLinkUrlMedia(self, src_url):
        """mediaファイルへのURL.
        """
        url = src_url
        url = self.url_media + url
        return url
    
    def makeAppLinkUrlStatic(self, src_url, do_quote=False):
        """staticファイルへのURL.
        """
        url = src_url
        url = self.url_static + url
        return url
    
    def makeAppLinkUrlImg(self, src_url, do_quote=False):
        """static画像ファイルへのURL.
        """
        url = src_url
        url = self.url_static_img + url
        return url
    
    def makeAppLinkUrlImgLarge(self, src_url, do_quote=False):
        """static画像ファイルへのURL.
        """
        url = src_url
        url = self.url_static_img_l + url
        return url
    
    def makeAppLinkUrlImgMedium(self, src_url, do_quote=False):
        """static画像ファイルへのURL.
        """
        url = src_url
        url = self.url_static_img_m + url
        return url
    
    def makeAppLinkUrlCss(self, src_url, do_quote=False):
        """static cssファイルへのURL.
        """
        url = src_url
        url = self.url_static_css + url
        return url
    
    def makeAppLinkUrlJs(self, src_url, do_quote=False):
        """static jsファイルへのURL.
        """
        url = src_url
        url = self.url_static_js + url
        return url
    
    def makeAppLinkUrlEffect(self, src_url, params=None, do_quote=False, do_compress=True):
        """演出ファイルへのURL.
        """
        url = src_url
        if params:
            if not do_compress or (settings_sub.IS_LOCAL and self.request.get('_test')):
                for k,v in params.items():
                    url = OSAUtil.addQuery(url, k, urllib.quote((u'%s' % v).encode('utf-8'), ''))
            else:
                hexstr = binascii.b2a_hex(zlib.compress(Json.encode(params).encode('utf-8')))
                url = OSAUtil.addQuery(url, 'params', hexstr)
        url = self.getUrlEffectStatic() + url
        return url
    
    def makeAppLinkUrlEffectParamGet(self, ope):
        """演出パラメータ取得用のURL.
        """
        url = self.getUrlEffectCgi() + UrlMaker.effect(ope)
        url = OSAUtil.addQuery(url, OSAUtil.KEY_OWNER_ID, self.osa_util.viewer_id)
        url = OSAUtil.addQuery(url, OSAUtil.KEY_APP_ID, self.appparam.app_id)
        if self.is_pc and self.osa_util.session:
            url = OSAUtil.addQuery(url, '_session', self.osa_util.session)
        return url
    
    #-----------------------------------------------------------------------------
    # etc...
    def getUrlArgs(self, base_path='/'):
        """
        現状のリクエストURLを元にREST形式URL paramのクラスインスタンスを返す
        """
        return UrlArgs(self.url_cgi + base_path, self.request.url)
    
    def getJsonArgs(self):
        """リクエストのbodyに入ってたJSONオブジェクトを返す.
        """
        if self.__json_args is None:
            request_body = self.request.body
            if self.__is_secure_body:
                # 復号化する.
                request_body = PLCrypto.decrypt(request_body)
            json_str = urllib.unquote(request_body) # 受け取ったJSON
            if not json_str or json_str[0] != '{':
                # 最初の文字が{じゃないときはJSONではない。たぶん。
                self.__json_args = {}
            else:
                if json_str[-1] == '=':
                    json_str = json_str[0:-1] # 最後の=を消す.
                self.__json_args = Json.decode(json_str)
        return self.__json_args
        
        
    def __call__(self):
        
        try:
            if self.request.useragent == "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)":
                # ウィルスバスターのアクセス.IE6も死ぬけど仕方ない.
                self.response.end()
                return
            
            self.__setStaticParam()
            self.osa_util = OSAUtil(self, self.appparam, self.is_pc)
        except:
            if not settings_sub.IS_DEV:
                try:
                    DbgLogger.write_error(self.__makeErrorHtml())
                except:
                    DbgLogger.write_error(u'Unknown...')
                self.response.clear()
                self.response.set_status(400)
                self.response.send('Bad Request')
                return
            raise
        
        try:
            self.addloginfo('checkUser')
            self.checkUser()
            self.addloginfo('setDefaultParam')
            self.setDefaultParam()
            self.addloginfo('check_process_pre')
            if self.check_process_pre():
                if settings_sub.IS_BENCH:
                    self.procBench()
                self.addloginfo('preprocess')
                self.preprocess()
                self.addloginfo('process')
                self.process()
        except AppError, er:
#            if er.code == AppError.Code.TOO_MANY_TRANSACTION:
#                DbgLogger.write_app_log(value=u'%s:%s' % (OSAUtil.get_now().strftime("[%Y-%m-%d %H:%M:%S]"), er.value))
            self.processAppError(er)
        except TimeoutError:
            # db接続ﾀｲﾑｱｳﾄ.
            self.processTimeout()
        except Exception:
            body = self.__makeErrorHtml()
            self.osa_util.logger.error(body)
            if self.osa_util.is_dbg_user:
                # デバッグﾕｰｻﾞｰはエラーの内容を知りたい.
                self.__processError(body)
            else:
                self.__processError(u'ｴﾗｰが発生しました。')
        
    def __makeErrorHtml(self):
        info = sys.exc_info()
        
        t = str(info[0]).replace('<', '').replace('>','')
        ex = '%s:%s' % (t, info[1])
        t_list = traceback.extract_tb(info[2])
        trace = ''
        for t in t_list:
            trace += '%s:%s<br />- %s<br />' % (t[0], t[1], t[2])
        body = ''
        body += 'request_path:<br />%s<br /><br />' % (self.request.path)
        body += 'trace:<br />%s<br />error:%s<br />' % (trace, ex)
        body += '<br />'
        body = body.replace('<br />', '\r\n')
        return body
    
    def __processError(self, error_message):
        # なんかｴﾗｰ.
        if settings_sub.IS_LOCAL and self.request.get('_test'):
            self.addlogerror(error_message)
            self.response.clear()
            self.response.set_status(500)
            self.response.write(error_message)
            self.response.end()
        else:
            self.processError(error_message)
    
    def processError(self, error_message):
        # なんかｴﾗｰ.
        self.html_param['error_message'] = error_message
        self.osa_util.write_html('error.html', self.html_param)
    
    def processAppError(self, err):
        self.__processError(StrUtil.to_s(err.getHtml(self.osa_util.is_admin_access and self.osa_util.is_dbg_user)))
    
    def check_process_pre(self):
        # メインの処理の前にチェックしたいこと.
        return True
    
    def processTimeout(self):
        # タイムアウト.
        body = self.__makeErrorHtml()
        self.__processError(body)
    
    def preprocess(self):
        pass
    def process(self):
        raise CabaretError('page not found')
    
    def checkUser(self):
        # overrideして必要な作業だけおこなう.
        self.osa_util.checkUser()
        self.osa_util.checkOAuth()
        
        if self.osa_util.is_admin_access and self.osa_util.is_dbg_user:
            return
        elif self.is_pc and not self.osa_util.useragent.is_pc():
            pass
        elif not self.is_pc and not self.osa_util.useragent.is_smartphone():
            pass
        else:
            return
        self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.no_support(), add_frompage=False))
    
    def addAppApiRequest(self, key, request, callback=None, *args, **kwargs):
        """ｱﾌﾟﾘ用APIリクエスト.
        """
        if request is not None:
            self._api_works[key] = [callback, args, kwargs]
            self.osa_util.addApiRequest(key, request)
    
    def execute_api(self):
        """ｱﾌﾟﾘ用APIリクエストの実行.
        """
        keys = self._api_works.keys()
        ret_data = None
        if 0 < len(keys):
            ret_data = self.osa_util.getThreadResult()
            
            for k in keys:
                work = self._api_works[k]
                f = work[0]
                if f != None:
                    args = work[1]
                    kwargs = work[2]
                    f(ret_data, *args, **kwargs)
                
            # もう一度呼び出すのを防ぐ.
            self._api_works = {}
        return ret_data
    
    def getModelMgr(self):
        """モデルのリクエスト管理オブジェクト.
        """
        return self.__model_mgr
    
    def addlog(self, msg):
        self.osa_util.logger.trace(msg)
    def addloginfo(self, msg):
        now = OSAUtil.get_now()
        td = now - self.__logtime
        self.osa_util.logger.info('(%d.%06dsec) %s' % (td.seconds, td.microseconds, msg))
        self.__logtime = now
    def addlogerror(self, msg):
        self.osa_util.logger.error(msg)
    
    def procBench(self):
        """ベンチマーク時に通るプロセス.
        """
        pass
    
    
    def get_html_param(self, key, key_test=None, data=None):
        # "."で文字列を分割する
        arr = key.split('.')
        key = arr[0]
        v = data or self.html_param
        for i in xrange(len(arr)):
            key = arr[i]
            if isinstance(v, dict) and v.has_key(key):
                v = v[key]
            else:
                v = ''
                break
        return v
    
    def make_simplehtml_url(self, target, **kwargs):
        """ただHTMLを表示するだけのページのURL.
        """
        url = UrlMaker.simple_html(target)
        for k,v in kwargs.items():
            url = OSAUtil.addQuery(url, k, urllib.quote(str(v)))
        return self.makeAppLinkUrl(url)
    
    def getFromPage(self):
        if self.__from_page is None:
            self.__from_page = FromPageUtil()
            self.__from_page.setParamsByString(self.request.get(Defines.URLQUERY_FROM))
        return self.__from_page
    
    def getFromPageName(self):
        return self.getFromPage().get('name', None)
    
    def getFromPageArgs(self):
        return self.getFromPage().get('args', None)
    
    def setFromPage(self, name, value=None):
        self.__from_page = FromPageUtil()
        self.__from_page.setParams(name, value)
    
    def addFromPageToUrlQuery(self, url):
        from_page = self.getFromPage()
        if from_page:
            return from_page.addQuery(url)
        return url
    
    def putPagenation(self, urlbase, page, contentnum, page_contentnum, urlhash=None):
        page_contentnum = max(1, page_contentnum)
        page_max = max(1, int((contentnum + page_contentnum - 1) / page_contentnum))
        
        if 0 < page:
            url = self.makeAppLinkUrl(OSAUtil.addQuery(urlbase, Defines.URLQUERY_PAGE, page - 1))
            if urlhash:
                url = "%s#%s" % (url, urlhash)
            self.html_param['url_page_prev'] = url
        if (page+1) < page_max:
            url = self.makeAppLinkUrl(OSAUtil.addQuery(urlbase, Defines.URLQUERY_PAGE, page + 1))
            if urlhash:
                url = "%s#%s" % (url, urlhash)
            self.html_param['url_page_next'] = url
        self.html_param['cur_page'] = page + 1
        self.html_param['page_max'] = page_max
