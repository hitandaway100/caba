# -*- coding: utf-8 -*-
import settings
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.models.Scout import ScoutMaster
from platinumegg.app.cabaret.kpi.models.scout import ScoutCompleteCount
from platinumegg.app.cabaret.kpi.csv.base import KpiCSVBase

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)

class Manager(KpiCSVBase):
    """スカウト達成分布.
    """
    def __init__(self, date, output_dir):
        KpiCSVBase.__init__(self, date, output_dir)
    
    def get_data(self):
        data = ScoutCompleteCount.aggregate(self.date)
        if not data:
            return None
        model_mgr = ModelRequestMgr()
        masterlist = model_mgr.get_mastermodel_all(ScoutMaster, 'id', using=backup_db)
        result = [(u'%d:%s' % (master.id, master.name), data.get(master.id, 0)) for master in masterlist]
        return result
    
    def delete(self):
        return ScoutCompleteCount.deleteByDate(self.date)
