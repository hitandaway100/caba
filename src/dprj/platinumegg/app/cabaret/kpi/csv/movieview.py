# -*- coding: utf-8 -*-
import settings
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.models.Card import CardAcquisition
from platinumegg.app.cabaret.models.Memories import MemoriesMaster
from platinumegg.app.cabaret.kpi.models.movie import MovieViewCount
from platinumegg.app.cabaret.kpi.csv.base import KpiCSVBase

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)

class Manager(KpiCSVBase):
    """動画再生数.
    """
    def __init__(self, date, output_dir):
        KpiCSVBase.__init__(self, date, output_dir)
    
    def get_data(self):
        """動画再生数.
        """
        data = MovieViewCount.aggregate(self.date)
        if not data:
            return None
        model_mgr = ModelRequestMgr()
        masters = BackendApi.get_model_dict(model_mgr, MemoriesMaster, data.keys(), using=backup_db)
        result = []
        for k, v in data.items():
            memoriesmaster = masters.get(k, None)
            if memoriesmaster:
                name = memoriesmaster.name
                text = memoriesmaster.text
                cnt = CardAcquisition.count(filters={'mid':memoriesmaster.id, 'maxlevel__gte':memoriesmaster.cardlevel}, using=backup_db)
            else:
                name = u'不明'
                text = u'不明'
                cnt = 0
            d = (k, name, text, v, cnt)
            result.append(d)
        return result
    
    def delete(self):
        """動画再生数を削除.
        """
        return MovieViewCount.deleteByDate(self.date)
