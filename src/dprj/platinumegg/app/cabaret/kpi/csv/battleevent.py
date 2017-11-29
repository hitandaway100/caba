# -*- coding: utf-8 -*-
import settings
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.kpi.csv.base import KpiCSVBase

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)


class BattleEventCSVBase(KpiCSVBase):
    def __init__(self, date, output_dir):
        KpiCSVBase.__init__(self, date, output_dir)
    
    def getBattleEventId(self, model_mgr):
        config = BackendApi.get_current_battleeventconfig(model_mgr, using=backup_db)
        return config.mid
