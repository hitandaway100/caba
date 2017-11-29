# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.models.Player import PlayerDeck
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from defines import Defines
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util import db_util
from platinumegg.lib.opensocial.util import OSAUtil
import settings_sub


class Handler(AppHandler):
    """デッキ変更書き込み.
    _idxに_cardを設定する.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerDeck]
    
    def process(self):
        args = self.getUrlArgs('/deckset/')
        
        try:
            is_auto = int(args.get(0, 0) or 0)
            target = args.get(1)
        except:
            raise CabaretError(u'引数が想定外です', CabaretError.Code.ILLEGAL_ARGS)
        
        if is_auto:
            self.processAuto(target)
        else:
            self.processNormal(target)
        
        url = UrlMaker.deck(target=target)
        selected_id = str(self.request.get(Defines.URLQUERY_CURRENT))
        if selected_id and selected_id.isdigit():
            url = OSAUtil.addQuery(url, Defines.URLQUERY_CARD, selected_id)
        if settings_sub.IS_BENCH:
            self.response.set_status(200)
            self.response.send()
        else:
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
    
    def processAuto(self, target):
        """自動設定.
        どうするのがいいんだろうか..
        """
        v_player = self.getViewerPlayer()
        model_mgr = self.getModelMgr()
        deckcapacity = v_player.deckcapacity
        uid = v_player.id
        
        if target == 'raid':
            # レイド.
            deck = BackendApi.get_raid_deck(uid, model_mgr, using=settings.DB_READONLY)
        else:
            deck = BackendApi.get_deck(uid, model_mgr, using=settings.DB_READONLY)
        
        deck_cardidlist = []
        cost_total = 0
        leader_id = 0
        if deck.leader:
            leader = BackendApi.get_cards([deck.leader], model_mgr, using=settings.DB_READONLY)
            if leader:
                leader = leader[0]
                cost = leader.master.cost
                if (cost + cost_total) <= deckcapacity:
                    deck_cardidlist.append(leader.id)
                    cost_total += cost
                    leader_id = leader.id
        
        if cost_total < deckcapacity:
            # 店舗に配属されているキャスト.
            store_castidlist = BackendApi.get_cabaretclub_active_cast_list(model_mgr, uid, OSAUtil.get_now())
            filter_func = lambda x,y:x.id not in store_castidlist
            cardlist = BackendApi.get_card_list_by_cost(v_player.id, 0, deckcapacity - cost_total, sortby=Defines.CardSortType.POWER_REV, arg_model_mgr=model_mgr, using=settings.DB_READONLY, filter_func=filter_func)
            while 0 < len(cardlist) and len(deck_cardidlist) < Defines.DECK_CARD_NUM_MAX:
                card = cardlist.pop(0)
                cost = card.master.cost
                if (cost + cost_total) <= deckcapacity and card.id != leader_id and card.master.ckind == Defines.CardKind.NORMAL:
                    deck_cardidlist.append(card.id)
                    cost_total += cost
        
        # 書き込み.
        if target == 'raid':
            wrote_model_mgr = db_util.run_in_transaction(Handler.tr_write_raid, v_player, deck_cardidlist)
        else:
            wrote_model_mgr = db_util.run_in_transaction(Handler.tr_write, v_player, deck_cardidlist)
        wrote_model_mgr.write_end()
    
    def processNormal(self, target):
        """通常設定.
        """
        try:
            # 選択したカード.
            cardid = int(self.request.get(Defines.URLQUERY_CARD))
            # 設定する場所.
            idx = int(self.request.get(Defines.URLQUERY_INDEX))
        except:
            raise CabaretError(u'引数が想定外です', CabaretError.Code.ILLEGAL_ARGS)
        
        v_player = self.getViewerPlayer()
        model_mgr = self.getModelMgr()
        uid = v_player.id
        
        if target == 'raid':
            # レイド.
            deck = BackendApi.get_raid_deck(uid, model_mgr, using=settings.DB_READONLY)
        else:
            deck = BackendApi.get_deck(uid, model_mgr, using=settings.DB_READONLY)
        
        # デッキ.
        cardidlist = deck.to_array()
        if idx == -1:
            # デッキから指定のカードを外す.
            if deck.leader == cardid:
                raise CabaretError(u'No.1は外せません', CabaretError.Code.ILLEGAL_ARGS)
            elif cardid in cardidlist:
                cardidlist.remove(cardid)
            else:
                # 設定済み.
                return
        else:
            idx = min(max(0, idx), len(cardidlist))
            if cardid in cardidlist:
                if idx < len(cardidlist):
                    if cardidlist[idx] == cardid:
                        # 設定済み.
                        return
                    else:
                        # 入れ替え.
                        cardidlist[cardidlist.index(cardid)] = cardidlist[idx]
                        cardidlist[idx] = cardid
                else:
                    # 削除して末尾に追加.
                    cardidlist.remove(cardid)
                    cardidlist.append(cardid)
            else:
                if idx < len(cardidlist):
                    cardidlist[idx] = cardid
                else:
                    # 末尾に追加.
                    cardidlist.append(cardid)
        
        # 書き込み.
        if target == 'raid':
            wrote_model_mgr = db_util.run_in_transaction(Handler.tr_write_raid, v_player, cardidlist)
        else:
            wrote_model_mgr = db_util.run_in_transaction(Handler.tr_write, v_player, cardidlist)
        wrote_model_mgr.write_end()
    
    def processList(self, target):
        """一括設定.
        """
        model_mgr = self.getModelMgr()
        
        try:
            # 選択したカード.
            cardidlist = list(set([int(strcardid) for strcardid in self.request.get(Defines.URLQUERY_CARD).split(',')]))
            if not cardidlist:
                raise CabaretError()
        except:
            raise CabaretError(u'設定できないキャストです', CabaretError.Code.ILLEGAL_ARGS)
        
        v_player = self.getViewerPlayer()
        
        if target == 'raid':
            # 書き込み.
            model_mgr = db_util.run_in_transaction(Handler.tr_write_raid, v_player, cardidlist)
        else:
            # 書き込み.
            model_mgr = db_util.run_in_transaction(Handler.tr_write, v_player, cardidlist)
        model_mgr.write_end()
    
    @staticmethod
    def tr_write(v_player, cardidlist):
        """書き込み.
        """
        model_mgr = ModelRequestMgr()
        BackendApi.set_deck(v_player, cardidlist, model_mgr)
        model_mgr.write_all()
        return model_mgr
    
    @staticmethod
    def tr_write_raid(v_player, cardidlist):
        """書き込み.
        """
        model_mgr = ModelRequestMgr()
        BackendApi.set_raid_deck(v_player, cardidlist, model_mgr)
        model_mgr.write_all()
        return model_mgr


def main(request):
    return Handler.run(request)
