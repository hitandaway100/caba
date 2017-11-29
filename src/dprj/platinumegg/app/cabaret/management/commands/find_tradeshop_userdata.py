# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.api import BackendApi
import settings_sub
from platinumegg.app.cabaret.models.Player import Player
from platinumegg.app.cabaret.models.UserLog import UserLogTradeShop
import settings
from defines import Defines

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)


class Command(BaseCommand):
    """交換所のログから指定の ID のアイテムを引いたユーザを探す.
    """
    def handle(self, *args, **options):
        print '================================'
        print 'find user ids'
        print '================================'

        model_mgr = ModelRequestMgr()

        START_TIME = '2016-07-04 16:00:00'
        END_TIME = '2016-07-04 16:50:00'

        SSR_MID = 12
        CAST_MID = 13

        receivelogs = UserLogTradeShop.fetchValues(
            filters={
                'ctime__gt': START_TIME,
                'ctime__lt': END_TIME
            }, using=backup_db)

        for mid in (SSR_MID, CAST_MID):
            print('Start : {}'.format(mid))
            for log in receivelogs:
                if log.shopitemid == mid:
                    print(log.uid)
