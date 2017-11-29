# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from platinumegg.app.cabaret.views.application.battle.base import BattleHandler
from platinumegg.app.cabaret.util.cabareterror import CabaretError

class Handler(BattleHandler):
    """バトル対戦相手情報.
    """
    
    def process(self):
        
        model_mgr = self.getModelMgr()
        
        battleplayer = self.getBattlePlayer()
        if battleplayer is None or battleplayer.opponent == 0:
            # 対戦相手設定へ.
            raise CabaretError(u'対戦相手を設定してください', CabaretError.Code.NOT_DATA)
        
        rankmaster = self.getBattleRankMaster()
        obj_list = self.getObjPlayerListByID([battleplayer.opponent])
        if not obj_list:
            # 対戦相手が削除された.
            raise CabaretError(u'対戦相手が見つかりませんでした.再設定してください.', CabaretError.Code.NOT_DATA)
        
        # 対戦相手.
        self.json_result_param['player'] = obj_list[0]
        
        # 残り対戦相手変更回数.
        opponent_change_restnum = BackendApi.get_battle_opponent_change_restcnt(model_mgr, battleplayer, rankmaster, using=settings.DB_READONLY)
        self.json_result_param['opponent_change_restnum'] = opponent_change_restnum
        
        # 実行用のキー.
        self.json_result_param['battlekey'] = battleplayer.result
        
        self.writeAppJson()
    
def main(request):
    return Handler.run(request)
