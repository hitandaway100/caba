# -*- coding: utf-8 -*-
import settings
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.kpi.models.scoutevent import ScoutEventPointSet
from platinumegg.app.cabaret.kpi.csv.scoutevent import ScoutEventCSVBase

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)


class Manager(ScoutEventCSVBase):
    """スカウトイベントポイント一覧.
    """
    def __init__(self, date, output_dir):
        ScoutEventCSVBase.__init__(self, date, output_dir)
    
    def get_data(self):
        model_mgr = ModelRequestMgr()
        eventid = self.getScoutEventId(model_mgr)
        
        data = ScoutEventPointSet.aggregate(eventid)
        if data:
            return list(data.items())
        else:
            return None
    
    def delete(self):
        model_mgr = ModelRequestMgr()
        if self.isScoutEventEnd(model_mgr):
            eventid = self.getScoutEventId(model_mgr)
            ScoutEventPointSet.getDB().delete(ScoutEventPointSet.makeKey(eventid))
