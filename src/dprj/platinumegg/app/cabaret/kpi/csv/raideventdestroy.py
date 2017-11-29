# -*- coding: utf-8 -*-
import settings
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.kpi.models.raidevent import RaidEventDestroyUserNum
from platinumegg.app.cabaret.kpi.csv.raidevent import RaidEventCSVBase

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)

class Manager(RaidEventCSVBase):
    """通常太客討伐回数別ユーザー数.
    """
    def __init__(self, date, output_dir):
        RaidEventCSVBase.__init__(self, date, output_dir)
    
    def get_data(self):
        model_mgr = ModelRequestMgr()
        eventid = self.getEventId(model_mgr)
        data = RaidEventDestroyUserNum.aggregate(eventid)
        if data:
            return data.items()
        else:
            return None