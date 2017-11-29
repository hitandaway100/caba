# -*- coding: utf-8 -*-
import settings
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.util.api import BackendApi, Objects
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from defines import Defines
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.card import CardUtil
import settings_sub
from platinumegg.app.cabaret.models.Player import PlayerRequest


class Handler(AppHandler):
    """異動確認.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerRequest]
    
    def __writeError(self, cabareterror):
        if settings_sub.IS_DEV:
            raise cabareterror
        else:
            url = UrlMaker.transfer()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
    
    def process(self):
        
        v_player = self.getViewerPlayer()
        model_mgr = self.getModelMgr()
        
        try:
            cardidlist = []
            for i in xrange(Defines.BOX_PAGE_CONTENT_NUM):
                str_cardid = self.request.get('%s%s' % (Defines.URLQUERY_CARD, i), None)
                if str_cardid and str_cardid.isdigit():
                    cardidlist.append(int(str_cardid))
            
            str_cardidlist = self.request.get(Defines.URLQUERY_CARD, None)
            if str_cardidlist:
                cardidlist.extend([int(str_cardid) for str_cardid in str_cardidlist.split(',')])
            
            if len(cardidlist) == 0:
                raise
        except:
            self.__writeError(CabaretError(u'不正なアクセスです', CabaretError.Code.ILLEGAL_ARGS))
            return
        
        cardidlist = list(set(cardidlist))
        cardlist = BackendApi.get_cards(cardidlist, model_mgr, using=settings.DB_READONLY)
        if len(cardlist) != len(cardidlist):
            self.__writeError(CabaretError(u'キャストが見つかりませんでした', CabaretError.Code.NOT_DATA))
            return
        
        deck = BackendApi.get_deck(v_player.id, model_mgr, using=settings.DB_READONLY)
        raid_deck = BackendApi.get_raid_deck(v_player.id, model_mgr, using=settings.DB_READONLY)
        
        cardobjlist = []
        
        # 成長したキャストを含んでいるか.
        include_growth = False
        # ハメ管理度が上がっているキャストを選んでいるか.
        include_hkincr_already = False
        
        url_base = UrlMaker.transferyesno()
        
        str_idlist = []
        albumidlist = []
        for cardset in cardlist:
            str_idlist.append(str(cardset.id))
            albumidlist.append(cardset.master.album)
        
        # 現在のストック数.
        cur_stocknum_models = BackendApi.get_cardstocks(model_mgr, v_player.id, list(set(albumidlist)), using=settings.DB_READONLY)
        stocknums = {}
        def getStockNum(album):
            model = cur_stocknum_models.get(album)
            num = model.num if model else 0
            return num + stocknums.get(album, 0)
        
        for cardset in cardlist:
            if not CardUtil.checkStockable(v_player.id, deck, cardset, raise_on_error=False) or raid_deck.is_member(cardset.id):
                self.__writeError(CabaretError(u'異動できないキャストが含まれています', CabaretError.Code.ILLEGAL_ARGS))
                return
            elif Defines.ALBUM_STOCK_NUM_MAX <= getStockNum(cardset.master.album):
                # 何かチェックが漏れてここに来た.
                self.__writeError(CabaretError(u'異動上限を超えます', CabaretError.Code.OVER_LIMIT))
                return
            album = cardset.master.album
            stocknums[album] = stocknums.get(album, 0) + 1
            
            obj_card = Objects.card(self, cardset)
            
            tmp = str_idlist[:]
            tmp.remove(str(cardset.id))
            if 0 < len(tmp):
                url = OSAUtil.addQuery(url_base, Defines.URLQUERY_CARD, ','.join(tmp))
            else:
                url = UrlMaker.transfer()
            obj_card['url_remove'] = self.makeAppLinkUrl(url)
            
            cardobjlist.append(obj_card)
            
            include_growth = include_growth or 0 < cardset.card.exp
            include_hkincr_already = include_hkincr_already or 1 < cardset.master.hklevel
        
        self.html_param['cardlist'] = cardobjlist
        
        self.html_param['flag_include_growth'] = include_growth
        self.html_param['flag_include_hkincr_already'] = include_hkincr_already
        
        url = UrlMaker.transferdo(v_player.req_confirmkey)
        url = OSAUtil.addQuery(url, Defines.URLQUERY_CARD, ','.join(str_idlist))
        self.html_param['url_transferdo'] = self.makeAppLinkUrl(url)
        
        self.writeAppHtml('card/transferyesno')
    

def main(request):
    return Handler.run(request)
