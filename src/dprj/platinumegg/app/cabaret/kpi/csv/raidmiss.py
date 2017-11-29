# -*- coding: utf-8 -*-
import settings
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.models.Happening import RaidMaster
from platinumegg.app.cabaret.kpi.models.raid import DailyRaidAppearCount,\
    DailyRaidDestroyCount
from platinumegg.app.cabaret.kpi.csv.base import KpiCSVBase

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)

class Manager(KpiCSVBase):
    """レイド失敗数.
    """
    def __init__(self, date, output_dir):
        KpiCSVBase.__init__(self, date, output_dir)
    
    def get_data(self):
        model_mgr = ModelRequestMgr()
        raidmaster_all = model_mgr.get_mastermodel_all(RaidMaster, 'id', using=backup_db)
        maxlevel = BackendApi.get_playermaxlevel(model_mgr, using=backup_db)
        
        result = []
        
        all_zero = True
        for raidmaster in raidmaster_all:
            row = [u'%d:%s' % (raidmaster.id, raidmaster.name)]
            data_appear = DailyRaidAppearCount.aggregate(self.date, raidmaster.id)
            data_destroy = DailyRaidDestroyCount.aggregate(self.date, raidmaster.id)
            if data_appear or data_destroy:
                all_zero = False
            
            data_appear = data_appear or {}
            data_destroy = data_destroy or {}
            
            for level in xrange(1, maxlevel+1):
                row.append(data_appear.get(level, 0) - data_destroy.get(level, 0))
            result.append(row)
        if all_zero:
            return None
        else:
            return result
