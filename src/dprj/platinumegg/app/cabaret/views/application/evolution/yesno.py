# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.models.Player import PlayerGold, PlayerDeck,\
    PlayerRequest
from platinumegg.app.cabaret.util.api import Objects, BackendApi
import settings
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.lib.opensocial.util import OSAUtil
from defines import Defines
from platinumegg.app.cabaret.views.application.evolution.base import EvolutionHandler
from platinumegg.app.cabaret.util.card import CardSet


class Handler(EvolutionHandler):
    """進化合成確認.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerGold, PlayerDeck, PlayerRequest]
    
    def makeCardObject(self, cardset, deck):
        obj_card = Objects.card(self, cardset, deck=deck)
        if cardset.card.id == self.__baseid or cardset.card.protection or obj_card['deckmember']:
            raise CabaretError(u'ハメ管理に使用できないキャストです.', CabaretError.Code.ILLEGAL_ARGS)
        url = UrlMaker.evolutionmaterial(self.__baseid)
        obj_card['url_evolution'] = self.makeAppLinkUrl(url)
        return obj_card
    
    def process(self):
        args = self.getUrlArgs('/evolutionyesno/')
        try:
            self.__baseid = int(args.get(0))
            self.__materialid = self.getMaterialId()
        except:
            raise CabaretError(u'引数が想定外です', CabaretError.Code.ILLEGAL_ARGS)
        
        v_player = self.getViewerPlayer()
        model_mgr = self.getModelMgr()
        
        # ベースカード.
        basecard = BackendApi.get_cards([self.__baseid], model_mgr, using=settings.DB_READONLY)
        basecard = basecard[0] if len(basecard) else None
        if not self.checkBaseCard(basecard):
            return
        evolmaster = BackendApi.get_evolution_cardmaster(model_mgr, basecard.master, using=settings.DB_READONLY)
        if evolmaster is None:
            raise CabaretError(u'ハメ管理後のキャストが設定されていません.', CabaretError.Code.INVALID_MASTERDATA)
        
        self.html_param['basecard'] = Objects.card(self, basecard)
        self.__basecard = basecard
        
        # プレイヤー情報.
        self.html_param['player'] = Objects.player(self, v_player)
        
        # デッキ情報.
        deck = BackendApi.get_deck(v_player.id, model_mgr, using=settings.DB_READONLY)
        basecard_post = CardSet(basecard.card, evolmaster)
        cost_over, deck_none = BackendApi.check_evol_deckcost(model_mgr, v_player, basecard_post, using=settings.DB_READONLY)
        self.html_param['deckcapacity_over'] = cost_over
        self.html_param['deck_none'] = deck_none
        
        # 素材カード.
        materialcard = BackendApi.get_cards([self.__materialid], model_mgr, using=settings.DB_READONLY)
        materialcard = materialcard[0] if len(materialcard) else None
        if not self.checkMaterialCard(basecard, materialcard, deck):
            return
        self.html_param['materialcard'] = Objects.card(self, materialcard)
        self.__materialcard = materialcard
        
        # 消費ゴールド.
        cost = evolmaster.evolcost
        self.html_param['cost'] = cost
        self.html_param['cost_over'] = v_player.gold < cost
        self.html_param['gold_post'] = v_player.gold - cost
        
        self.html_param['cardnum'] = BackendApi.get_cardnum(v_player.id, model_mgr, using=settings.DB_READONLY)
        
        BackendApi.get_evolutiondata(model_mgr, v_player.id, using=settings.DB_READONLY)
        
        # 書き込みへのURL.
        url = UrlMaker.evolutiondo(self.__baseid, v_player.req_confirmkey)
        self.html_param['url_do'] = self.makeAppLinkUrl(OSAUtil.addQuery(url, Defines.URLQUERY_CARD, self.__materialcard.id))
        
        self.writeAppHtml('evolution/yesno')

def main(request):
    return Handler.run(request)
