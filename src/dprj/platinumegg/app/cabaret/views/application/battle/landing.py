# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.application.battle.base import BattleHandler
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.api import BackendApi

class Handler(BattleHandler):
    """バトルランディングページ.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        
        now = OSAUtil.get_now()
        battleplayer = self.getBattlePlayer()
        if battleplayer is None or battleplayer.lpvtime is None or now < battleplayer.lpvtime:
            # 閲覧時間を更新.
            v_player = self.getViewerPlayer()
            BackendApi.update_battle_lp_vtime(v_player.id, now)
        
        self.writeAppHtml('tutorial/lp')
    

def main(request):
    return Handler.run(request)
