# -*- coding: utf-8 -*-
import settings
from platinumegg.app.cabaret.kpi.models.invite import InviteCount
from platinumegg.app.cabaret.kpi.csv.base import KpiCSVBase

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)

class Manager(KpiCSVBase):
    """招待数.
    """
    def __init__(self, date, output_dir):
        KpiCSVBase.__init__(self, date, output_dir)
    
    def get_data(self):
        date = self.date
        data = InviteCount.aggregate(date)
        if data:
            return list(data.items())
        else:
            return None
    
    def deleteInviteCount(self, date):
        date = self.date
        InviteCount.deleteByDate(date)
