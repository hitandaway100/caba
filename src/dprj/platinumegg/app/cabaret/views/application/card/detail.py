# -*- coding: utf-8 -*-
import settings
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.util.api import BackendApi, Objects
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.card import CardUtil
from defines import Defines
from platinumegg.lib.opensocial.util import OSAUtil


class Handler(AppHandler):
    """カード詳細.
    """
    
    def process(self):
        
        v_player = self.getViewerPlayer()
        
        args = self.getUrlArgs('/carddetail/')
        strcardid = args.get(0, None)
        
        model_mgr = self.getModelMgr()
        
        cardset = None
        if strcardid and strcardid.isdigit():
            cardid = int(strcardid)
            cardlist = BackendApi.get_cards([cardid], model_mgr, using=settings.DB_READONLY)
            if cardlist:
                cardset = cardlist[0]
        if cardset is None or cardset.card.uid != v_player.id:
            raise CabaretError(u'閲覧できないキャストです', CabaretError.Code.ILLEGAL_ARGS)
        
        if self.getFromPageName() == Defines.FromPages.CARDBOX:
            url = UrlMaker.cardbox()
            args = self.getFromPageArgs()
            if args and len(args) == 3:
                ctype, sortby, page = args
                url = OSAUtil.addQuery(url, Defines.URLQUERY_CTYPE, ctype)
                url = OSAUtil.addQuery(url, Defines.URLQUERY_SORTBY, sortby)
                url = OSAUtil.addQuery(url, Defines.URLQUERY_PAGE, page)
            self.html_param['url_back'] = self.makeAppLinkUrl(url, add_frompage=False)
        elif self.getFromPageName() == Defines.FromPages.DECK_RAID:
            url = UrlMaker.deck_raid()
            self.html_param['url_back'] = self.makeAppLinkUrl(url, add_frompage=False)
        elif self.getFromPageName() == Defines.FromPages.DECK_NORMAL:
            url = UrlMaker.deck()
            self.html_param['url_back'] = self.makeAppLinkUrl(url, add_frompage=False)
        
        deck = BackendApi.get_deck(v_player.id, model_mgr, using=settings.DB_READONLY)
        raid_deck = BackendApi.get_raid_deck(v_player.id, model_mgr, using=settings.DB_READONLY)
        cardidlist = []
        cardidlist.extend(deck.to_array())
        cardidlist.extend(raid_deck.to_array())
        
        self.html_param['card'] = Objects.card(self, cardset, deck=cardidlist)
        
        is_stockable = False
        is_stock_overlimit = False
        if CardUtil.checkStockable(v_player.id, deck, cardset, raise_on_error=False):
            stocknum_model = BackendApi.get_cardstock(model_mgr, v_player.id, cardset.master.album, using=settings.DB_READONLY)
            num = stocknum_model.num if stocknum_model else 0
            is_stock_overlimit = Defines.ALBUM_STOCK_NUM_MAX <= num
            is_stockable = True
        self.html_param['is_stockable'] = is_stockable
        self.html_param['is_stock_overlimit'] = is_stock_overlimit
        
        self.writeAppHtml('card/carddetail')
    

def main(request):
    return Handler.run(request)
