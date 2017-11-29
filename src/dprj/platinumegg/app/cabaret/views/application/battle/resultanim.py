# -*- coding: utf-8 -*-
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.views.application.battle.base import BattleHandler
from platinumegg.app.cabaret.util.cabareterror import CabaretError
import settings_sub


class Handler(BattleHandler):
    """バトル結果演出.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        self.__swf_params = {}
        
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        
        # 結果データ.
        battleresult = BackendApi.get_battleresult(model_mgr, v_player.id, using=settings.DB_READONLY)
        if battleresult is None:
            # 結果が存在しない.
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'結果がない')
            url = UrlMaker.battle()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        
        url = UrlMaker.battleresult()
        self.__swf_params['backUrl'] = self.makeAppLinkUrl(url)
        
        # 結果によって演出を変更.
        data = battleresult.data
        if data['is_win']:
            if data['rankup']:
                self.appRedirectToEffect('shuttenkanryou/effect.html', self.__swf_params)
            elif data['norma_comp']:
                self.appRedirectToEffect('normaclear/effect.html', self.__swf_params)
            else:
                self.appRedirectToEffect('youwin/effect.html', self.__swf_params)
        else:
            self.appRedirectToEffect('youlose/effect.html', self.__swf_params)
        
    

def main(request):
    return Handler.run(request)
