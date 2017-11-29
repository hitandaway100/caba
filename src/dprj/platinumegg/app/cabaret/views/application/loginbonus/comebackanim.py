# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.cabareterror import CabaretError
import settings_sub
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.views.application.loginbonus.base import LoginBonusHandler
from platinumegg.lib.opensocial.util import OSAUtil
import settings
from platinumegg.app.cabaret.models.Player import PlayerLogin


class Handler(LoginBonusHandler):
    """カムバックキャンペーン演出.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerLogin]
    
    def process(self):
        
        args = self.getUrlArgs('/comebackanim/')
        mid = args.getInt(0)
        loginbonus = args.getInt(1)
        
        model_mgr = self.getModelMgr()
        now = OSAUtil.get_now()
        
        # プレイヤー情報.
        v_player = self.getViewerPlayer()
        if not BackendApi.check_loginbonus_received(v_player, now):
            # まだ受け取っていない.
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'まだ受け取っていない')
            url = self.makeAppLinkUrlRedirect(UrlMaker.loginbonus())
            self.appRedirect(url)
            return
        
        uid = v_player.id
        
        comebackdata = BackendApi.get_comebackcampaign_userdata(model_mgr, uid, mid, using=settings.DB_READONLY)
        if comebackdata is None:
            url = self.makeAppLinkUrlRedirect(UrlMaker.mypage())
            self.appRedirect(url)
            return
        
        cur_day = comebackdata.days
        master = BackendApi.get_comebackcampaignmaster(model_mgr, mid, using=settings.DB_READONLY)
        if master is None:
            url = self.makeAppLinkUrlRedirect(UrlMaker.mypage())
            self.appRedirect(url)
            return
        
        # 遷移先.
        url = self.makeNextEffectUrl(loginbonus, timelimited=True, comeback=mid, sugoroku=True)
        
        today_thumb = master.get_thumbnail(cur_day)
        
        if today_thumb is not None:
            params = {
                'backUrl' : self.makeAppLinkUrlSwfEmbed(url),
                'pre' : self.url_static_img,
                'i0' : today_thumb,
                'has_next' : False,
            }
            tomorrow_thumb = master.get_thumbnail(cur_day+1)
            if tomorrow_thumb is not None:
                params.update(i1=tomorrow_thumb, has_next=True)
            
            self.appRedirectToEffect('%s/effect.html' % master.effectname, params)
        else:
            self.appRedirect(self.makeAppLinkUrlRedirect(url))

def main(request):
    return Handler.run(request)
