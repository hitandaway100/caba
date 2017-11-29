# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.models.Player import PlayerGold
from platinumegg.app.cabaret.util.api import Objects, BackendApi
import settings
from platinumegg.app.cabaret.views.application.evolution.base import EvolutionHandler
from defines import Defines

class Handler(EvolutionHandler):
    """進化合成ベースカード選択.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerGold]
    
    @classmethod
    def getCacheNameSpaceBase(self):
        return 'evolution:base:%s'
    
    def makeUrlSelf(self):
        return UrlMaker.evolution()
    
    def __getCardlist(self, model_mgr, uid):
        if self.__cardlist is None:
            ctype = self.getCtype()
            sortby = self.getSortby()
            self.__cardlist = BackendApi.get_evolutionbase_list(uid, ctype=ctype, sortby=sortby, arg_model_mgr=model_mgr, using=settings.DB_READONLY)
        return self.__cardlist
    
    def getCardlist(self, model_mgr, uid, offset, limit):
        cardlist = self.__getCardlist(model_mgr, uid)
        return cardlist[offset:(offset+limit)]
    
    def getCardPageNumMax(self, model_mgr, uid):
        num = len(self.__getCardlist(model_mgr, uid))
        page = max(1, int((num + self.PAGE_CONTENT_NUM - 1) / self.PAGE_CONTENT_NUM))
        return page
    
    def process(self):
        
        self.__cardlist = None
        
        model_mgr = self.getModelMgr()
        
        self.loadSortParams(default_sortby=Defines.CardSortType.HKLEVEL_REV)
        
        # プレイヤー情報.
        v_player = self.getViewerPlayer()
        self.html_param['player'] = Objects.player(self, v_player)
        
        # カード所持数.
        cardnum = BackendApi.get_cardnum(v_player.id, model_mgr, using=settings.DB_READONLY)
        self.html_param['cardnum'] = cardnum
        
        # カード.
        self.putCardList()
        
        self.writeEvolutionHtml('evolution/baseselect')

def main(request):
    return Handler.run(request)
