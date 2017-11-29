# -*- coding: utf-8 -*-
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.views.application.battle.base import BattleHandler
from platinumegg.app.cabaret.models.Player import PlayerFriend, PlayerAp,\
    PlayerExp, PlayerGold, PlayerCrossPromotion
from platinumegg.app.cabaret.util.cabareterror import CabaretError
import settings_sub
from platinumegg.app.cabaret.util.apprandom import AppRandom
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util import db_util


class Handler(BattleHandler):
    """バトル書き込み.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerFriend, PlayerAp, PlayerExp]
    
    def process(self):
        
        try:
            args = self.getUrlArgs('/battledo/')
            battleid = int(args.get(0, 0))
        except:
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'引数が正しくありません', CabaretError.Code.ILLEGAL_ARGS)
            url = UrlMaker.battle()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        
        # バトル情報.
        battleplayer = self.getBattlePlayer(using=settings.DB_DEFAULT)
        if battleplayer is None:
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'対戦相手が見つかりませんでした', CabaretError.Code.NOT_DATA)
            self.redirectToOppSelect()
            return
        elif battleplayer.result and battleid != battleplayer.result:
            url = self.makeAppLinkUrlRedirect(UrlMaker.battleanim())
            self.appRedirect(url)
            return
        
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        
        # 対戦相手.
        oid = battleplayer.opponent
        o_player = None
        if oid and v_player.id != oid:
            arr = BackendApi.get_players(self, [oid], [PlayerExp], using=settings.DB_READONLY)
            if arr:
                o_player = arr[0]
        if o_player is None:
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'対戦相手が見つかりませんでした', CabaretError.Code.NOT_DATA)
            self.redirectToOppSelect()
            return
        
        if battleid == battleplayer.result:
            # お互いのカード.
            v_deck = BackendApi.get_deck(v_player.id, model_mgr, using=settings.DB_READONLY)
            o_deck = BackendApi.get_deck(o_player.id, model_mgr, using=settings.DB_READONLY)
            v_deck_cardlist = BackendApi.get_cards(v_deck.to_array(), model_mgr, using=settings.DB_READONLY)
            o_deck_cardlist = BackendApi.get_cards(o_deck.to_array(), model_mgr, using=settings.DB_READONLY)
            
            # 計算.
            rand = AppRandom()
            data = BackendApi.battle(v_player, v_deck_cardlist, o_player, o_deck_cardlist, rand)
            
            v_deck_cardidlist = v_deck.to_array()
            o_deck_cardidlist = o_deck.to_array()
            try:
                model_mgr, _ = db_util.run_in_transaction(self.tr_write, v_player.id, oid, v_deck_cardidlist, o_deck_cardidlist, data, battleid)
                model_mgr.write_end()
            except CabaretError, err:
                if err.code == CabaretError.Code.ALREADY_RECEIVED:
                    pass
                elif settings_sub.IS_LOCAL:
                    raise err
                else:
                    url = self.makeAppLinkUrlRedirect(UrlMaker.battlepre())
                    self.appRedirect(url)
                    return
        url = self.makeAppLinkUrlRedirect(UrlMaker.battleanim())
        self.appRedirect(url)
    
    def tr_write(self, uid, oid, v_deck_cardidlist, o_deck_cardidlist, data, battleid):
        model_mgr = ModelRequestMgr(loginfo=self.addloginfo)
        players = BackendApi.get_players(self, [uid, oid], [PlayerGold, PlayerExp, PlayerFriend], model_mgr=model_mgr)
        v_player = None
        o_player = None
        for player in players:
            if player.id == uid:
                v_player = player
            else:
                o_player = player
        battleresult = BackendApi.tr_battle(model_mgr, v_player, o_player, v_deck_cardidlist, o_deck_cardidlist, data, battleid)

        model_mgr.write_all()
        return model_mgr, battleresult

def main(request):
    return Handler.run(request)
