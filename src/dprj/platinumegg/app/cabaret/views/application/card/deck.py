# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.models.Player import PlayerDeck
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from defines import Defines
import settings_sub
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.models.Card import Deck
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util import db_util


class Handler(AppHandler):
    """デッキ編成.
    現在のデッキメンバー.
    総コスト.
    コスト上限.
    総接客力.
    自動選択へのURL.
    追加するURL.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerDeck]
    
    def process(self):
        
        args = self.getUrlArgs('/deck/')
        target = args.get(0)
        
        v_player = self.getViewerPlayer()
        model_mgr = self.getModelMgr()
        uid = v_player.id
        
        # デッキ.
        deck = None
        if target == 'raid':
            self.setFromPage(Defines.FromPages.DECK_RAID, [])
            deck = BackendApi.get_raid_deck(uid, model_mgr, using=settings.DB_READONLY)
            if isinstance(deck, Deck):
                # 通常のデッキをレイドデッキに移す.
                def tr(cardidlist):
                    model_mgr = ModelRequestMgr()
                    BackendApi.set_raid_deck(v_player, cardidlist, model_mgr)
                    model_mgr.write_all()
                    return model_mgr
                db_util.run_in_transaction(tr, deck.to_array()).write_end()
        
        if deck is None:
            target = 'normal'
            self.setFromPage(Defines.FromPages.DECK_NORMAL, [])
            deck = BackendApi.get_deck(uid, model_mgr, using=settings.DB_READONLY)
        
        cardidlist = deck.to_array()
        
        # メンバーに加えるカードを先に選択するフローがあるので引数にカードのIDが来ることがある.
        arg_card_id = self.request.get(Defines.URLQUERY_CARD, None)
        selected_card = None
        selected_card_cost = 0
        if arg_card_id:
            try:
                arg_card_id = int(arg_card_id)
                if arg_card_id in cardidlist:
                    # デッキに設定済み.
                    arg_card_id = None
                else:
                    cardset = BackendApi.get_cards([arg_card_id], model_mgr, using=settings.DB_READONLY)[0]
                    if cardset.card.uid != v_player.id:
                        arg_card_id = None
                    else:
                        self.html_param['selected_card'] = Objects.card(self, cardset)
                        selected_card = cardset
                        selected_card_cost = selected_card.master.cost
            except:
                if settings_sub.IS_LOCAL:
                    raise
        
        # カードを取得.
        cardlist = BackendApi.get_cards(cardidlist, model_mgr, using=settings.DB_READONLY)
        
        url = UrlMaker.deckset(auto=True, target=target)
        self.html_param['url_auto'] = self.makeAppLinkUrl(url)
        if len(cardlist) == 0:
            # どうしようか..自動選択に飛ばしておくか..
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        
        if selected_card:
            urlbase = OSAUtil.addQuery(UrlMaker.deckset(target=target), Defines.URLQUERY_CARD, selected_card.id)
        else:
            urlbase = UrlMaker.deckmember(target=target)
        
        url_removebase = UrlMaker.deckset(target=target)
        if selected_card:
            url_removebase = OSAUtil.addQuery(url_removebase, Defines.URLQUERY_CURRENT, selected_card.id)
        
        obj_cardlist = []
        cost = 0
        power_total = 0
        for cardset in cardlist:
            obj = Objects.card(self, cardset, deck=deck)
            url = OSAUtil.addQuery(urlbase, Defines.URLQUERY_INDEX, len(obj_cardlist))
            obj['url_deck'] = self.makeAppLinkUrl(url)
            
            url = OSAUtil.addQuery(url_removebase, Defines.URLQUERY_CARD, cardset.id)
            url = OSAUtil.addQuery(url, Defines.URLQUERY_INDEX, -1)
            obj['url_remove'] = self.makeAppLinkUrl(url)
            
            obj_cardlist.append(obj)
            
            cost += cardset.master.cost
            power_total += cardset.power
        
        if selected_card_cost:
            for obj_card in obj_cardlist:
                tmp = cost - obj_card['master']['cost'] + selected_card_cost
                if v_player.deckcapacity < tmp:
                    # コストオーバー.
                    obj_card['cost_over'] = True
        
        if len(cardlist) < Defines.DECK_CARD_NUM_MAX and (cost+selected_card_cost) < v_player.deckcapacity:
            url = OSAUtil.addQuery(urlbase, Defines.URLQUERY_INDEX, len(obj_cardlist))
            self.html_param['url_addmember'] = self.makeAppLinkUrl(url)
        
        self.html_param['leader'] = obj_cardlist[0]
        self.html_param['memberlist'] = obj_cardlist[1:]
        
        self.html_param['cost'] = cost
        self.html_param['capacity'] = v_player.deckcapacity
        self.html_param['power_total'] = power_total
        
        self.html_param['deck_edit_target'] = target
        
        self.putFromBackPageLinkUrl()
        
        if self.is_pc:
            self.html_param['change_leader'] = obj_cardlist[0]
        
        self.writeAppHtml('deck/deck')

def main(request):
    return Handler.run(request)
