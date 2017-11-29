# -*- coding: utf-8 -*-
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from platinumegg.app.cabaret.views.application.battleevent.base import BattleEventBaseHandler
from defines import Defines
from platinumegg.app.cabaret.util.cabareterror import CabaretError


class Handler(BattleEventBaseHandler):
    """バトルイベントプレゼントページ.
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
        
        view_result = self.request.get(Defines.URLQUERY_FLAG) == '1'
        
        # 現在の贈り物情報を確認.
        presentdata = BackendApi.get_battleeventpresent_pointdata(model_mgr, uid, cur_eventmaster.id, using=(settings.DB_DEFAULT if view_result else settings.DB_READONLY))
        if presentdata is None:
            raise CabaretError(u'このイベントでは閲覧できません')
        
        cur_data = presentdata.getData()
        presentmaster = BackendApi.get_battleeventpresent_master(model_mgr, cur_eventmaster.id, cur_data['number'], using=settings.DB_READONLY)
        if presentmaster.point <= presentdata.point:
            # 達成済み.
            playerrequest = BackendApi.get_playerrequest(model_mgr, uid)
            url = UrlMaker.battleevent_presentreceive(playerrequest.req_confirmkey)
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        
        # 結果表示フラグ.
        if view_result and presentdata.precontent:
            contentmaster = BackendApi.get_battleeventpresent_content_master(model_mgr, presentdata.precontent, using=settings.DB_READONLY)
            prizelist = BackendApi.get_prizelist(model_mgr, contentmaster.prizes, using=settings.DB_READONLY)
            self.html_param['prize'] = BackendApi.make_prizeinfo(self, prizelist, using=settings.DB_READONLY)
        
        # 現在の贈り物情報.
        self.html_param['battleeventpresent'] = Objects.battleevent_present(self, presentmaster, presentdata)
        
        # イベント情報.
        self.html_param['battleevent'] = Objects.battleevent(self, cur_eventmaster, now)
        
        # 対戦相手一覧のリンク.
        url = UrlMaker.battleevent_opplist()
        self.html_param['url_battleevent_opplist'] = self.makeAppLinkUrl(url)
        
        # 報酬一覧のリンク.
        url = UrlMaker.battleevent_presentlist()
        self.html_param['url_battleevent_presentlist'] = self.makeAppLinkUrl(url)
        
        # HTML書き出し.
        self.writeAppHtml('%s/present' % ('gcevent' if cur_eventmaster.is_goukon else 'btevent'))
    

def main(request):
    return Handler.run(request)
