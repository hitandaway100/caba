# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
import settings
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.models.Player import PlayerCrossPromotion
from defines import Defines
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
        #self.output_csv(self.get_dmmid_tutorial_complete(), 'playertutorial')
        # bool_columns = [field.column for field in PlayerCrossPromotion._meta.fields if type(field) is BooleanField]
        # for column in bool_columns:
        #     self.output_csv(self.get_dmmid_column_true(column), column)
        # self.output_csv(self.get_dmmid_total_login(), 'total_login_count')
        #self.output_csv(self.get_dmmid_total_login_greater_than(5), 'total_login_count_greater_5')
        #cabaret_battleresult
        cross_promo_start_time = Defines.CROSS_PROMO_START_TIME.strftime('%Y-%m-%d %H:%M:%S')
        cross_promo_end_time = Defines.CROSS_PROMO_END_TIME.strftime('%Y-%m-%d %H:%M:%S')
        cursor = connections[backup_db].cursor()
        raid_event_master_id = 35
        self.output_csv(self.get_dmmid_tutorial_complete(cross_promo_start_time, cross_promo_end_time, cursor), 'playertutorial')
        self.output_csv(self.get_dmmid_total_login_greater_than(5, cursor), "total_login_count_greater_5")
        self.output_csv(self.get_open_gold_treasure(cross_promo_start_time, cross_promo_end_time, cursor), "open_gold_treasure")
        self.output_csv(self.get_open_cabaclub(cross_promo_start_time, cursor), "open_cabaclub")
        self.output_csv(self.get_userlog_trade(cross_promo_start_time, cross_promo_end_time, cursor), "userlog_trade")
        #self.output_csv(self.get_raidpoint_greater_than(raid_event_master_id, 1000, cursor), "raid_point")
        #self.output_csv(self.get_raidboss_kill_greater_than(raid_event_master_id, 1, cursor), "raidboss_kill_greater_1")
        #self.output_csv(self.get_raidboss_kill_greater_than(raid_event_master_id, 5, cursor), "raidboss_kill_greater_5")
        self.output_csv(self.get_player_level_greater_than(cross_promo_start_time, 10, cursor), "player_level_greater_10")
        self.output_csv(self.get_player_level_greater_than(cross_promo_start_time, 20, cursor), "player_level_greater_20")
        self.output_csv(self.get_play_cabadou(cross_promo_start_time, cursor), "play_cabadou")
        self.output_csv(self.get_play_cabadou_win_continue(cursor), "play_cabadou__win_continue")

    def get_open_gold_treasure(self, start_time, end_time, cursor):
        sql = "SELECT p.dmmid FROM \
        (select uid from `cabaret_treasuregoldopened` where otime between '{0}' and '{1}') AS hoge \
        INNER JOIN cabaret_player p ON hoge.uid = p.id;".format(start_time, end_time)
        return self.exec_sql(cursor, sql)

    def get_open_cabaclub(self, start_time, cursor):
        sql = "SELECT p.dmmid FROM \
        (select uid from `cabaret_cabaclubstoreplayerdata` where ltime >= '{0}') AS hoge \
        INNER JOIN cabaret_player p ON hoge.uid = p.id;".format(start_time)
        return self.exec_sql(cursor, sql)

    def get_userlog_trade(self, start_time, end_time, cursor):
        # 秘宝交換を行ったか
        sql = "SELECT DISTINCT p.dmmid FROM \
        (select uid from `cabaret_userlogtrade` where ctime between '{0}' and '{1}') AS hoge \
        INNER JOIN cabaret_player p ON hoge.uid = p.id;".format(start_time, end_time)
        return self.exec_sql(cursor, sql)

    def get_play_cabadou(self, time, cursor):
        sql = "SELECT p.dmmid FROM \
(select uid from cabaret_battleresult where ctime >= '%s') AS hoge \
INNER JOIN cabaret_player p ON hoge.uid = p.id;" % (time)
        return self.exec_sql(cursor, sql)

    def get_play_cabadou_win_continue(self, cursor):
        sql = "SELECT p.dmmid FROM \
        (select id from cabaret_playercrosspromotion where is_battle_win_continue = True) AS hoge \
        INNER JOIN cabaret_player p ON hoge.id = p.id;"
        return self.exec_sql(cursor, sql)

    def get_gacha_play_count_greater_than(self, gacha_id, count, cursor):
        sql = "SELECT p.dmmid FROM \
(select uid from cabaret_gachaplaycount where mid = %d and cnttotal >= %d) AS raidscore \
INNER JOIN cabaret_player p ON raidscore.uid = p.id;" % (gacha_id, count)
        return self.exec_sql(cursor, sql)

    def get_raidboss_kill_greater_than(self, event_id, count, cursor):
        sql = "SELECT cabaret_player.dmmid FROM \
(SELECT uid from cabaret_raideventscore WHERE mid >= %d and (destroy + destroy_big) >= %d) AS hoge \
INNER JOIN cabaret_player ON hoge.uid=cabaret_player.id" % (event_id, count)
        return self.exec_sql(cursor, sql)

    def get_raidpoint_greater_than(self, raid_id, raid_point, cursor):
        sql = "SELECT p.dmmid FROM \
(select uid from cabaret_raideventscore where mid = %d and point >= %d) AS raidscore \
INNER JOIN cabaret_player p ON raidscore.uid = p.id;" % (raid_id, raid_point)
        return self.exec_sql(cursor, sql)
        
    def get_dmmid_tutorial_complete(self, start_time, end_time, cursor):
        sql = "SELECT cabaret_player.dmmid FROM \
(SELECT playertutorial.id FROM (SELECT * from cabaret_playertutorial WHERE tutorialstate = %d AND etime <= '%s') AS playertutorial \
INNER JOIN cabaret_playerlogin ON cabaret_playerlogin.id=playertutorial.id where cabaret_playerlogin.ltime >= '%s' ) as tutori_login_player \
INNER JOIN cabaret_player ON tutori_login_player.id=cabaret_player.id" % (Defines.TutorialStatus.COMPLETED, end_time, start_time)
        return self.exec_sql(cursor, sql)

    def get_player_level_greater_than(self, time, level, cursor):
        sql = "SELECT cabaret_player.dmmid From \
(SELECT exp.id from (SELECT id FROM cabaret_playerexp where level >= %d) AS exp \
INNER JOIN cabaret_playerlogin ON cabaret_playerlogin.id=exp.id where cabaret_playerlogin.ltime >= '%s') AS 10_login_player \
INNER JOIN cabaret_player ON 10_login_player.id = cabaret_player.id" % (level, time)
        return self.exec_sql(cursor, sql)

    def get_dmmid_total_login_greater_than(self, login_count, cursor):
        sql = 'SELECT p.dmmid FROM \
(SELECT id FROM cabaret_playercrosspromotion WHERE total_login_count >= %d) AS crosspromo \
INNER JOIN cabaret_player p ON crosspromo.id = p.id;' % login_count
        return self.exec_sql(cursor, sql)

    def get_max_playerid(self, cursor, model_name):
        cursor.execute("SELECT MAX(id) FROM cabaret_{};".format(model_name))
        count_result = cursor.fetchall()
        return count_result[0][0]

    def get_dmmid_column_true(self, column):
        sql = 'SELECT p.dmmid FROM \
(SELECT id FROM cabaret_playercrosspromotion WHERE %s = TRUE and id BETWEEN {start} AND {end}) AS crosspromo \
INNER JOIN cabaret_player p ON crosspromo.id = p.id;' % (column)
        return self.get_sql(sql, 'bool')

    def exec_sql(self, cursor, sql):
        print sql
        cursor.execute(sql)
        return cursor.fetchall()
        
    def get_sql(self, sql, type):
        cursor = connections[backup_db].cursor()
        max_id = self.get_max_playerid(cursor, 'playercrosspromotion')
        results = ()
        for i in range(max_id / BATCH_SIZE + 1):
            if type == 'tutorial':
                format = {'status': Defines.TutorialStatus.COMPLETED, 'etime': Defines.CROSS_PROMO_END_TIME.strftime('%Y-%m-%d %H:%M:%S'),
                          'start': i*BATCH_SIZE+1, 'end': (i+1)*BATCH_SIZE}
            else:
                format = {'start': i*BATCH_SIZE+1, 'end': (i+1)*BATCH_SIZE}
            cursor.execute(sql.format(**format))
            result = cursor.fetchall()
            results += result
            print sql

            time.sleep(0.3)
        return results

    def output_csv(self, id_list, column):
        with open('crosspromo_{}.csv'.format(column), 'w') as f:
            writer = csv.writer(f)
            writer.writerows(id_list)
