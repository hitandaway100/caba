# -*- coding: utf-8 -*-
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.api import BackendApi, Objects
from platinumegg.app.cabaret.views.application.battle.base import BattleHandler
from platinumegg.app.cabaret.models.Player import PlayerFriend, PlayerAp,\
    PlayerKey
from platinumegg.lib.opensocial.util import OSAUtil

class Handler(BattleHandler):
    """バトルTOP.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerFriend, PlayerAp, PlayerKey]
    
    def process(self):
        
        self.setFromPage(None)
        
        v_player = self.getViewerPlayer()
        battleplayer = self.getBattlePlayer()
        if battleplayer is None or not battleplayer.lpvtime or OSAUtil.get_now() <= battleplayer.lpvtime:
            self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.battlelp()))
            return
        
        # 現在のランク.
        rankmaster = self.getBattleRankMaster()
        
        # プレイヤー.
        self.html_param['player'] = Objects.player(self, v_player)
        
        # バトル情報.
        self.html_param['battleplayer'] = Objects.battleplayer(self, battleplayer, rankmaster)
        
        # 対戦相手検索のUrl.
        self.html_param['url_battlepre'] = self.makeAppLinkUrl(UrlMaker.battlepre())
        
        # 気力回復のUrl.
        self.html_param['url_bprecover'] = self.makeAppLinkUrl(UrlMaker.bprecover())
        
        # 最大ランク.
        model_mgr = self.getModelMgr()
        self.html_param['max_rank'] = BackendApi.get_battlerank_max(model_mgr, using=settings.DB_READONLY)
        
        # 鍵情報.
        self.html_param['treasurekey'] = Objects.key(self, v_player)
        
        # イベント開催中判定.
        cur_eventmaster = BackendApi.get_current_battleevent_master(model_mgr, using=settings.DB_READONLY)
        self.html_param['battleevent'] = Objects.battleevent(self, cur_eventmaster) if cur_eventmaster else None
        self.html_param['url_battleevent_top'] = self.makeAppLinkUrl(UrlMaker.battleevent_top())
        
        # 書き込み.
        self.writeAppHtml('battle/battle')
    

def main(request):
    return Handler.run(request)
