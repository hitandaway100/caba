# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.views.application.happening.base import HappeningHandler
import settings_sub
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util import db_util
from defines import Defines


class Handler(HappeningHandler):
    """レイド救援依頼送信.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        
        v_player = self.getViewerPlayer()
        
        happeningraidset = self.getHappeningRaidSet()
        if happeningraidset is None or not happeningraidset.happening.happening.is_boss_appeared():
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'レイドが発生していない')
            url = self.makeAppLinkUrlRedirect(UrlMaker.happening())
            self.appRedirect(url)
            return
        
        # レイド情報.
        raidboss = happeningraidset.raidboss
        if raidboss is None:
            raise CabaretError(u'レイド情報がありません', CabaretError.Code.UNKNOWN)
        elif not raidboss.raid.helpflag:
            to_other = self.request.get(Defines.URLQUERY_FLAG) == "1"
            
            try:
                model_mgr = db_util.run_in_transaction(self.tr_write, v_player.id, to_other)
                model_mgr.write_end()
            except CabaretError:
                if settings_sub.IS_LOCAL:
                    raise
        
        url = self.makeAppLinkUrlRedirect(self.makeLinkRaidBattlePre(happeningraidset))
        self.appRedirect(url)
    
    def tr_write(self, uid, to_other):
        """DB書き込み.
        """
        model_mgr = ModelRequestMgr(loginfo=self.addloginfo)
        BackendApi.tr_send_raidhelp(model_mgr, uid, to_other)
        model_mgr.write_all()
        return model_mgr

def main(request):
    return Handler.run(request)
