# -*- coding: utf-8 -*-
import settings
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.kpi.csv.base import KpiCSVBase
import datetime

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)

class ScoutEventCSVBase(KpiCSVBase):
    def __init__(self, date, output_dir):
        KpiCSVBase.__init__(self, date, output_dir)
    
    def getScoutEventId(self, model_mgr):
        config = BackendApi.get_current_scouteventconfig(model_mgr, using=backup_db)
        return config.mid
    
    def isScoutEventEnd(self, model_mgr):
        config = BackendApi.get_current_scouteventconfig(model_mgr, using=backup_db)
        bordertime = self.date + datetime.timedelta(days=1)
        return config.endtime < bordertime
    
    def isScoutEventPresentEnd(self, model_mgr):
        config = BackendApi.get_current_scouteventconfig(model_mgr, using=backup_db)
        bordertime = self.date + datetime.timedelta(days=1)
        return config.present_endtime < bordertime
