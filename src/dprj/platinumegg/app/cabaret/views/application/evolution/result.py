# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.views.application.evolution.base import EvolutionHandler
from platinumegg.app.cabaret.models.Player import PlayerGold
from platinumegg.app.cabaret.util.api import BackendApi, Objects
from platinumegg.app.cabaret.util.cabareterror import CabaretError
import settings
import settings_sub
from copy import copy
from platinumegg.app.cabaret.util.card import CardSet


class Handler(EvolutionHandler):
    """進化合成アニメ.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerGold]
    
    def process(self):
        v_player = self.getViewerPlayer()
        model_mgr = self.getModelMgr()
        
        # 合成結果.
        evolutiondata = BackendApi.get_evolutiondata(model_mgr, v_player.id, using=settings.DB_READONLY)
        
        # ベースカード.
        basecardset = BackendApi.get_cards([evolutiondata.result_baseid], model_mgr, using=settings.DB_READONLY)
        if not basecardset:
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'ハメ管理したキャストが見つかりません.')
            url = UrlMaker.evolution()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        basecardset = basecardset[0]
        self.html_param['basecard_post'] = Objects.card(self, basecardset)
        
        pre_master = BackendApi.get_cardmasters([evolutiondata.mid], model_mgr, using=settings.DB_READONLY).get(evolutiondata.mid)
        if pre_master is None or (pre_master.albumhklevel+1) != basecardset.master.albumhklevel:
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'ハメ管理前のキャストが見つかりません.')
            url = UrlMaker.evolution()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        pre_card = copy(basecardset.card)
        evolutiondata.set_to_card(pre_card)
        pre_cardset = CardSet(pre_card, pre_master)
        self.html_param['basecard_pre'] = Objects.card(self, pre_cardset)
        
        # 素材カード.
        materialcard = BackendApi.get_cards([evolutiondata.result_materialid], model_mgr, using=settings.DB_READONLY, deleted=True)
        if not materialcard:
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'ハメ管理に使用したキャストが見つかりません.')
            url = UrlMaker.evolution()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        self.html_param['materialcard'] = Objects.card(self, materialcard[0])
        
        self.writeAppHtml('evolution/complete')

def main(request):
    return Handler.run(request)
