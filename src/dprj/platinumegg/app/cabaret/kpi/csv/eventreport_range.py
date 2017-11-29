# -*- coding: utf-8 -*-
import datetime
import settings
from platinumegg.app.cabaret.kpi.csv.eventreport import EventReportCSVBase
from platinumegg.app.cabaret.models.raidevent.RaidEvent import CurrentRaidEventConfig
from platinumegg.app.cabaret.models.ScoutEvent import CurrentScoutEventConfig
from platinumegg.app.cabaret.models.battleevent.BattleEvent import CurrentBattleEventConfig
from platinumegg.app.cabaret.util.datetime_util import DateTimeUtil

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)

class Manager(EventReportCSVBase):
    """期間別イベントレポートデータ.
    """
    def __init__(self, date, output_dir):
        EventReportCSVBase.__init__(self, date, output_dir)
    
    def get_data(self):
        
        config_cls_list = (
            CurrentRaidEventConfig,
            CurrentScoutEventConfig,
            CurrentBattleEventConfig
        )
        # 各configの期間を見る.
        for config_cls in config_cls_list:
            config = config_cls.getByKey(config_cls.SINGLE_ID, using=backup_db)
            if config is None or config.mid < 1:
                continue
            
            s_time = DateTimeUtil.toBaseTime(config.starttime, 0)
            e_time = DateTimeUtil.toBaseTime(config.endtime + datetime.timedelta(days=1), 0)
            if s_time <= self.date < e_time:
                return self.get_data_by_range(s_time, e_time)
        
        return None
