# -*- coding: utf-8 -*-
import datetime
import settings
from defines import Defines
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.datetime_util import DateTimeUtil
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.models.Gacha import GachaMaster, GachaPlayCount,\
    GachaConsumePoint
from platinumegg.app.cabaret.models.Schedule import ScheduleMaster
from platinumegg.app.cabaret.kpi.models.gacha import GachaLastStepSortSet
from platinumegg.app.cabaret.kpi.models.login import WeeklyLoginSet
from platinumegg.app.cabaret.kpi.csv.base import KpiCSVBase

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)

class Manager(KpiCSVBase):
    """ユーザごとのガチャデータ.
    """
    def __init__(self, date, output_dir):
        KpiCSVBase.__init__(self, date, output_dir)
        self.__midlist = None
    
    def get_data(self):
        """ユーザごとのガチャデータ.
        """
        # 7日前.
        s_time = DateTimeUtil.toBaseTime(self.date - datetime.timedelta(days=7), 0)
        e_time = self.date
        
        # 過去1週間以内にログインしたユーザー.
        str_uidlist = WeeklyLoginSet.getUserIdListByRange(s_time, e_time)
        
        # 対象のガチャ.
        filters = {
            'consumetype__in' : Defines.GachaConsumeType.PAYMENT_TYPES,
        }
        gachamasterlist = GachaMaster.fetchValues(filters=filters, order_by='id', using=backup_db)
        
        model_mgr = ModelRequestMgr()
        
        def checkSchedule(gachamaster):
            if gachamaster.schedule:
                # 期間チェック.
                master = model_mgr.get_model(ScheduleMaster, gachamaster.schedule, using=backup_db)
                if master and ((master.stime <= master.etime <= s_time) or (e_time < master.stime <= master.etime)):
                    # 期間外.
                    return False
            return True
        
        midlist = [gachamaster.id for gachamaster in gachamasterlist if checkSchedule(gachamaster)]
        self.__midlist = midlist
        
        redisdb = GachaLastStepSortSet.getDB()
        result = []
        if midlist:
            for str_uid in str_uidlist:
                if not str_uid or not str(str_uid).isdigit():
                    continue
                uid = int(str_uid)
                
                tmp_model_mgr = ModelRequestMgr()
                idlist = [GachaPlayCount.makeID(uid, mid) for mid in midlist]
                # 回転数.
                countdict = BackendApi.get_model_dict(tmp_model_mgr, GachaPlayCount, idlist, using=backup_db, key=lambda x:x.mid)
                
                # 課金額.
                paydict = BackendApi.get_model_dict(tmp_model_mgr, GachaConsumePoint, idlist, using=backup_db, key=lambda x:x.mid)
                
                for mid in midlist:
                    if not countdict.get(mid):
                        continue
                    cnt = countdict[mid].cnttotal
                    pay = paydict[mid].point if paydict.get(mid) else 0
                    step = redisdb.zscore(GachaLastStepSortSet.makeKey(self.date, mid), uid) or 0
                    result.append((uid, mid, cnt, pay, step))
        return result
    
    def delete(self):
        """ステップ数を削除.
        """
        if self.__midlist:
            redisdb = GachaLastStepSortSet.getDB()
            keys = [GachaLastStepSortSet.makeKey(self.date, mid) for mid in self.__midlist]
            redisdb.delete(*keys)
