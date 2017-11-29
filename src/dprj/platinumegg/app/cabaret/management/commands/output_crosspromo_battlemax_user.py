# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
import settings
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from django.db import connections
import time
import csv
from django.db.models.fields import BooleanField

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)
BATCH_SIZE = 1000

class Command(BaseCommand):
    """クロスプロモの出力.
    """
    def handle(self, *args, **options):
        sql = "SELECT cabaret_player.dmmid FROM (SELECT * FROM cabaret_battleplayer where id BETWEEN {start} AND {end} AND cabaret_battleplayer.rank = 20) AS battleplayer INNER JOIN cabaret_player ON battleplayer.id=cabaret_player.id"
        results = self.get_sql(sql)
        self.output_csv(results, 'battlemax_users')
        
    def get_sql(self, sql):
        cursor = connections[backup_db].cursor()
        max_id = self.get_max_playerid(cursor, 'player')
        results = ()
        for i in range(max_id / BATCH_SIZE + 1):
            between = {'start': i*BATCH_SIZE+1, 'end': (i+1)*BATCH_SIZE}
            print sql.format(**between)
            cursor.execute(sql.format(**between))
            result = cursor.fetchall()
            results += result

            time.sleep(1)
        return results
        
    def get_max_playerid(self, cursor, model_name):
        cursor.execute("SELECT MAX(id) FROM cabaret_{};".format(model_name))
        count_result = cursor.fetchall()
        return count_result[0][0]
        
    def output_csv(self, id_list, column):
        try:
            f = open('crosspromo_{}.csv'.format(column), 'w')
            writer = csv.writer(f)
            writer.writerows(id_list)
        finally:
            f.close()
