# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.cabareterror import CabaretError
import settings_sub
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.views.application.loginbonus.base import LoginBonusHandler
from platinumegg.lib.opensocial.util import OSAUtil
import settings
from defines import Defines


class Handler(LoginBonusHandler):
    """期限付きログインボーナス演出.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        
        args = self.getUrlArgs('/lbtlanim/')
        mid = args.getInt(0)
        loginbonus = args.getInt(1)
        
        model_mgr = self.getModelMgr()
        now = OSAUtil.get_now()
        
        # プレイヤー情報.
        v_player = self.getViewerPlayer()
        if BackendApi.check_lead_loginbonustimelimited(model_mgr, v_player.id, now):
            # まだ受け取っていない.
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'まだ受け取っていない')
            url = self.makeAppLinkUrlRedirect(UrlMaker.loginbonustimelimiteddo())
            self.appRedirect(url)
            return
        
        logindata = BackendApi.get_logintimelimited_data(model_mgr, v_player.id, mid, using=settings.DB_READONLY)
        if logindata is None:
            url = self.makeAppLinkUrlRedirect(UrlMaker.mypage())
            self.appRedirect(url)
            return
        
        cur_day = logindata.days
        
        master = BackendApi.get_loginbonustimelimitedmaster(model_mgr, mid, using=settings.DB_READONLY)
        if master is None:
            url = self.makeAppLinkUrlRedirect(UrlMaker.mypage())
            self.appRedirect(url)
            return
        
        #取得したアイテム(名前,日数).
        cur_bonusmaster = BackendApi.get_loginbonustimelimiteddaysmaster(model_mgr, master.id, cur_day, using=settings.DB_READONLY)
        if not cur_bonusmaster:
            # 演出いらない.
            url = self.makeAppLinkUrlRedirect(UrlMaker.mypage())
            self.appRedirect(url)
            return
        
        str_midlist = self.request.get(Defines.URLQUERY_ID) or ''
        dataUrl = self.makeAppLinkUrlEffectParamGet('loginbonustimelimited/%s/%s' % (mid, loginbonus))
        if str_midlist:
            dataUrl = OSAUtil.addQuery(dataUrl, Defines.URLQUERY_ID, str_midlist)

        self.appRedirectToEffect2('%s/effect2.html' % master.effectname, dataUrl)

def main(request):
    return Handler.run(request)
