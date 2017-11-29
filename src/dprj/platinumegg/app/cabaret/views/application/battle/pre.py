# -*- coding: utf-8 -*-
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.api import BackendApi, Objects
from platinumegg.app.cabaret.views.application.battle.base import BattleHandler
from platinumegg.app.cabaret.models.Player import PlayerAp, PlayerFriend
from defines import Defines


class Handler(BattleHandler):
    """バトル確認.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerAp, PlayerFriend]
    
    def process(self):
        
        battleplayer = self.getBattlePlayer()
        if battleplayer is None or battleplayer.opponent == 0:
            # 対戦相手設定へ.
            self.redirectToOppSelect()
            return
        
        obj_list = self.getObjPlayerListByID([battleplayer.opponent])
        if not obj_list:
            # これも飛ばしておく.
            self.redirectToOppSelect()
            return
        
        self.setFromPage(Defines.FromPages.BATTLEPRE)
        
        v_player = self.getViewerPlayer()
        
        rankmaster = self.getBattleRankMaster()
        
        self.html_param['o_player'] = obj_list[0]
        
        self.html_param['player'] = Objects.player(self, v_player)
        self.html_param['battleplayer'] = Objects.battleplayer(self, battleplayer, rankmaster)
        
        # 最大ランク.
        model_mgr = self.getModelMgr()
        self.html_param['max_rank'] = BackendApi.get_battlerank_max(model_mgr, using=settings.DB_READONLY)
        
        # 残り対戦相手変更回数.
        self.html_param['opponent_change_restnum'] = BackendApi.get_battle_opponent_change_restcnt(model_mgr, battleplayer, rankmaster, using=settings.DB_READONLY)
        
        # アイテム.
        BackendApi.put_bprecover_uselead_info(self)
        
        # バトル開始URL.
        battleplayer = self.getBattlePlayer()
        url = UrlMaker.battledo(battleplayer.result)
        self.html_param['url_battle_do'] = self.makeAppLinkUrl(url)
        
        # 相手変更URL.
        url = UrlMaker.battleoppselect(battleplayer.change_cnt + 1)
        self.html_param['url_battle_oppselect'] = self.makeAppLinkUrl(url)
        
        # 金の鍵の獲得率.
        self.html_param['goldkey_rate'] = BackendApi.get_battle_goldkey_rate(model_mgr, battleplayer, rankmaster, using=settings.DB_READONLY)
        
        # 書き込み.
        if v_player.get_bp() < rankmaster.bpcost:
            self.writeAppHtml('battle/battleapnone')
        else:
            self.writeAppHtml('battle/battleselect')
    

def main(request):
    return Handler.run(request)
