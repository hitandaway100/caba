# -*- coding: utf-8 -*-
import settings
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.models.Battle import BattleRankMaster
from platinumegg.app.cabaret.kpi.models.battle import BattleRankupCount
from platinumegg.app.cabaret.kpi.csv.base import KpiCSVBase

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)

class Manager(KpiCSVBase):
    """バトルランクアップ分布.
    """
    def __init__(self, date, output_dir):
        KpiCSVBase.__init__(self, date, output_dir)
    
    def get_data(self):
        data = BattleRankupCount.aggregate(self.date)
        if not data:
            return None
        model_mgr = ModelRequestMgr()
        masterlist = model_mgr.get_mastermodel_all(BattleRankMaster, 'id', using=backup_db)
        result = [(u'%d:%s%s' % (master.id, master.region, master.town), data.get(master.id, 0)) for master in masterlist]
        return result
    
    def delete(self):
        BattleRankupCount.deleteByDate(self.date)
