# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
import settings
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util import db_util
from django.db import connections
import time
from platinumegg.app.cabaret.models import PlayerCrossPromotion
from platinumegg.app.cabaret.models.base.queryset import Query

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)
SQL = """
SELECT DISTINCT player.id, store.is_open, battle.rank, exp.level FROM
(SELECT * FROM cabaret_player WHERE cabaret_player.id BETWEEN {} AND {}) as player
LEFT JOIN cabaret_battleplayer battle ON player.id = battle.id
LEFT JOIN cabaret_cabaclubstoreplayerdata store ON player.id = store.uid and store.is_open=1
LEFT JOIN cabaret_playerexp exp ON player.id = exp.id;
"""[1:-1]

class Command(BaseCommand):
    """ クロスプロモーション期間開始時の既存ユーザーに対するバッチ処理
    """
    def handle(self, *args, **options):
        delete_target_model_cls_list = (
            PlayerCrossPromotion,
        )
        def tr():
            for model_cls in delete_target_model_cls_list:
                tablename = model_cls.get_tablename()
                query_string = "truncate table `%s`;" % tablename
                Query.execute_update(query_string, [], False)
                print 'delete...%s' % tablename
        db_util.run_in_transaction(tr)

        if args and args[0] == 'set_user_status':
            self.set_user_status()

    def set_user_status(self):
        cursor = connections[backup_db].cursor()
        MAX_ID = self.get_max_player_id(cursor)
        BATCH_SIZE = 1000
        for i in range(MAX_ID/BATCH_SIZE+1):
            sql = SQL.format(i*BATCH_SIZE+1, (i+1)*BATCH_SIZE)
            print sql
            cursor.execute(sql)
            bulk_insert_list = [self.bulk_insert_instance(result) for result in cursor.fetchall()]

            try:
                PlayerCrossPromotion.objects.bulk_create(bulk_insert_list)
            except Exception as exception:
                print "--------Error------"
                print exception
                print "-------------------"
                continue
            time.sleep(0.3)

    def get_max_player_id(self, cursor):
        cursor.execute('SELECT MAX(id) FROM cabaret_player;')
        return cursor.fetchone()[0]

    def bulk_insert_instance(self, flags):
        return PlayerCrossPromotion(id=flags[0],
                                    is_open_cabaclub=self.is_open(flags[1]),
                                    is_battle_rank5=self.is_rank5(flags[2]),
                                    is_level10=self.is_level10(flags[3]),
                                    is_level20=self.is_level20(flags[3]))

    def is_open(self, status):
        return 0 < status

    def is_level10(self, level):
        return 10 <= level

    def is_level20(self, level):
        return 20 <= level

    def is_rank5(self, rank):
        return 5 <= rank
