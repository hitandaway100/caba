# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
import settings_sub
import os
from platinumegg.app.cabaret.models.UserLog import UserLogLevelUpBonus
from platinumegg.app.cabaret.models.LevelUpBonus import LevelUpBonusPlayerData
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util import db_util
import settings
import csv
import time
from defines import Defines

class Command(BaseCommand):
    def handle(self, *args, **options):
        print "BATCH START"
        levelupbonus_logs =  UserLogLevelUpBonus.all(using=settings.DB_READONLY)
        commands_path = os.path.dirname(os.path.realpath(__file__))
        csv_path = os.path.join(commands_path, "levelupbonus_csv/levelupbonus.csv")
        
        with open(csv_path, 'r') as f:
            def tr(rows):
                model_mgr = ModelRequestMgr()
                
                for row in rows:
                    key = LevelUpBonusPlayerData.makeID(int(row[0]), Defines.LEVELUP_BONUS_VERSION)
                    playerdata = model_mgr.get_model(LevelUpBonusPlayerData, key)
                    if not playerdata:
                        print "irregular user {}".format(row[0])
                    else:
                        playerdata.last_prize_level = row[1]
                        model_mgr.set_save(playerdata)
                model_mgr.write_all()
                model_mgr.write_end()
                
            spamReader = csv.reader(f)
            rows = []
            for i, row in enumerate(spamReader):
                rows.append(row)
                if i % 1000 == 0:
                    print "now...{}".format(row[0])
                    db_util.run_in_transaction(tr, rows)
                    rows = []
            db_util.run_in_transaction(tr, rows)
            print "All End"
