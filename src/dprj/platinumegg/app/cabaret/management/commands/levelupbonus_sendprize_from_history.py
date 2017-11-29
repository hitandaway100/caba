# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
import settings
import datetime
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from defines import Defines
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.models.base.queryset import Query
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.models.UserLog import UserLogLevelUpBonus
from platinumegg.app.cabaret.models.LevelUpBonus import LevelUpBonusPlayerData, LevelUpBonusMaster
from optparse import make_option
from collections import namedtuple

class Command(BaseCommand):
    """レベルアップ報酬が中抜けしているユーザにプレゼントを配るプログラム.
    """
    option_list = BaseCommand.option_list + (
        make_option('-d', '--dry-run', action="store_true", dest="dry_run", default=False),
    )

    def handle(self, *args, **options):
        model_mgr = ModelRequestMgr()
        print "now get UserLogLevelUpBonus"
        levelupbonus_logs =  UserLogLevelUpBonus.all(using=settings.DB_READONLY)
        logs_each_player = self.get_logs_each_player(levelupbonus_logs)
        
        print "now get LevelUpBonusMaster"
        levelupbonus_masters =  LevelUpBonusMaster.all(using=settings.DB_READONLY)
        levelup_master_levels = [i.level for i in levelupbonus_masters]
        levelup_master_levels.sort()
        
        print "start check_miss_and_sendprize"
        self.check_miss_and_sendprize(model_mgr, logs_each_player, levelupbonus_masters, levelup_master_levels, options["dry_run"])

    def get_logs_each_player(self, levelupbonus_logs):
        logs_each_player = {}
        for levelupbonus_log in levelupbonus_logs:
            if not logs_each_player.has_key(levelupbonus_log.uid):
                logs_each_player[levelupbonus_log.uid] = []
            logs_each_player[levelupbonus_log.uid].append(levelupbonus_log)
        return logs_each_player;

    def check_miss_level(self, levelupbonus_logs, levelupbonus_master_levels):
        max_level = max(levelupbonus_logs, key=lambda x:x.level).level
        index = levelupbonus_master_levels.index(max_level)
        master_levels = levelupbonus_master_levels[0:index]
        log_levels = [i.level for i in levelupbonus_logs]
        miss_levels = set(master_levels) - set(log_levels)
        return list(miss_levels)
        
    def __checkLevelUpBonus_tr_write(self, uid, prizelistdata, levelup_bonus_logs):
        model_mgr = ModelRequestMgr()

        for prizelist_data in prizelistdata:
            BackendApi.tr_add_prize(model_mgr, uid, prizelist_data.prizelist, prizelist_data.text)
        for levelup_prize_log in levelup_bonus_logs:
            model_mgr.set_save(levelup_prize_log)

        model_mgr.write_all()
        model_mgr.write_end()
        
    def check_miss_and_sendprize(self, model_mgr, logs_each_player, levelupbonus_masters, levelup_master_levels, is_dry):
        counter = 0
        for uid, levelupbonus_logs in logs_each_player.items():
            misslevel = self.check_miss_level(levelupbonus_logs, levelup_master_levels)
            if misslevel:
                levelup_bonus_logs = []
                prizelistdata = []
                PrizelistData = namedtuple('PrizelistData', ('prizelist', 'text'))
        
                print "uid={} sendprize LEVEL:{}".format(uid, misslevel)
                miss_levelupbonus_masters = [i for i in levelupbonus_masters if i.level in misslevel]
                for levelupbonus_master in miss_levelupbonus_masters:
                    prizelist = BackendApi.get_prizelist(model_mgr, levelupbonus_master.prize_id, using=settings.DB_READONLY)
                    prizelistdata.append(PrizelistData(prizelist, levelupbonus_master.levelupbonus_text))
                    levelup_bonus_logs.append(UserLogLevelUpBonus.create(uid, levelupbonus_master.version, levelupbonus_master.prize_id, levelupbonus_master.level))
                if not is_dry:
                    db_util.run_in_transaction(self.__checkLevelUpBonus_tr_write, uid, prizelistdata, levelup_bonus_logs)
            counter += 1
            if counter % 1000 == 0:
                print "now...{}".format(uid)
