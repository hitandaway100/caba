# -*- coding: utf-8 -*-
import settings
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.models.Happening import RaidMaster
from platinumegg.app.cabaret.kpi.models.raidevent import RaidEventDestroyLevelMap
from platinumegg.app.cabaret.kpi.csv.raidevent import RaidEventCSVBase

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)

class Manager(RaidEventCSVBase):
    """超太客Lv別討伐回数.
    """
    def __init__(self, date, output_dir):
        RaidEventCSVBase.__init__(self, date, output_dir)
    
    def get_data(self):
        model_mgr = ModelRequestMgr()
        eventid = self.getEventId(model_mgr)
        
        result = []
        
        raidmaster_all = model_mgr.get_mastermodel_all(RaidMaster, 'id', fetch_deleted=True, using=backup_db)
        for raidmaster in raidmaster_all:
            row = ["%s(ID:%s)" % (raidmaster.name, raidmaster.id)]
            data = RaidEventDestroyLevelMap.hgetall(eventid, raidmaster.id)
            if not data:
                continue
            for level in xrange(1, 101):
                num = data.get(str(level), 0)
                row.append(num)
            result.append(row)
        if result:
            return result
        else:
            return None
