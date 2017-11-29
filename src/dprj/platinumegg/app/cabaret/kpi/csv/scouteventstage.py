# -*- coding: utf-8 -*-
import settings
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.kpi.models.scoutevent import ScoutEventStageDistributionAmount
from platinumegg.app.cabaret.kpi.csv.scoutevent import ScoutEventCSVBase

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)


class Manager(ScoutEventCSVBase):
    """スカウトイベントステージ到達人数分布.
    """
    def __init__(self, date, output_dir):
        ScoutEventCSVBase.__init__(self, date, output_dir)
    
    def get_data(self):
        model_mgr = ModelRequestMgr()
        eventid = self.getScoutEventId(model_mgr)
        
        data = ScoutEventStageDistributionAmount.aggregate(eventid)
        if not data:
            return None
        
        result = []
        stagelist = data.keys()
        stagelist.sort(key=lambda x:int(x))
        for stage in stagelist:
            result.append([stage, data[stage]])
        return result
