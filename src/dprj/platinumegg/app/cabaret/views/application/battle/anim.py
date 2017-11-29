# -*- coding: utf-8 -*-
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.views.application.battle.base import BattleHandler
from platinumegg.app.cabaret.util.cabareterror import CabaretError
import settings_sub


class Handler(BattleHandler):
    """バトル演出.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        
        # 結果データ.
        battleresult = BackendApi.get_battleresult(model_mgr, v_player.id, using=settings.DB_READONLY)
        if battleresult is None or not battleresult.anim:
            # 結果が存在しない.
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'結果がない')
            url = UrlMaker.battle()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        
        # 演出用パラメータ.
        dataUrl = self.makeAppLinkUrlEffectParamGet('battle')
        self.appRedirectToEffect2('battle2/effect2.html', dataUrl)

def main(request):
    return Handler.run(request)
