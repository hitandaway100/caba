# -*- coding: utf-8 -*-
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.api import BackendApi, Objects
from platinumegg.app.cabaret.views.application.battle.base import BattleHandler
from platinumegg.app.cabaret.util.cabareterror import CabaretError
import settings_sub
from defines import Defines
from platinumegg.app.cabaret.models.Player import PlayerAp, PlayerFriend,\
    PlayerExp


class Handler(BattleHandler):
    """バトル結果.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerAp, PlayerFriend, PlayerExp]
    
    def process(self):
        
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        
        self.setFromPage(Defines.FromPages.BATTLE)
        
        # 結果データ.
        battleresult = BackendApi.get_battleresult(model_mgr, v_player.id, using=settings.DB_READONLY)
        if battleresult is None:
            # 結果が存在しない.
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'結果がない')
            url = UrlMaker.battle()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        
        # 対戦相手.
        oid = battleresult.oid
        arr = BackendApi.get_players(self, [oid], [PlayerExp], using=settings.DB_READONLY)
        o_player = arr[0] if arr else None
        if o_player is None:
            # 相手が存在しない.
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'相手が存在しない')
            url = UrlMaker.battle()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        
        obj_v_player, obj_o_player = self.getObjPlayerList([v_player, o_player])
        
        obj_v_player['power_total'] = battleresult.data['v_power']
        obj_o_player['power_total'] = battleresult.data['o_power']
        
        obj_v_player['skilllist'] = battleresult.anim.make_html_skilllist(True)
        obj_o_player['skilllist'] = battleresult.anim.make_html_skilllist(False)
        
        self.html_param['player'] = obj_v_player
        self.html_param['o_player'] = obj_o_player
        
        if BackendApi.check_friend(v_player.id, oid, arg_model_mgr=model_mgr, using=settings.DB_READONLY):
            pass
        elif BackendApi.check_friendrequest_receive(v_player.id, oid, arg_model_mgr=model_mgr, using=settings.DB_READONLY):
            pass
        elif BackendApi.check_friendrequest_send(v_player.id, oid, arg_model_mgr=model_mgr, using=settings.DB_READONLY):
            pass
        else:
            self.html_param['is_friendrequest_ok'] = True
        
        data = battleresult.data
        self.html_param['resultdata'] = data
        
        # 獲得したアイテム.
        prizes = data.get('prizes')
        if prizes:
            prizelist = BackendApi.get_prizelist(model_mgr, prizes, using=settings.DB_READONLY)
            self.html_param['prize'] = BackendApi.make_prizeinfo(self, prizelist, using=settings.DB_READONLY)
        
        # レベルアップしたカード.
        obj_lebelupcardlist = []
        levelupcardlist = BackendApi.get_cards(battleresult.levelupcard.keys(), model_mgr, using=settings.DB_READONLY)
        for levelupcard in levelupcardlist:
            obj_card = Objects.card(self, levelupcard)
            obj_card['level_add'] = battleresult.levelupcard.get(levelupcard.id, 0)
            obj_lebelupcardlist.append(obj_card)
        self.html_param['levelupcardlist'] = obj_lebelupcardlist
        
        # 回復アイテム.
        BackendApi.put_bprecover_uselead_info(self)
        
        # 続けて戦う.
        url = UrlMaker.battleoppselect(0)
        self.html_param['url_battlecontinue'] = self.makeAppLinkUrl(url)
        
        # html書き込み.
        if data['is_win']:
            # 金の鍵の獲得率.
            battleplayer = self.getBattlePlayer()
            rankmaster = self.getBattleRankMaster()
            self.html_param['goldkey_rate'] = BackendApi.get_battle_goldkey_rate(model_mgr, battleplayer, rankmaster, using=settings.DB_READONLY)
            self.writeAppHtml('battle/battlewin')
        else:
            self.writeAppHtml('battle/battlelose')

def main(request):
    return Handler.run(request)
