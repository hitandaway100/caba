# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.views.application.battleevent.base import BattleEventBaseHandler
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from platinumegg.app.cabaret.util.cabareterror import CabaretError
import settings_sub

class Handler(BattleEventBaseHandler):
    """バトルイベントバトル結果演出.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        
        model_mgr = self.getModelMgr()
        
        args = self.getUrlArgs('/battleeventresultanim/')
        eventid = args.getInt(0)
        rarity = args.getInt(1)
        piecenumber = args.getInt(2)
        is_complete = args.getInt(3)

        eventmaster = None
        if eventid:
            eventmaster = BackendApi.get_battleevent_master(model_mgr, eventid, using=settings.DB_READONLY)

        if eventmaster is None:
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'引数がおかしい')
            self.redirectToTop()
            return

        v_player = self.getViewerPlayer()
        uid = v_player.id

        # 結果データ.
        battleresult = BackendApi.get_battleevent_battleresult(model_mgr, eventid, uid, using=settings.DB_READONLY)
        if battleresult is None:
            # 結果が存在しない.
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'結果がない')
            url = UrlMaker.battleevent_top(eventid)
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        
        swf_params = {}
        piecedata = battleresult.data.get('piecedata')
        if piecedata and not piecedata.get('is_item'):
            url = UrlMaker.battleevent_battlepiecepresent(eventid, piecedata['rarity'], piecedata['piece'], piecedata['is_complete'])
        else:
            url = UrlMaker.battleevent_battleresult(eventid)
        
        swf_params['backUrl'] = self.makeAppLinkUrl(url)
        
        # 結果によって演出を変更.
        data = battleresult.data
        if data['is_win']:
            self.appRedirectToEffect('youwin/effect.html', swf_params)
        else:
            self.appRedirectToEffect('youlose/effect.html', swf_params)

def main(request):
    return Handler.run(request)
