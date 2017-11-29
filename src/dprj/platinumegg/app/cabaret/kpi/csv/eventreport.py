# -*- coding: utf-8 -*-
import datetime
import settings
from platinumegg.app.cabaret.kpi.csv.base import KpiCSVBase
from platinumegg.app.cabaret.kpi.models.event import EventJoinDaily,\
    EventPlayDaily, EventShopPaymentPointDaily, EventShopPaymentUUDaily,\
    EventGachaPaymentPointDaily, EventGachaPaymentUUDaily

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)

class EventReportCSVBase(KpiCSVBase):
    """イベントレポートデータ.
        参加UU(SP)
        参加UU(PC)
        参加UU(両方)
        アクセスUU(SP)
        アクセスUU(PC)
        アクセスUU(両方)
        アイテム課金額(SP)
        アイテム課金額(PC)
        アイテム課金UU(SP)
        アイテム課金UU(PC)
        アイテム課金UU(両方)
        ガチャ課金額(SP)
        ガチャ課金額(PC)
        ガチャ課金UU(SP)
        ガチャ課金UU(PC)
        ガチャ課金UU(両方)
        両方課金しているUU(SP)
        両方課金しているUU(PC)
        両方課金しているUU(両方)
    """
    def __init__(self, date, output_dir):
        KpiCSVBase.__init__(self, date, output_dir)
    
    def get_data_by_range(self, s_date, e_date):
        """イベントレポートデータ.
        """
        SP = 0
        PC = 1
        
        redisdb = EventJoinDaily.getDB()
        
        days = []
        timediff = datetime.timedelta(days=0)
        tmp_date = s_date + timediff
        while tmp_date <= e_date:
            days.append(timediff.days)
            timediff = datetime.timedelta(days=timediff.days+1)
            tmp_date = s_date + timediff
        
        if not days:
            return None
        
        def forEachDays(func, *args, **kwargs):
            resultlist = [func(s_date+datetime.timedelta(days=day), *args, **kwargs) for day in days]
            return resultlist
        
        row = []
        
        def aggregateUU(uu_cls, union_format="TMP_UNION##%s", do_delete_union=True):
            # キー.
            sp_keys = forEachDays(uu_cls.makeKey, False)
            pc_keys = forEachDays(uu_cls.makeKey, True)
            
            # UNIONを作成.
            dest_key_sp = union_format % SP
            dest_key_pc = union_format % PC
            redisdb.sunionstore(dest_key_sp, *sp_keys)
            redisdb.sunionstore(dest_key_pc, *pc_keys)
            
            # SPのUU(この時点ではPCも含んでいる状態).
            sp_uu = redisdb.scard(dest_key_sp)
            # PCのUU(この時点ではSPも含んでいる状態).
            pc_uu = redisdb.scard(dest_key_pc)
            # 両方のUU.
            both_uu = 0
            if sp_uu and pc_uu:
                both_uu = len(redisdb.sinter(dest_key_sp, dest_key_pc))
                # 純粋なSPUUとPCUUにする.
                sp_uu -= both_uu
                pc_uu -= both_uu
            # 後片付け.
            if do_delete_union:
                redisdb.delete(dest_key_sp, dest_key_pc)
            
            return sp_uu, pc_uu, both_uu
        
        #参加UU.
        row.extend(aggregateUU(EventPlayDaily))
        #アクセスUU.
        row.extend(aggregateUU(EventJoinDaily))
        
        #アイテム課金額(SP).
        row.append(sum(forEachDays(lambda x:int(redisdb.hget(EventShopPaymentPointDaily.makeKey(x, False), x.day) or 0))))
        #アイテム課金額(PC).
        row.append(sum(forEachDays(lambda x:int(redisdb.hget(EventShopPaymentPointDaily.makeKey(x, True), x.day) or 0))))
        
        #アイテム課金UU.
        shop_union_format = "ShopUU##%s"
        row.extend(aggregateUU(EventShopPaymentUUDaily, union_format=shop_union_format, do_delete_union=False))
        
        #ガチャ課金額(SP).
        row.append(sum(forEachDays(lambda x:int(redisdb.hget(EventGachaPaymentPointDaily.makeKey(x, False), x.day) or 0))))
        #ガチャ課金額(PC).
        row.append(sum(forEachDays(lambda x:int(redisdb.hget(EventGachaPaymentPointDaily.makeKey(x, True), x.day) or 0))))
        
        #ガチャ課金UU.
        gacha_union_format = "GachaUU##%s"
        row.extend(aggregateUU(EventGachaPaymentUUDaily, union_format=gacha_union_format, do_delete_union=False))
        
        key_shop_sp = shop_union_format % SP
        key_shop_pc = shop_union_format % PC
        key_gacha_sp = gacha_union_format % SP
        key_gacha_pc = gacha_union_format % PC
        inter_key_sp = "INTER##%s" % SP
        inter_key_pc = "INTER##%s" % PC
        
        #両方課金しているUU(SP).
        redisdb.sinterstore(inter_key_sp, key_shop_sp, key_gacha_sp)
        row.append(redisdb.scard(inter_key_sp))
        
        #両方課金しているUU(PC).
        redisdb.sinterstore(inter_key_pc, key_shop_pc, key_gacha_pc)
        row.append(redisdb.scard(inter_key_pc))
        
        
        #両方課金しているUU(両方).
        row.append(len(redisdb.sinter(inter_key_sp, inter_key_pc)))
        
        # 後片付け.
        redisdb.delete(inter_key_sp, key_shop_sp, key_gacha_sp, inter_key_pc, key_shop_pc, key_gacha_pc)
        
        return [row]
