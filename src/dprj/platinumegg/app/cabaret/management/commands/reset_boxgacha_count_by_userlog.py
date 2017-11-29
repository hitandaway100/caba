# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.present import PrizeData, Present
#from defines import Defines
from platinumegg.app.cabaret.util.api import BackendApi
import settings_sub
from platinumegg.app.cabaret.models.Player import Player
from platinumegg.app.cabaret.models.Gacha import GachaBoxResetPlayerData
from platinumegg.app.cabaret.models.UserLog import UserLogGacha
import settings
from defines import Defines

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)


class Command(BaseCommand):
    """ガチャのログから特攻 BOX ガチャを引いた人を検索して リセットカウントをリセットする.
    """
    def handle(self, *args, **options):
        print '================================'
        print 'find logs'
        print '================================'

        model_mgr = ModelRequestMgr()

        START_TIME = '2016-06-30 16:00:00'
        END_TIME = '2016-07-01 18:00:00'

        MID = 1249

        receivelogs = UserLogGacha.fetchValues(
            filters={
                'ctime__gt': START_TIME,
                'ctime__lt': END_TIME
            }, using=backup_db)

        userids = []
        for log in receivelogs:
            if log.mid == MID:
                userids.append(log.uid)

        for uid in list(set(userids)):
            print(uid)
            try:
                db_util.run_in_transaction(self.tr_write, uid)
            except:
                print('{}...NG'.format(uid))

    def tr_write(self, uid):
        model_mgr = ModelRequestMgr()

        def forUpdate(instance, inserted):
            instance.resetcount = 0

        model_mgr.add_forupdate_task(GachaBoxResetPlayerData, uid, forUpdate)

        model_mgr.write_all()
        model_mgr.write_end()
