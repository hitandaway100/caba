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
    """ガチャのリセット回数を全ユーザ 0 にする.
    """
    def handle(self, *args, **options):
        print '================================'
        print 'reset box gacha reset_count.'
        print '================================'

        model_mgr = ModelRequestMgr()

        users = Player.objects.all()
        for user in users:
            print(user.id)
            try:
                db_util.run_in_transaction(self.tr_write, user.id)
            except:
                print('{}...NG'.format(user.id))

    def tr_write(self, uid):
        model_mgr = ModelRequestMgr()

        def forUpdate(instance, inserted):
            instance.resetcount = 0

        model_mgr.add_forupdate_task(GachaBoxResetPlayerData, uid, forUpdate)

        model_mgr.write_all()
        model_mgr.write_end()
