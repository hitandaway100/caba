# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.views.application.scoutevent.base import ScoutHandler
from defines import Defines
import settings_sub
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util import db_util


class Handler(ScoutHandler):
    """スカウトイベントチップ交換書き込み.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        try:
            tanzaku_number = int(self.request.get(Defines.URLQUERY_ID))
            tanzaku_num = int(self.request.get(Defines.URLQUERY_NUMBER))
        except:
            raise CabaretError(u'引数が想定外', CabaretError.Code.ILLEGAL_ARGS)
        
        args = self.getUrlArgs('/sceventtiptradedo/')
        confirmkey = args.get(0)
        
        model_mgr = self.getModelMgr()
        
        using = settings.DB_READONLY
        
        eventmaster = BackendApi.get_current_scouteventmaster(model_mgr, using=using)
        if eventmaster is None:
            raise CabaretError(u'Event Closed.', CabaretError.Code.EVENT_CLOSED)
        mid = eventmaster.id
        
        v_player = self.getViewerPlayer()
        uid = v_player.id
        
        # 短冊情報.
        tanzakumaster = BackendApi.get_scoutevent_tanzakumaster(model_mgr, mid, tanzaku_number, using=settings.DB_READONLY)
        if tanzakumaster is None:
            if settings_sub.IS_DEV:
                raise CabaretError(u'存在しない短冊です', CabaretError.Code.ILLEGAL_ARGS)
            url = UrlMaker.scouteventtiptrade()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        
        def tr(uid, eventmaster, tanzakumaster, num, confirmkey):
            model_mgr = ModelRequestMgr()
            BackendApi.tr_scoutevent_trade_tip(model_mgr, uid, eventmaster, tanzakumaster, num, confirmkey)
            model_mgr.write_all()
            return model_mgr
        try:
            db_util.run_in_transaction(tr, uid, eventmaster, tanzakumaster, tanzaku_num, confirmkey).write_end()
        except CabaretError, err:
            if err.code == CabaretError.Code.ALREADY_RECEIVED:
                pass
            else:
                raise
        
        url = UrlMaker.scouteventtiptraderesult(tanzaku_number, tanzaku_num)
        self.appRedirect(self.makeAppLinkUrlRedirect(url))

def main(request):
    return Handler.run(request)
