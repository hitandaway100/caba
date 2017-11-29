# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.models.Player import PlayerGold
from platinumegg.app.cabaret.util.api import Objects, BackendApi
import settings
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.lib.opensocial.util import OSAUtil
from defines import Defines
from platinumegg.app.cabaret.views.application.evolution.base import EvolutionHandler


class Handler(EvolutionHandler):
    """進化合成素材カード選択.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerGold]
    
    @classmethod
    def getCacheNameSpaceBase(self):
        return 'evolution:material:%s'
    
    def makeUrlSelf(self):
        return UrlMaker.evolutionmaterial(self.__baseid)
    
    def makeCardObject(self, cardset, deck):
        obj_card = Objects.card(self, cardset, deck=deck)
        url = OSAUtil.addQuery(UrlMaker.evolutionyesno(self.__baseid), Defines.URLQUERY_CARD, cardset.card.id)
        obj_card['url_evolution'] = self.makeAppLinkUrl(url)
        return obj_card
    
    def __getCardlist(self, model_mgr, uid):
        if self.__cardlist is None:
            self.__cardlist = BackendApi.get_evolutionmaterial_list(uid, self.__basecard, arg_model_mgr=model_mgr, using=settings.DB_READONLY)
        return self.__cardlist
    
    def getCardlist(self, model_mgr, uid, offset, limit):
        cardlist = self.__getCardlist(model_mgr, uid)
        return cardlist[offset:(offset + limit)]
    
    def getCardPageNumMax(self, model_mgr, uid):
        num = len(self.__getCardlist(model_mgr, uid))
        page = max(1, int((num + self.PAGE_CONTENT_NUM - 1) / self.PAGE_CONTENT_NUM))
        return page
    
    def process(self):
        
        self.__cardlist = None
        
        args = self.getUrlArgs('/evolutionmaterial/')
        try:
            self.__baseid = int(args.get(0))
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
        
        self.loadSortParams()
        
        # プレイヤー情報.
        self.html_param['player'] = Objects.player(self, v_player)
        
        # カード所持数.
        cardnum = BackendApi.get_cardnum(v_player.id, model_mgr, using=settings.DB_READONLY)
        self.html_param['cardnum'] = cardnum
        
        # カード.
        self.putCardList()
        
        self.writeEvolutionHtml('evolution/materialselect')

def main(request):
    return Handler.run(request)
