# -*- coding: utf-8 -*-
import settings
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.kpi.models.battleevent import BattleEventMemberCount,\
    BattleEventJoin
from platinumegg.app.cabaret.kpi.csv.battleevent import BattleEventCSVBase

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)

class Manager(BattleEventCSVBase):
    """バトルイベント参加人数.
    """
    def __init__(self, date, output_dir):
        BattleEventCSVBase.__init__(self, date, output_dir)
    
    def get_data(self):
        model_mgr = ModelRequestMgr()
        eventid = self.getBattleEventId(model_mgr)
        rankmasterlist = BackendApi.get_battleevent_rankmaster_by_eventid(model_mgr, eventid, using=backup_db)
        
        str_date = self.date.strftime("%Y/%m/%d")
        datalist = []
        membercounts = BattleEventMemberCount.aggregate(self.date)
        joincounts = BattleEventJoin.aggregate(self.date)
        for rankmaster in rankmasterlist:
            rank = rankmaster.rank
            datalist.append((str_date, rank, membercounts.get(rank, 0), joincounts.get(rank, 0)))
        return datalist
    
    def delete(self):
        BattleEventJoin.deleteByDate(self.date)
        BattleEventMemberCount.deleteByDate(self.date)
