# -*- coding: utf-8 -*-
import settings
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.kpi.models.raidevent import RaidEventDailyConsumeTicket
from platinumegg.app.cabaret.kpi.csv.raidevent import RaidEventCSVBase

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)

class Manager(RaidEventCSVBase):
    """日別イベントガチャ実行数.
    """
    def __init__(self, date, output_dir):
        RaidEventCSVBase.__init__(self, date, output_dir)
    
    def get_data(self):
        model_mgr = ModelRequestMgr()
        data = RaidEventDailyConsumeTicket.aggregate(self.date, self.getEventId(model_mgr))
        if data:
            return data.items()
        else:
            return None
    
    def delete(self):
        model_mgr = ModelRequestMgr()
        RaidEventDailyConsumeTicket.deleteByDate(self.date, self.getEventId(model_mgr))
