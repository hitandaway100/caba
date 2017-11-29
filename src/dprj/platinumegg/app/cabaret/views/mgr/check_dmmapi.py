# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.adminhandler import AdminHandler
import settings_sub
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.lib.platform.api.objects import PeopleRequestData
from platinumegg.lib.platform.api.request import ApiNames
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from platinumegg.lib.strutil import StrUtil
import urllib
import urllib2


class Handler(AdminHandler):
    """DMM API生存確認ページ.
    """
    
    @classmethod
    def get_timeout_time(cls):
        return 5
    
    @classmethod
    def get_default_status(cls):
        """デフォルトで返すHttpStatus.
        """
        return 500
    
    def checkUser(self):
        # 認証.
        if settings_sub.IS_LOCAL:
            return
        elif self.request.remote_addr.startswith('10.116.41.'):
            return
        self.response.set_status(404)
        raise CabaretError(u'NotFound!!', CabaretError.Code.NOT_AUTH)
    
    def send(self, status):
        self.response.set_status(status)
        self.response.send()
    
    def process(self):
        
        model_mgr = self.getModelMgr()
        appconfig = BackendApi.get_appconfig(model_mgr, using=settings.DB_READONLY)
        if appconfig.is_maintenance():
            # メンテ中はチェックしない.
            self.send(200)
            return
        
        if settings_sub.IS_DEV:
            VIEWER_ID = "8350420"
        else:
            VIEWER_ID = "10814964"
        
        def callback(ret_data, reqkey, dmmid, result):
            try:
                person = ret_data[reqkey].get()
                if type(person) in (list, tuple):
                    person = person[0]
                result[dmmid] = person
            except:
                pass
        
        
        request = self.osa_util.makeApiRequest(ApiNames.People, PeopleRequestData.createForPeople(VIEWER_ID))
        reqkey = 'check_dmmapi:%s' % VIEWER_ID
        self.addAppApiRequest(reqkey, request)
        
        client = OSAUtil.get_cache_client()
        error_cnt = int(client.get("check_dmmapi:error") or 0)
        
        ret_data = self.execute_api()
        success = False
        try:
            ret_data[reqkey].get()
            success = True
        except Exception:
            error_cnt += 1
            if 5 < error_cnt:
                if (error_cnt-5) % 10 == 1:
                    message = u"""[To:1984418] 藤竿 高志(Takashi FUJISAO)さん\n[To:1980432] 山田 健太(YAMADA Kenta)さん\n[To:1973173] 川合 佑輔(Yusuke Kawai)さん\n[To:2004847] 酒井 崇(Takashi SAKAI)さん\n[To:1973150] 秋谷 亮(RYO Akitani)さん\nΩ＼ζ°)ﾁｰﾝ＜DMMのAPIサーバが死にました…\n上様ご乱心です"""
                    self.sendmessage_to_chatwork(message)
                self.send(500)
                return
        if success:
            if 0 < error_cnt:
                message = u"""DMMのAPIサーバが生き返ったよ！！"""
                self.sendmessage_to_chatwork(message)
            error_cnt = 0
        client.set("check_dmmapi:error", error_cnt)
        self.send(200)
    
    def sendmessage_to_chatwork(self, message):
        try:
            SERVER_URL = "https://api.chatwork.com/v1"
            url = '{}/rooms/21193248/messages'.format(SERVER_URL)
            data = urllib.urlencode({"body" :u"[To:1984418] 藤竿 高志(Takashi FUJISAO)さん\n[To:1980432] 山田 健太(YAMADA Kenta)さん\n[To:1973173] 川合 佑輔(Yusuke Kawai)さん\n[To:2004847] 酒井 崇(Takashi SAKAI)さん\n[To:1973150] 秋谷 亮(RYO Akitani)さん\n{}".format(message)})
            req = urllib2.Request(url)
            req.get_method = lambda:'POST'
            req.add_header('X-ChatWorkToken', '2ab7238c4d2920a9714742389a0a8eb4')
            req.add_data(StrUtil.to_s(data))
            urllib2.urlopen(req)
        except:
            if settings_sub.IS_DEV:
                raise

def main(request):
    return Handler.run(request)
