# -*- coding: utf-8 -*-
import settings
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.kpi.models.battleevent import BattleEventFame
from platinumegg.app.cabaret.kpi.csv.battleevent import BattleEventCSVBase

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)

class Manager(BattleEventCSVBase):
    """バトルイベント名声ポイント.
    """
    def __init__(self, date, output_dir):
        BattleEventCSVBase.__init__(self, date, output_dir)
    
    def get_data(self):
        model_mgr = ModelRequestMgr()
        eventid = self.getBattleEventId(model_mgr)
        
        data = BattleEventFame.aggregate(eventid)
        if data:
            return list(data.items())
        else:
            return None
