# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.views.application.battleevent.base import BattleEventBaseHandler
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from platinumegg.app.cabaret.util.cabareterror import CabaretError
import settings_sub

class Handler(BattleEventBaseHandler):
    """バトルイベントバトル演出.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        
        args = self.getUrlArgs('/battleeventbattleanim/')
        eventid = args.getInt(0)
        rarity = args.getInt(1)
        piecenumber = args.getInt(2)
        is_complete = args.getInt(3)
        if is_complete is None:
            is_complete = 0

        if eventid is None:
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'引数がおかしい')
            self.redirectToTop()
            return
        
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        uid = v_player.id
        
        # 結果データ.
        battleresult = BackendApi.get_battleevent_battleresult(model_mgr, eventid, uid, using=settings.DB_READONLY)
        if battleresult is None or not battleresult.anim:
            # 結果が存在しない.
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'結果がない')
            url = UrlMaker.battleevent_top(eventid)
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        
        # 演出用パラメータ.
        if (not rarity is None) and (not piecenumber is None) and (not is_complete is None):
            dataUrl = self.makeAppLinkUrlEffectParamGet('battleevent/%d/%d/%d/%d/' % (eventid, rarity, piecenumber, is_complete))
        else:
            dataUrl = self.makeAppLinkUrlEffectParamGet('battleevent/%d/' % eventid)

        self.appRedirectToEffect2('battle2/effect2.html', dataUrl)

def main(request):
    return Handler.run(request)
