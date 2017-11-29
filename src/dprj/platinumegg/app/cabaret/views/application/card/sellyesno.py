# -*- coding: utf-8 -*-
import settings
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.util.api import BackendApi, Objects
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from defines import Defines
from platinumegg.app.cabaret.models.Player import PlayerGold, PlayerTreasure
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.card import CardUtil
import settings_sub


class Handler(AppHandler):
    """カード売却確認.
    表示するもの:
        売却するカード一覧.
        売却金額の合計.
        所持金.
        売却後の所持金.
    エラー:
        存在しないカードを選んだ.
        他プレイヤーのカードを選んだ.
        デッキのカードを選んだ.
        保護中のカードを選んだ.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerGold, PlayerTreasure]
    
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
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'不正なアクセスです', CabaretError.Code.ILLEGAL_ARGS)
            url = UrlMaker.sell()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        
        cardidlist = list(set(cardidlist))
        cardlist = BackendApi.get_cards(cardidlist, model_mgr, using=settings.DB_READONLY)
        if len(cardlist) != len(cardidlist):
            raise CabaretError(u'キャストが見つかりませんでした', CabaretError.Code.NOT_DATA)
        
        deck = BackendApi.get_deck(v_player.id, model_mgr, using=settings.DB_READONLY)
        
        cardobjlist = []
        sellprice_total = 0
        sellprice_treasure_total = 0
        
        # レアカードを含んでいるか.
        include_rare = False
        # ハメ管理度が上がっているカードを選んでいるか.
        include_hkincr_already = False
        
        url_base = UrlMaker.sellyesno()
        
        str_idlist = [str(cardset.id) for cardset in cardlist]
        for cardset in cardlist:
            is_rare, hkincr_already = CardUtil.checkSellable(v_player.id, deck, cardset)
            sellprice_total += cardset.sellprice
            sellprice_treasure_total += cardset.sellprice_treasure
            obj_card = Objects.card(self, cardset)
            
            tmp = str_idlist[:]
            tmp.remove(str(cardset.id))
            if 0 < len(tmp):
                url = OSAUtil.addQuery(url_base, Defines.URLQUERY_CARD, ','.join(tmp))
            else:
                url = UrlMaker.sell()
            obj_card['url_remove'] = self.makeAppLinkUrl(url)
            
            cardobjlist.append(obj_card)
            
            include_rare = include_rare or is_rare
            include_hkincr_already = include_hkincr_already or hkincr_already
        
        self.html_param['cardlist'] = cardobjlist
        self.html_param['sellprice'] = sellprice_total
        self.html_param['sellprice_treasure'] = sellprice_treasure_total
        if 0 < sellprice_total:
            self.html_param['gold_pre'] = v_player.gold
            self.html_param['gold_post'] = min(v_player.gold + sellprice_total, Defines.VALUE_MAX)
        if 0 < sellprice_treasure_total:
            self.html_param['treasure_pre'] = v_player.cabaretking
            self.html_param['treasure_post'] = min(v_player.cabaretking + sellprice_treasure_total, Defines.VALUE_MAX)
        
        self.html_param['flag_include_rare'] = include_rare
        self.html_param['flag_include_hkincr_already'] = include_hkincr_already
        
        url = UrlMaker.selldo()
        url = OSAUtil.addQuery(url, Defines.URLQUERY_CARD, ','.join(str_idlist))
        self.html_param['url_selldo'] = self.makeAppLinkUrl(url)
        
        self.writeAppHtml('card/sellyesno')
    

def main(request):
    return Handler.run(request)
