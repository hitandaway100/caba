# -*- coding: utf-8 -*-
import settings
from platinumegg.app.cabaret.models.Player import Player
from platinumegg.app.cabaret.kpi.models.battleevent import BattleEventPieceCollect
from platinumegg.app.cabaret.kpi.csv.battleevent import BattleEventCSVBase

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)

class Manager(BattleEventCSVBase):
    """バトルイベントピース取得数.
    """
    def __init__(self, date, output_dir):
        BattleEventCSVBase.__init__(self, date, output_dir)

    def get_data(self):
        data = BattleEventPieceCollect.aggregate(self.date)
        if not data:
            return None
        result = [['R', 0], ['HR', 0], ['SR', 0], ['SSR', 0]]
        for str_rarity, str_count in data.iteritems():
            result[int(str_rarity)][1] += int(str_count)
        return result
