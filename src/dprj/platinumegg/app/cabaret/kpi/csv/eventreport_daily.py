# -*- coding: utf-8 -*-
import settings
from platinumegg.app.cabaret.kpi.csv.eventreport import EventReportCSVBase
from platinumegg.app.cabaret.util.datetime_util import DateTimeUtil

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)

class Manager(EventReportCSVBase):
    """日別イベントレポートデータ.
    """
    def __init__(self, date, output_dir):
        EventReportCSVBase.__init__(self, date, output_dir)
    
    def get_data(self):
        date = DateTimeUtil.toBaseTime(self.date, 0)
        return self.get_data_by_range(date, date)
