# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.views.application.card.boxbase import BoxHandler
from platinumegg.app.cabaret.util.api import Objects, BackendApi
import settings
from defines import Defines
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.models.Player import PlayerDeck


class Handler(BoxHandler):
    """デッキメンバー選択.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerDeck]
    
    def makeUrlSelf(self):
        return OSAUtil.addQuery(UrlMaker.deckmember(self.__target), Defines.URLQUERY_INDEX, self.__selected_index)
    
    def getDeckCardIdList(self):
        return self.__deck.to_array()
    
    def __getCardList(self, model_mgr, uid, limit=-1, offset=0):
        if self.__cardlist is None:
            ctype = self.getCtype()
            sortby = self.getSortby()
            self.__cardlist = BackendApi.get_card_list_by_cost(uid, 0, self.__cost_max, ctype=ctype, sortby=sortby, arg_model_mgr=model_mgr, using=settings.DB_READONLY)
        if limit == -1:
            return self.__cardlist[offset:]
        else:
            return self.__cardlist[offset:(offset+limit)]
    
    def getCardlist(self, model_mgr, uid, offset, limit):
        cardlist = self.__getCardList(model_mgr, uid, limit, offset)
        return cardlist
    
    def getCardPageNumMax(self, model_mgr, uid):
        cardlist = self.__getCardList(model_mgr, uid)
        num = len(cardlist)
        page = max(1, int((num + self.PAGE_CONTENT_NUM - 1) / self.PAGE_CONTENT_NUM))
        return page
    
    def makeCardObject(self, cardset, deck):
        data = Objects.card(self, cardset, deck=deck)
        url = UrlMaker.deckset(target=self.__target)
        url = OSAUtil.addQuery(url, Defines.URLQUERY_INDEX, self.__selected_index)
        url = OSAUtil.addQuery(url, Defines.URLQUERY_CARD, cardset.id)
        data['url_deck'] = self.makeAppLinkUrl(url)
        return data
    
    def process(self):
        
        args = self.getUrlArgs('/deckmember/')
        target = args.get(0)
        
        self.__cardlist = None
        
        self.loadSortParams()
        try:
            idx = int(self.request.get(Defines.URLQUERY_INDEX, None))
        except:
            raise CabaretError(u'引数が想定外です', CabaretError.Code.ILLEGAL_ARGS)
        self.__selected_index = idx
        
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        uid = v_player.id
        
        deck = None
        if target == 'raid':
            # レイド.
            deck = BackendApi.get_raid_deck(uid, model_mgr, using=settings.DB_READONLY)
        else:
            target = 'normal'
            deck = BackendApi.get_deck(uid, model_mgr, using=settings.DB_READONLY)
        self.__target = target
        self.__deck = deck
        
        deck_idlist = deck.to_array()
        deck_cardlist = BackendApi.get_cards(deck_idlist, model_mgr, using=settings.DB_READONLY)
        idx = min(max(0, idx), len(deck_cardlist))
        
        if idx < len(deck_cardlist):
            # 設定中のカード.
            current_card = Objects.card(self, deck_cardlist[idx], deck=deck)
            url = None
            if 0 < idx:
                url = OSAUtil.addQuery(UrlMaker.deckset(target=target), Defines.URLQUERY_CARD, deck_cardlist[idx].id)
                url = OSAUtil.addQuery(url, Defines.URLQUERY_INDEX, -1)
                url = self.makeAppLinkUrl(url)
            current_card['url_remove'] = url
            self.html_param['current_card'] = current_card
        
        cost = 0
        for i in xrange(len(deck_cardlist)):
            if i == idx:
                continue
            cost += deck_cardlist[i].master.cost
        rest = v_player.deckcapacity - cost
        self.__cost_max = rest
        
        self.putCardList()
        
        # 店舗に配属されているキャスト.
        store_castidlist = BackendApi.get_cabaretclub_active_cast_list(model_mgr, uid, OSAUtil.get_now(), using=settings.DB_READONLY)
        self.html_param['store_castidlist'] = store_castidlist
        
        self.html_param['deck_edit_target'] = target
        
        self.writeBoxHtml('deck/member')

def main(request):
    return Handler.run(request)
