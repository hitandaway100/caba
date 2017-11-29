# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from defines import Defines
import settings_sub
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.views.application.raidevent.base import RaidEventBaseHandler


class Handler(RaidEventBaseHandler):
    """スカウトカード獲得書き込み.
    引数:
        実行したスカウトのID.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        args = self.getUrlArgs('/raideventscoutcardget/')
        try:
            stageid = int(args.get(0))
            itemid = int(self.request.get(Defines.URLQUERY_ID, 0))
            usenum = int(self.request.get(Defines.URLQUERY_NUMBER, 0))
            if not (0 <= usenum):
                raise
        except:
            raise CabaretError(u'引数が想定外です', CabaretError.Code.ILLEGAL_ARGS)
        
        v_player = self.getViewerPlayer()
        model_mgr = self.getModelMgr()
        
        using = settings.DB_READONLY
        
        eventmaster = BackendApi.get_current_raideventmaster(model_mgr, using=using)
        if eventmaster is None:
            raise CabaretError(u'Event Closed.', CabaretError.Code.EVENT_CLOSED)
        mid = eventmaster.id
        
        # アイテムの確認.
        itemmaster = None
        if itemid:
            if not itemid in Defines.ItemEffect.SCOUT_CARD_ITEMS:
                if settings_sub.IS_LOCAL:
                    raise CabaretError(u'使用できないアイテムです')
                playdata = BackendApi.get_raideventstage_playdata(model_mgr, mid, v_player.id, using)
                if playdata:
                    url = UrlMaker.raidevent_scoutresult(stageid, playdata.alreadykey)
                    self.appRedirect(self.makeAppLinkUrlRedirect(url))
                else:
                    self.redirectToTop()
                return
            itemmaster = BackendApi.get_itemmaster(model_mgr, itemid, using=settings.DB_READONLY)
            if itemmaster is None:
                raise CabaretError(u'アイテムが見つかりません', CabaretError.Code.INVALID_MASTERDATA)
        
        playerconfigdata = BackendApi.get_playerconfigdata(v_player.id)
        
        try:
            model_mgr = db_util.run_in_transaction(Handler.tr_write, mid, v_player.id, stageid, itemmaster, usenum, playerconfigdata.autosell_rarity)
            model_mgr.write_end()
        except CabaretError, err:
            if settings_sub.IS_LOCAL:
                raise
            elif err.code == CabaretError.Code.ALREADY_RECEIVED:
                # 判定済み.
                pass
            else:
                raise
        
        url = UrlMaker.raidevent_scoutcardgetresult(stageid)
        self.appRedirect(self.makeAppLinkUrlRedirect(url))
    
    @staticmethod
    def tr_write(mid, uid, stageid, itemmaster, usenum, autosell_rarity):
        """書き込み.
        """
        model_mgr = ModelRequestMgr()
        BackendApi.tr_determine_raidevent_scoutcard(model_mgr, mid, uid, stageid, itemmaster, usenum, autosell_rarity=autosell_rarity)
        model_mgr.write_all()
        return model_mgr

def main(request):
    return Handler.run(request)
