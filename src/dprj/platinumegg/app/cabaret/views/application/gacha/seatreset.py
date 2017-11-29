# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.application.gacha.base import GachaHandler
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from defines import Defines
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util import db_util
import settings
from platinumegg.app.cabaret.util.cabareterror import CabaretError


class Handler(GachaHandler):
    """シートのリセット.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        # チェックの確認.
        flag = self.request.get(Defines.URLQUERY_ACCEPT) == '1'
        if not flag:
            # ユーザーが承認していない.
            pass
        else:
            model_mgr = self.getModelMgr()
            v_player = self.getViewerPlayer()
            uid = v_player.id
            
            # BoxID.
            gachamid = str(self.request.get(Defines.URLQUERY_ID) or '')
            
            gachamaster = None
            if gachamid and gachamid.isdigit():
                gachamid = int(gachamid)
                gachamaster = BackendApi.get_gachamaster(model_mgr, gachamid, using=settings.DB_READONLY)
            
            if gachamaster is None or not gachamaster.seattableid or gachamaster.consumetype not in {Defines.GachaConsumeType.SEAT, Defines.GachaConsumeType.SEAT2} or gachamaster.stock != 0:
                # リセットできない.
                pass
            else:
                # 書き込み.
                Handler.write(uid, gachamaster)
        
        url = OSAUtil.addQuery(UrlMaker.gacha(), Defines.URLQUERY_CTYPE, Defines.GachaConsumeType.TO_TOPIC[gachamaster.consumetype])
        url = OSAUtil.addQuery(url, Defines.URLQUERY_GTYPE, Defines.GachaConsumeType.GTYPE_NAMES[gachamaster.consumetype])
        url = OSAUtil.addQuery(url, Defines.URLQUERY_GTAB, gachamaster.tabengname)
        self.appRedirect(self.makeAppLinkUrlRedirect(url))
    
    @staticmethod
    def write(uid, gachamaster):
        try:
            model_mgr = db_util.run_in_transaction(Handler.tr_write, uid, gachamaster)
            model_mgr.write_end()
        except CabaretError, err:
            if err.code == CabaretError.Code.ALREADY_RECEIVED:
                pass
            else:
                raise
    
    @staticmethod
    def tr_write(uid, seatid):
        """ボックスの中身をリセット.
        """
        model_mgr = ModelRequestMgr()
        BackendApi.tr_reset_gachaseatplaydata(model_mgr, uid, seatid)
        model_mgr.write_all()
        return model_mgr
    

def main(request):
    return Handler.run(request)
