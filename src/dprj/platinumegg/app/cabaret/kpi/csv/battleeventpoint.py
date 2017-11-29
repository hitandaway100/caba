# -*- coding: utf-8 -*-
import settings
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.kpi.csv.battleevent import BattleEventCSVBase
from platinumegg.app.cabaret.util.redisdb import BattleEventRanking

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)

class Manager(BattleEventCSVBase):
    """獲得秘宝数.
    """
    def __init__(self, date, output_dir):
        BattleEventCSVBase.__init__(self, date, output_dir)
    
    def get_data(self):
        model_mgr = ModelRequestMgr()
        eventid = self.getBattleEventId(model_mgr)
        
        num_max = BattleEventRanking.getRankerNum(eventid)
        LIMIT = 500
        
        datalist = []
        offset = 0
        while offset < num_max:
            datalist.extend(BattleEventRanking.fetch(eventid, offset, LIMIT))
            offset += LIMIT
        return datalist
