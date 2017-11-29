# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from platinumegg.app.cabaret.kpi.models.login import WeeklyLoginSet
from platinumegg.lib.opensocial.util import OSAUtil
import datetime
from platinumegg.app.cabaret.kpi.models.payment import FQ5PaymentSet,\
    DailyPaymentPointSet
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.models.Gacha import GachaMaster
import settings
from platinumegg.app.cabaret.kpi.models.event import EventJoinDaily,\
    EventPlayDaily, EventGachaPaymentUUDaily, EventShopPaymentUUDaily,\
    EventGachaPaymentPointDaily, EventShopPaymentPointDaily

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)

class Command(BaseCommand):
    """KPI集計用のデータをお掃除.
    """
    def handle(self, *args, **options):
        
        print '================================'
        print 'clean_kpi'
        print '================================'
        
        now = OSAUtil.get_now()
        
        print 'delete WeeklyLoginSet'
        # 9から11日のログインを削除.
        redisdb = WeeklyLoginSet.getDB()
        keys = [WeeklyLoginSet.makeKey(now - datetime.timedelta(days=days)) for days in xrange(9, 12)]
        if keys:
            redisdb.delete(*keys)
        
        print 'delete FQ5PaymentSet'
        # 40日前のFQ5を削除.
        model_mgr = ModelRequestMgr()
        
        gachamidlist = model_mgr.get_mastermodel_idlist(GachaMaster, using=backup_db)
        redisdb = FQ5PaymentSet.getDB()
        
        target_date = now - datetime.timedelta(days=40)
        keys = [FQ5PaymentSet.makeKey(target_date, mid) for mid in gachamidlist]
        if keys:
            redisdb.delete(*keys)
        
        # 60から65日前のイベントレポートを削除.
        print 'delete EventReport'
        redisdb = EventJoinDaily.getDB()
        for days in xrange(60, 65):
            target_date = now - datetime.timedelta(days=days)
            redisdb.delete(
                EventJoinDaily.makeKey(target_date, False),
                EventJoinDaily.makeKey(target_date, True),
                EventPlayDaily.makeKey(target_date, False),
                EventPlayDaily.makeKey(target_date, True),
                EventGachaPaymentUUDaily.makeKey(target_date, False),
                EventGachaPaymentUUDaily.makeKey(target_date, True),
                EventShopPaymentUUDaily.makeKey(target_date, False),
                EventShopPaymentUUDaily.makeKey(target_date, True),
                EventGachaPaymentPointDaily.makeKey(target_date, False),
                EventGachaPaymentPointDaily.makeKey(target_date, True),
                EventShopPaymentPointDaily.makeKey(target_date, False),
                EventShopPaymentPointDaily.makeKey(target_date, True),
            )
        
        # 40から45日前の消費ポイントを削除.
        print 'delete EventReport'
        redisdb = DailyPaymentPointSet.getDB()
        keys = [for days in xrange(40, 45)]
        for days in xrange(40, 45):
            target_date = now - datetime.timedelta(days=days)
            
        
        print 'all done'
