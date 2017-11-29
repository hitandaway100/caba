# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from platinumegg.app.cabaret.views.application.happening.base import HappeningHandler
from defines import Defines
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.models.Player import PlayerRequest

class Handler(HappeningHandler):
    """レイド情報取得.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerRequest]
    
    def process(self):
        
        try:
            raidid = int(self.request.get(Defines.URLQUERY_ID))
        except:
            raidid = None
        
        model_mgr = self.getModelMgr()
        
        v_player = self.getViewerPlayer()
        
        # レイド情報.
        happeningraidset = None
        if raidid:
            happeningraidset = BackendApi.get_happeningraidset(model_mgr, raidid, using=settings.DB_READONLY)
        if happeningraidset is None or happeningraidset.raidboss is None:
            raise CabaretError(u'存在しないレイドです', CabaretError.Code.NOT_DATA)
        
        # ハプニング情報.
        obj_happening = Objects.happening(self, happeningraidset)
        self.json_result_param['happening'] = obj_happening
        
        # ダメージ履歴.
        func_put_attacklog = self.putRaidAttackLog(happeningraidset.raidboss)
        # お助け.
        func_put_playerlist = self.putHelpFriend(happeningraidset.raidboss)
        
        if func_put_attacklog or func_put_playerlist:
            self.execute_api()
            if func_put_attacklog:
                func_put_attacklog()
            if func_put_playerlist:
                func_put_playerlist()
        
        # 確認キー.
        self.json_result_param['battlekey'] = v_player.req_confirmkey
        
        self.writeAppJson()
    
def main(request):
    return Handler.run(request)
