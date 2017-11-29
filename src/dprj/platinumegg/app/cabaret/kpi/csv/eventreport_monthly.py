# -*- coding: utf-8 -*-
import datetime
import settings
from platinumegg.app.cabaret.kpi.csv.eventreport import EventReportCSVBase
from platinumegg.app.cabaret.util.datetime_util import DateTimeUtil

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)

class Manager(EventReportCSVBase):
    """月別イベントレポートデータ.
    """
    def __init__(self, date, output_dir):
        EventReportCSVBase.__init__(self, date, output_dir)
    
    def get_data(self):
        # 前月の最終日.
        e_date = DateTimeUtil.strToDateTime(self.date.strftime("%Y%m01"), "%Y%m%d") - datetime.timedelta(days=1)
        # 前月の1日.
        s_date = DateTimeUtil.strToDateTime(e_date.strftime("%Y%m01"), "%Y%m%d")
        
        return self.get_data_by_range(s_date, e_date)
