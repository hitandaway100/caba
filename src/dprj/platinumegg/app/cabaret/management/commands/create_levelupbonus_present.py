# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.db import connections

from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.models.LevelUpBonus import LevelUpBonusMaster, LevelUpBonusPlayerData
from platinumegg.app.cabaret.models.UserLog import UserLogLevelUpBonus

import settings
from defines import Defines

class Command(BaseCommand):
    """レベルアップ達成ボーナスを事前に配布する.
    """
    def handle(self, *args, **options):
        
        print '================================'
        print 'create_levelupbonus_present'
        print '================================'

        model_mgr = ModelRequestMgr()
        appconfig = BackendApi.get_appconfig(model_mgr)
        if not appconfig.is_maintenance():
            print u'メンテナンスモードにしてください'
            return
        print 'check maintenance...OK\n'

        cursor = connections[settings.DB_DEFAULT].cursor()
        self.stdout.write(
            '!!! LevelUpBonus Version {}. MasterDB: {} !!!'.format(
                Defines.LEVELUP_BONUS_VERSION,
                settings.DATABASES[cursor.db.alias]['HOST']
            )
        )
        cursor.execute('select id, level from cabaret_playerexp;')
        rows = cursor.fetchall()

        cursor.execute('select uid from cabaret_levelupbonusplayerdata where mid={};'.format(Defines.LEVELUP_BONUS_VERSION))
        levelupbonus_uidlist = set([x[0] for x in cursor.fetchall()])

        errorlist = []
        midlist = BackendApi.get_levelupbonus_master(model_mgr, Defines.LEVELUP_BONUS_VERSION)
        masterlist = BackendApi.get_model_list(model_mgr, LevelUpBonusMaster, midlist)
        uid_index, level_index = (0, 1)
        for row in rows:
            if row[uid_index] not in levelupbonus_uidlist:
                print 'userid: {}. level: {}'.format(row[uid_index], row[level_index])
                for master in masterlist:
                    if master.level <= row[level_index]:
                        print 'level: {}'.format(master.level)
                        print 'prizeid: {}'.format(master.prize_id)
                        prizelist = BackendApi.get_prizelist(model_mgr, master.prize_id)
                        key = LevelUpBonusPlayerData.makeID(row[uid_index], Defines.LEVELUP_BONUS_VERSION)
                        playerdata = LevelUpBonusPlayerData.createInstance(key)
                        playerdata.last_prize_level = row[level_index]
                        userlog = UserLogLevelUpBonus.create(row[uid_index], master.version, master.prize_id, master.level)
                        try:
                            db_util.run_in_transaction(self.tr_prezent, row[uid_index], prizelist, playerdata, userlog, master.levelupbonus_text)
                        except Exception as e:
                            print 'present error: {}'.format(e)
                            errorlist.append((row[uid_index], master.level))

        for error in errorlist:
            print 'uid: {}, master.level: {}'.format(error[uid_index], error[level_index])

    def tr_prezent(self, uid, prizelist, data, userlog, text):
        model_mgr = ModelRequestMgr()
        model_mgr.set_save(data)
        model_mgr.set_save(userlog)
        BackendApi.tr_add_prize(model_mgr, uid, prizelist, text)
        model_mgr.write_all()
        model_mgr.write_end()
