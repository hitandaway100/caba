# -*- coding: utf-8 -*-

import datetime

from platinumegg.app.cabaret.kpi.csv.base import KpiCSVBase
from platinumegg.app.cabaret.util.api import BackendApi
import settings

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)


class ProduceEventCSVBase(KpiCSVBase):
    def __init__(self, date, output_dir):
        KpiCSVBase.__init__(self, date, output_dir)

    def getProduceEventId(self, model_mgr):
        config = BackendApi.get_current_produce_event_config(model_mgr, using=backup_db)
        return config.mid
