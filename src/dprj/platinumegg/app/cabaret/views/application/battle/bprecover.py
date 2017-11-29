# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.api import BackendApi, Objects
from platinumegg.app.cabaret.views.application.battle.base import BattleHandler
from platinumegg.app.cabaret.models.Player import PlayerAp, PlayerFriend
from defines import Defines


class Handler(BattleHandler):
    """気力回復.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerAp, PlayerFriend]
    
    def process(self):
        
        v_player = self.getViewerPlayer()
        self.getBattlePlayer(get_instance=True)
        rankmaster = self.getBattleRankMaster()
        
        self.setFromPage(Defines.FromPages.BATTLE)
        
        self.html_param['player'] = Objects.player(self, v_player)
        self.html_param['rankmaster'] = Objects.battlerank(self, rankmaster)
        
        # アイテム.
        BackendApi.put_bprecover_uselead_info(self)
        
        # 書き込み.
        self.writeAppHtml('battle/battleaprecover')
    

def main(request):
    return Handler.run(request)
