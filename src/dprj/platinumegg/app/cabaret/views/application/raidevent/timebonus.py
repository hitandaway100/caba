# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.application.raidevent.base import RaidEventBaseHandler
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.api import BackendApi
import settings


class Handler(RaidEventBaseHandler):
    """イベントレイドタイムボーナス演出.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        
        model_mgr = self.getModelMgr()
        cur_eventmaster = self.getCurrentRaidEvent()
        v_player = self.getViewerPlayer()
        uid = v_player.id
        
        # OP閲覧フラグを確認.
        flagrecord = self.getCurrentRaidFlagRecord()
        if flagrecord is None:
            # OPを見ていない.
            url = UrlMaker.raidevent_opening()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        
        # タイムボーナス演出閲覧判定.
        now = OSAUtil.get_now()
        stime, etime = BackendApi.get_raidevent_timebonus_time(model_mgr, using=settings.DB_READONLY, now=now)
        if stime is None or etime is None:
            # タイムボーナス中じゃない.
            url = UrlMaker.raidevent_start()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
            
        elif not (stime <= flagrecord.tbvtime < etime):
            # タイムボーナス演出閲覧時間を更新.
            flagrecord = BackendApi.update_raideventflagrecord(model_mgr, cur_eventmaster.id, uid, tbvtime=now)
            model_mgr.set_got_models([flagrecord])
        
        # 演出のパラメータ.
#        effectpath = '%s/timebonus/effect.html' % cur_eventmaster.effectname
#        effectpath = 'levelup/effect.html'
#        params = {
#            'backUrl' : self.makeAppLinkUrl(UrlMaker.raidevent_start()),
#        }
#        self.appRedirectToEffect(self.makeAppLinkUrlEffect(effectpath, params))
        self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.raidevent_start()))
    

def main(request):
    return Handler.run(request)
