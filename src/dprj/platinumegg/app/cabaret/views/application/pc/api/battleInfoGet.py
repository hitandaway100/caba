# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from platinumegg.app.cabaret.views.application.battle.base import BattleHandler

class Handler(BattleHandler):
    """バトル情報.
    """
    
    def process(self):
        
        model_mgr = self.getModelMgr()
        
        battleplayer = self.getBattlePlayer(get_instance=True)
        rankmaster = self.getBattleRankMaster()
        
        # バトル情報.
        self.json_result_param['battleplayer'] = Objects.battleplayer(self, battleplayer, rankmaster)
        
        # 最大ランク.
        self.json_result_param['max_rank'] = BackendApi.get_battlerank_max(model_mgr, using=settings.DB_READONLY)
        
        self.writeAppJson()
    
def main(request):
    return Handler.run(request)
