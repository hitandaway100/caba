# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.views.application.card.boxbase import BoxHandler
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from defines import Defines


class Handler(BoxHandler):
    """異動.
    """
    
    def makeUrlSelf(self):
        return UrlMaker.transfer()
    
    def __getCardlist(self, model_mgr, uid):
        if self.__cardlist is None:
            ctype = self.getCtype()
            sortby = self.getSortby()
            rare = self.getMaxRare()
            self.__cardlist = BackendApi.get_album_addable_cardlist(model_mgr, uid, ctype=ctype, rare=rare, sortby=sortby, using=settings.DB_READONLY)
        return self.__cardlist
    
    def getCardlist(self, model_mgr, uid, offset, limit):
        cardlist = self.__getCardlist(model_mgr, uid)[offset:(offset+limit)]
        albumlist = list(set([cardset.master.album for cardset in cardlist]))
        self.__cardstock_models = BackendApi.get_cardstocks(model_mgr, uid, albumlist, using=settings.DB_READONLY)
        return cardlist
    
    def getCardPageNumMax(self, model_mgr, uid):
        num = len(self.__getCardlist(model_mgr, uid))
        page = max(1, int((num + self.PAGE_CONTENT_NUM - 1) / self.PAGE_CONTENT_NUM))
        return page
    
    def makeCardObject(self, cardset, deck):
        obj_card = Objects.card(self, cardset, deck=deck)
        # ストック可能な数を埋め込む.
        stocknum = self.__getStockNum(cardset.master.album)
        obj_card.update(stock_num=stocknum, stockable_num=max(0, Defines.ALBUM_STOCK_NUM_MAX - stocknum))
        return obj_card
    
    @classmethod
    def getCacheNameSpaceBase(self):
        return 'transfercard:%s'
    
    def __getStockNum(self, album):
        stockmodel = self.__cardstock_models.get(album)
        return stockmodel.num if stockmodel else 0
    
    def process(self):
        self.__cardlist = None
        self.__cardstock_models = {}
        
        self.loadSortParams(default_maxrare=Defines.Rarity.RARE)
        
        self.putCardList()
        
        url = UrlMaker.transferyesno()
        self.html_param['url_transferyesno'] = self.makeAppLinkUrl(url)
        
        self.writeBoxHtml('card/transfer')

def main(request):
    return Handler.run(request)
