# -*- coding: utf-8 -*-
import settings
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.kpi.csv.raidevent import RaidEventCSVBase
from platinumegg.app.cabaret.kpi.models.raidevent import RaidEventStageDistributionAmount
from platinumegg.app.cabaret.util.api import BackendApi

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)


class Manager(RaidEventCSVBase):
    """レイドイベントステージ到達人数分布.
    """
    def __init__(self, date, output_dir):
        RaidEventCSVBase.__init__(self, date, output_dir)
    
    def get_data(self):
        model_mgr = ModelRequestMgr()
        eventid = self.getEventId(model_mgr)
        eventmaster = BackendApi.get_raideventmaster(model_mgr, eventid, backup_db)
        if not eventmaster.flag_dedicated_stage:
            return None
        
        data = RaidEventStageDistributionAmount.aggregate(eventid)
        if not data:
            return None
        
        result = []
        stagelist = data.keys()
        stagelist.sort(key=lambda x:int(x))
        for stage in stagelist:
            result.append([stage, data[stage]])
        return result
