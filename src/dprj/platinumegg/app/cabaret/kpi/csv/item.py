# -*- coding: utf-8 -*-
import settings
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.models.Item import ItemMaster
from platinumegg.app.cabaret.kpi.models.item import ItemDistributionAmount
from platinumegg.app.cabaret.kpi.csv.base import KpiCSVBase

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)

class Manager(KpiCSVBase):
    """カード分布.
    """
    def __init__(self, date, output_dir):
        KpiCSVBase.__init__(self, date, output_dir)
    
    def get_data(self):
        model_mgr = ModelRequestMgr()
        itemmasterlist = model_mgr.get_mastermodel_all(ItemMaster, order_by='id')
        
        result = []
        for itemmaster in itemmasterlist:
            _, vnum, rnum = ItemDistributionAmount.aggregateByMasterId(itemmaster.id)
            if vnum or rnum:
                result.append((itemmaster.id, itemmaster.name, vnum, rnum))
        if result:
            return result
        else:
            return None
