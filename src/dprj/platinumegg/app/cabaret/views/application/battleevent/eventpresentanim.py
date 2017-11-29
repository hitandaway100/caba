# -*- coding: utf-8 -*-
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from platinumegg.app.cabaret.views.application.battleevent.base import BattleEventBaseHandler
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from defines import Defines


class Handler(BattleEventBaseHandler):
    """バトルイベントプレゼント受け取り演出.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        
        now = OSAUtil.get_now()
        
        model_mgr = self.getModelMgr()
        
        config = BackendApi.get_current_battleeventconfig(model_mgr, using=settings.DB_READONLY)
        cur_eventmaster = None
        if config.mid and config.starttime <= now < config.epilogue_endtime:
            cur_eventmaster = BackendApi.get_battleevent_master(model_mgr, config.mid, using=settings.DB_READONLY)
        
        if cur_eventmaster is None:
            self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.mypage()))
            return
        elif config.starttime <= now < config.endtime:
            self.checkBattleEventUser(do_check_battle_open=False, do_check_regist=False)
            if self.response.isEnd:
                return
        
        v_player = self.getViewerPlayer()
        uid = v_player.id
        
        # 現在の贈り物情報を確認.
        presentdata = BackendApi.get_battleeventpresent_pointdata(model_mgr, uid, cur_eventmaster.id, using=settings.DB_DEFAULT)
        pre_data = presentdata.getPreData()
        if pre_data is None:
            # 受け取り情報がない.
            self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.mypage()))
            return
        
        # 達成を一応確認.
        cur_data = presentdata.getData()
        presentmaster = BackendApi.get_battleeventpresent_master(model_mgr, cur_eventmaster.id, cur_data['number'], using=settings.DB_READONLY)
        if presentmaster.point <= presentdata.point:
            # 達成済みで受け取っていない.
            playerrequest = BackendApi.get_playerrequest(model_mgr, uid)
            url = UrlMaker.battleevent_presentreceive(playerrequest.req_confirmkey)
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        
        presentmaster = BackendApi.get_battleeventpresent_master(model_mgr, cur_eventmaster.id, pre_data['number'], using=settings.DB_READONLY)
        
        # 演出後のページ.
        url = OSAUtil.addQuery(UrlMaker.battleevent_present(), Defines.URLQUERY_FLAG, 1)
        
        params = {
            'backUrl' : self.makeAppLinkUrl(url),
            'logoPre' : self.url_static_img + 'event/btevent/%s/' % cur_eventmaster.codename,
            'pre' : self.url_static_img,
            'item' : presentmaster.thumb,
        }
        
        # 演出へリダイレクト.
        self.appRedirectToEffect('btevent/event_extra_alcohol/effect.html', params)
    
    @staticmethod
    def tr_write(uid, eventid, confirmkey, presentmaster_next):
        """書き込み.
        """
        model_mgr = ModelRequestMgr()
        BackendApi.tr_battleeventpresent_receive_present(model_mgr, uid, eventid, confirmkey, presentmaster_next)
        model_mgr.write_all()
        return model_mgr

def main(request):
    return Handler.run(request)
