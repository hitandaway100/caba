# -*- coding: utf-8 -*-
import settings
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.kpi.models.scoutevent import ScoutEventGachaPointConsumeHash
from platinumegg.app.cabaret.kpi.csv.scoutevent import ScoutEventCSVBase

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)


class Manager(ScoutEventCSVBase):
    """スカウトイベントガチャポイント消費量.
    """
    def __init__(self, date, output_dir):
        ScoutEventCSVBase.__init__(self, date, output_dir)
    
    def get_data(self):
        model_mgr = ModelRequestMgr()
        eventid = self.getScoutEventId(model_mgr)
        
        data = ScoutEventGachaPointConsumeHash.aggregate(eventid)
        if data:
            return list(data.items())
        else:
            return None
    
    def delete(self):
        model_mgr = ModelRequestMgr()
        if self.isScoutEventPresentEnd(model_mgr):
            eventid = self.getScoutEventId(model_mgr)
            ScoutEventGachaPointConsumeHash.getDB().delete(ScoutEventGachaPointConsumeHash.makeKey(eventid))
