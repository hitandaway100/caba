# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.present import PrizeData
from platinumegg.app.cabaret.models.Present import PrizeMaster
#from defines import Defines
from platinumegg.app.cabaret.util.api import BackendApi
import settings_sub
from platinumegg.app.cabaret.models.Player import Player
import settings
from defines import Defines
import csv
import os
import time

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)
TEXTID = 116
class Command(BaseCommand):
    """お詫びを一括配布.
    """
    def handle(self, *args, **options):
        commands_path = os.path.dirname(os.path.realpath(__file__))
        env_path = os.path.join(commands_path, "crosspromo_prize_csv/noahs_gate")
        
        self.send_prize(env_path, "tutorial", [110303, 120303])
        self.send_prize(env_path, "10f", [611043])
        self.send_prize(env_path, "ero_scene", [600301])
        self.send_prize(env_path, "raid_boss_1", [611075])
        self.send_prize(env_path, "5login", [610425])
        self.send_prize(env_path, "raid_boss_10", [400305])
        self.send_prize(env_path, "20f", [611044])
        self.send_prize(env_path, "user_rank_20", [610524])
        self.send_prize(env_path, "trade", [410301])

    def send_prize(self, csv_dir, csv_name, prize_ids):
        print '================================'
        print csv_name
        print '================================'
        file_path = os.path.join(csv_dir, csv_name + ".csv")
        
        model_mgr = ModelRequestMgr()
        prizelist = model_mgr.get_models(PrizeMaster, prize_ids, using=backup_db)
        
        self.send_prize_from_csv(file_path, prizelist, TEXTID, "send_prize_" + csv_name)

    def send_prize_from_csv(self, csv_path, prizelist, textid, method_name):
        BATCH_SIZE = 1000

        with open(csv_path, 'r') as f:
            spamReader = csv.reader(f)

            dmmids_buffer = []
            for row in spamReader:
                dmmids_buffer.append(row[0])
                if len(dmmids_buffer) == BATCH_SIZE:
                    self.send_owabi(self.get_playerids(dmmids_buffer).values(), prizelist, textid, method_name)
                    dmmids_buffer = []
                    time.sleep(1)
            self.send_owabi(self.get_playerids(dmmids_buffer).values(), prizelist, textid, method_name)

    def get_playerids(self, dmmids):
        dmmid_list = list(set(dmmids))
        uid_to_dmmid = dict([(int(p.dmmid), int(p.id)) for p in Player.fetchValues(['id', 'dmmid'], filters={'dmmid__in':dmmid_list}, using=backup_db)])
        
        return uid_to_dmmid
        
    def send_owabi(self, uids, prizelist, textid, method_name, is_write=True):
        for uid in uids:
            if is_write:
                def tr(uid, prizelist, textid):
                    model_mgr = ModelRequestMgr()
                    
                    BackendApi.tr_add_prize(model_mgr, uid, prizelist, textid)
                    model_mgr.write_all()
                    return model_mgr
                model_mgr = db_util.run_in_transaction(tr, uid, prizelist, textid)
                try:
                    model_mgr.write_end()
                    print uid
                except:
                    print 'Error {0}:{1}'.format(method_name,uid)
