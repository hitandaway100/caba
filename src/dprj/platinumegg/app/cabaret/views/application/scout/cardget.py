# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.views.application.scout.base import ScoutHandler
from defines import Defines
import settings_sub
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util import db_util


class Handler(ScoutHandler):
    """スカウトカード獲得書き込み.
    引数:
        実行したスカウトのID.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        args = self.getUrlArgs('/scoutcardget/')
        try:
            scoutid = int(args.get(0))
            itemid = int(self.request.get(Defines.URLQUERY_ID, 0))
        except:
            raise CabaretError(u'引数が想定外です', CabaretError.Code.ILLEGAL_ARGS)
        
        v_player = self.getViewerPlayer()
        model_mgr = self.getModelMgr()
        
        # アイテムの確認.
        itemmaster = None
        if itemid:
            if not itemid in Defines.ItemEffect.SCOUT_CARD_ITEMS:
                if settings_sub.IS_LOCAL:
                    raise CabaretError(u'使用できないアイテムです')
                playdata = BackendApi.get_scoutprogress(model_mgr, v_player.id, [scoutid], using=settings.DB_READONLY).get(scoutid, None)
                if playdata:
                    url = UrlMaker.scoutresult(scoutid, playdata.alreadykey)
                    self.appRedirect(self.makeAppLinkUrlRedirect(url))
                else:
                    self.redirectToTop()
                return
            itemmaster = BackendApi.get_itemmaster(model_mgr, itemid, using=settings.DB_READONLY)
            if itemmaster is None:
                raise CabaretError(u'アイテムが見つかりません', CabaretError.Code.INVALID_MASTERDATA)
        
        playerconfigdata = BackendApi.get_playerconfigdata(v_player.id)
        
        try:
            model_mgr = db_util.run_in_transaction(Handler.tr_write, v_player.id, scoutid, itemmaster, playerconfigdata.autosell_rarity)
            model_mgr.write_end()
        except CabaretError, err:
            if settings_sub.IS_LOCAL:
                raise
            elif err.code == CabaretError.Code.ALREADY_RECEIVED:
                # 判定済み.
                pass
            else:
                raise
        
        url = UrlMaker.scoutcardgetresult(scoutid)
        self.appRedirect(self.makeAppLinkUrlRedirect(url))
    
    @staticmethod
    def tr_write(uid, scoutid, itemmaster, autosell_rarity):
        """書き込み.
        """
        model_mgr = ModelRequestMgr()
        BackendApi.tr_determine_scoutcard(model_mgr, uid, scoutid, itemmaster, autosell_rarity=autosell_rarity)
        model_mgr.write_all()
        return model_mgr

def main(request):
    return Handler.run(request)
