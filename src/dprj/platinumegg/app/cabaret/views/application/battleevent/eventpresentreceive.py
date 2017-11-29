# -*- coding: utf-8 -*-
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from platinumegg.app.cabaret.views.application.battleevent.base import BattleEventBaseHandler
import urllib
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util import db_util


class Handler(BattleEventBaseHandler):
    """バトルイベントプレゼント受け取りページ.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        
        args = self.getUrlArgs('/battleeventpresentreceive/')
        confirmkey = urllib.unquote(args.get(0) or '')
        
        now = OSAUtil.get_now()
        
        model_mgr = self.getModelMgr()
        
        # 対象のイベント.
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
        
        # 次を選ぶ.
        presentmaster_list = BackendApi.get_battleeventpresent_master_by_eventdid(model_mgr, cur_eventmaster.id, using=settings.DB_READONLY).values()
        presentmaster_next = BackendApi.choice_battleeventpresent(model_mgr, uid, cur_eventmaster.id, using=settings.DB_READONLY, presentmaster_list=presentmaster_list)
        
        try:
            db_util.run_in_transaction(Handler.tr_write, uid, cur_eventmaster.id, confirmkey, presentmaster_next).write_end()
        except CabaretError, err:
            BackendApi.get_battleeventpresent_pointdata(model_mgr, uid, cur_eventmaster.id)
            if err.code == CabaretError.Code.ALREADY_RECEIVED:
                pass
            else:
                raise
        
        # 演出へリダイレクト.
        url = UrlMaker.battleevent_presentanim()
        self.appRedirect(self.makeAppLinkUrlRedirect(url))
    
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
