# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
import settings
from platinumegg.app.cabaret.models.PaymentEntry import ShopPaymentEntry,\
    GachaPaymentEntry
from django.db import connections

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)
 
class Command(BaseCommand):
    """トップ層の課金ユーザの出力.
    """
    def handle(self, *args, **options):
        LIMIT = 50
        START_TIME = "2016-03-01 00:00:00"
        END_TIME = "2016-04-01 00:00:00"
        
        results = self.get_gachapaymententry(LIMIT, START_TIME, END_TIME)
        self.output_csv(results)

    def get_gachapaymententry(self, limit, from_time, end_time):
        GachaPaymentEntry.sql("", using=backup_db)
        cursor = connections[backup_db].cursor()
        sql = "SELECT uid,sum(price) AS sum_price FROM cabaret_gachapaymententry WHERE ctime >= '{}' AND ctime < '{}' GROUP BY uid ORDER BY sum_price DESC LIMIT {};".format(
            from_time, end_time, limit
        )
        cursor.execute(sql)
        return cursor.fetchall()

    def output_csv(self, results):
        print "rank,user_id,price"
        for i,result in enumerate(results):
            print str(i+1) + "," + str(result[0]) + "," + str(result[1])
