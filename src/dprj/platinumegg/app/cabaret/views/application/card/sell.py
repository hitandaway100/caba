# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.views.application.card.boxbase import BoxHandler
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from platinumegg.app.cabaret.util.card import CardListFilter


class Handler(BoxHandler):
    """カード売却.
    絞り込み.
        すべて.
        小悪魔.
        大和撫子.
        ツンデレ.
    ソート.
        新着順.
        古い順.
        レアリティが高い順.
        レアリティが低い順.
        レベルが高い順.
        レベルが低い順.
        コストが高い順.
        コストが低い順.
        接客力が高い順.
        接客力が低い順.
    ページング.
    """
    
    def makeUrlSelf(self):
        return UrlMaker.sell()
    
    def __getCardlist(self, model_mgr, uid):
        if self.__cardlist is None:
            ctype = self.getCtype()
            sortby = self.getSortby()
            ckindlist = self.getCKindList()
            maxrare = self.getMaxRare()
            filter_obj = CardListFilter(ctype=ctype, maxrare=maxrare, ckind=ckindlist)
            self.__cardlist = BackendApi.get_sellcard_list(uid, filter_obj=filter_obj, sortby=sortby, arg_model_mgr=model_mgr, using=settings.DB_READONLY)
        return self.__cardlist
    
    def getCardlist(self, model_mgr, uid, offset, limit):
        return self.__getCardlist(model_mgr, uid)[offset:(offset+limit)]
    
    def getCardPageNumMax(self, model_mgr, uid):
        num = len(self.__getCardlist(model_mgr, uid))
        page = max(1, int((num + self.PAGE_CONTENT_NUM - 1) / self.PAGE_CONTENT_NUM))
        return page
    
    @classmethod
    def getCacheNameSpaceBase(self):
        return 'sellcard:%s'
    
    def process(self):
        self.__cardlist = None
        
        self.loadSortParams()
        
        self.putCardList()
        
        url = UrlMaker.sellyesno()
        self.html_param['url_sellyesno'] = self.makeAppLinkUrl(url)
        
        self.writeBoxHtml('card/sell')

def main(request):
    return Handler.run(request)
