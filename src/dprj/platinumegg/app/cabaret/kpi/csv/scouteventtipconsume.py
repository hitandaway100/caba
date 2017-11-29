# -*- coding: utf-8 -*-
import settings
from platinumegg.app.cabaret.kpi.models.scoutevent import ScoutEventTipConsumeHash
from platinumegg.app.cabaret.kpi.csv.scoutevent import ScoutEventCSVBase
from platinumegg.app.cabaret.models.Player import Player
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)

class Manager(ScoutEventCSVBase):
    """スカウトイベントチップ消費数.
    """
    def __init__(self, date, output_dir):
        ScoutEventCSVBase.__init__(self, date, output_dir)
        self.__data = None
    
    def get_data(self):
        uid_max = Player.max_value('id', using=backup_db)
        data = ScoutEventTipConsumeHash.aggregate(uid_max)
        self.__data = data
        return data or None
    
    def delete(self):
        if self.__data is None or not self.isScoutEventPresentEnd(ModelRequestMgr()):
            return
        
        redisdb = ScoutEventTipConsumeHash.getDB()
        keylist = []
        for arr in self.__data:
            uid = arr[0]
            keylist.append(ScoutEventTipConsumeHash.makeKey(uid))
            if 100 <= len(keylist):
                redisdb.delete(*keylist)
                keylist = []
        if keylist:
            redisdb.delete(*keylist)
