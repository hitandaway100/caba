# -*- coding: utf-8 -*-
import settings
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.models.PlayerLevelExp import PlayerLevelExpMaster
from platinumegg.app.cabaret.kpi.models.player import PlayerLevelDistributionAmount
from platinumegg.app.cabaret.kpi.csv.base import KpiCSVBase

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)

class Manager(KpiCSVBase):
    """プレイヤーレベル分布.
    """
    def __init__(self, date, output_dir):
        KpiCSVBase.__init__(self, date, output_dir)
    
    def get_data(self):
        data = PlayerLevelDistributionAmount.aggregate()
        if not data:
            return None
        model_mgr = ModelRequestMgr()
        levelexplist = model_mgr.get_mastermodel_all(PlayerLevelExpMaster, 'level', using=backup_db)
        result = [(levelexp.level, data.get(levelexp.level, 0)) for levelexp in levelexplist]
        return result
