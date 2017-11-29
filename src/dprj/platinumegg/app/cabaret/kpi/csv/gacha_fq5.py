# -*- coding: utf-8 -*-
import settings
from defines import Defines
from platinumegg.app.cabaret.util.datetime_util import DateTimeUtil
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.models.Gacha import GachaMaster
from platinumegg.app.cabaret.models.Schedule import ScheduleMaster
from platinumegg.app.cabaret.kpi.models.payment import FQ5PaymentSet
from platinumegg.app.cabaret.kpi.csv.base import KpiCSVBase

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)

class Manager(KpiCSVBase):
    """FQ5課金ユーザ.
    """
    def __init__(self, date, output_dir):
        KpiCSVBase.__init__(self, date, output_dir)
    
    def get_data(self):
        """FQ5課金ユーザ.
        """
        # 1日のDate.
        s_time = DateTimeUtil.strToDateTime(self.date.strftime("%Y%m01"), "%Y%m%d")
        
        # 集計終了時間.
        e_time = DateTimeUtil.toBaseTime(self.date, 23, 59, 59)
        
        # 対象のガチャ.
        filters = {
            'consumetype__in' : Defines.GachaConsumeType.PAYMENT_TYPES,
        }
        gachamasterlist = GachaMaster.fetchValues(filters=filters, order_by='id', using=backup_db)
        
        model_mgr = ModelRequestMgr()
        
        result = []
        for gachamaster in gachamasterlist:
            if gachamaster.schedule:
                # 期間チェック.
                master = model_mgr.get_model(ScheduleMaster, gachamaster.schedule, using=backup_db)
                if master and ((master.stime <= master.etime <= s_time) or (e_time < master.stime <= master.etime)):
                    # 期間外.
                    continue
            # FQ5UU.
            cnt = FQ5PaymentSet.countByRange(s_time, e_time, gachamaster.id)
            result.append((gachamaster.id, cnt))
        return result
