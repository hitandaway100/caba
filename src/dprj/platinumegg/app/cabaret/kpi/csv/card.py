# -*- coding: utf-8 -*-
import settings
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.models.Card import CardMaster
from platinumegg.app.cabaret.kpi.models.card import CardDistributionAmount
from platinumegg.app.cabaret.kpi.csv.base import KpiCSVBase

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)

class Manager(KpiCSVBase):
    """カード分布.
    """
    def __init__(self, date, output_dir):
        KpiCSVBase.__init__(self, date, output_dir)
    
    def get_data(self):
        data = CardDistributionAmount.aggregate()
        if not data:
            return None
        model_mgr = ModelRequestMgr()
        cardmasterlist = model_mgr.get_mastermodel_all(CardMaster, 'id', using=backup_db)
        result = [(u'%d:%s' % (cardmaster.id, cardmaster.name), data.get(cardmaster.id, 0)) for cardmaster in cardmasterlist]
        return result
