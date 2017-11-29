# -*- coding: utf-8 -*-
import settings
from platinumegg.app.cabaret.models.Player import Player
from platinumegg.app.cabaret.kpi.models.battleevent import BattleEventDailyUserRankSet,\
    BattleEventBattleCountAttack, BattleEventBattleCountAttackWin,\
    BattleEventBattleCountDefense, BattleEventBattleCountDefenseWin
from platinumegg.app.cabaret.kpi.csv.battleevent import BattleEventCSVBase

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)

class Manager(BattleEventCSVBase):
    """バトルイベントバトル回数.
    """
    def __init__(self, date, output_dir):
        BattleEventCSVBase.__init__(self, date, output_dir)
    
    def get_data(self):
        idmax = Player.max_value('id', using=backup_db)
        if not idmax:
            return []
        
        LIMIT = 500
        datalist = []
        uid = 1
        date = self.date
        
        while uid <= idmax:
            range_max = min(idmax + 1, uid+LIMIT)
            uidlist = range(uid, range_max)
            
            rank_map = BattleEventDailyUserRankSet.fetch(date, uidlist)
            attack_map = BattleEventBattleCountAttack.fetch(date, uidlist)
            attackwin_map = BattleEventBattleCountAttackWin.fetch(date, uidlist)
            defense_map = BattleEventBattleCountDefense.fetch(date, uidlist)
            defensewin_map = BattleEventBattleCountDefenseWin.fetch(date, uidlist)
            
            for uid in uidlist:
                datalist.append((uid, rank_map.get(uid, 0), attack_map.get(uid, 0), attackwin_map.get(uid, 0), defense_map.get(uid, 0), defensewin_map.get(uid, 0)))
            uid += LIMIT
        
        return datalist
    
    def delete(self):
        date = self.date
        
        redisdb = BattleEventBattleCountAttack.getDB()
        pipe = redisdb.pipeline()
        
        BattleEventDailyUserRankSet.deleteByDate(date, pipe)
        BattleEventBattleCountAttack.deleteByDate(date, pipe)
        BattleEventBattleCountAttackWin.deleteByDate(date, pipe)
        BattleEventBattleCountDefense.deleteByDate(date, pipe)
        BattleEventBattleCountDefenseWin.deleteByDate(date, pipe)
        
        pipe.execute()
