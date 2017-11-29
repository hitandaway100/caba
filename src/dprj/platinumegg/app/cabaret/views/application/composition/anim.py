# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.views.application.composition.base import CompositionHandler
from platinumegg.app.cabaret.models.Player import PlayerGold
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.cabareterror import CabaretError
import settings
import settings_sub


class Handler(CompositionHandler):
    """合成アニメ.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerGold]
    
    def process(self):
        v_player = self.getViewerPlayer()
        model_mgr = self.getModelMgr()
        
        # 合成結果.
        compositiondata = BackendApi.get_compositiondata(model_mgr, v_player.id, using=settings.DB_READONLY)
        
        # ベースカード.
        basecardset = BackendApi.get_cards([compositiondata.result_baseid], model_mgr, using=settings.DB_READONLY)
        if not basecardset or basecardset[0].card.mid != compositiondata.mid:
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'教育したキャストが見つかりません.')
            url = UrlMaker.composition()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        basecardset = basecardset[0]
        
        # 素材カード.
        materialcardsetlist = BackendApi.get_cards(compositiondata.result_materialidlist, model_mgr, using=settings.DB_READONLY, deleted=True)
        
        exp_pre = compositiondata.result_exp_pre
        exp_add = compositiondata.result_exp
        level_pre = compositiondata.result_lvpre
        level_add = compositiondata.result_lvup
        skilllevelup = compositiondata.result_skilllvup
        is_great_success = compositiondata.result_flag_great_success
        params = BackendApi.make_composition_effectparams(self, basecardset, materialcardsetlist, exp_pre, exp_add, level_pre, level_add, skilllevelup, is_great_success)
        
        # 結果へのURL.
        url = UrlMaker.compositionresult()
        params['backUrl'] = self.makeAppLinkUrl(url)
        
        self.appRedirectToEffect('education/effect.html', params)

def main(request):
    return Handler.run(request)
