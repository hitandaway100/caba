# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.present import PrizeData, Present
#from defines import Defines
from platinumegg.app.cabaret.util.api import BackendApi
import settings_sub
from platinumegg.app.cabaret.models.Player import Player
from platinumegg.app.cabaret.models.UserLog import UserLogGacha
import settings
from defines import Defines

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)


class Command(BaseCommand):
    """ガチャのログから特定のガチャを回した人を探す
    """
    def handle(self, *args, **options):
        print '================================'
        print 'find logs'
        print '================================'

        model_mgr = ModelRequestMgr()

        START_TIME = '2016-09-05 16:00:00'
        END_TIME = '2016-09-16 15:00:00'

        MIDS = range(385, 393)  # 戦国コラボガチャ前半
        MIDS2 = range(402, 410)  # 戦国コラボガチャ後半

        receivelogs = UserLogGacha.fetchValues(
            filters={
                'ctime__gt': START_TIME,
                'ctime__lt': END_TIME
            }, using=backup_db)

        userids = []
        for log in receivelogs:
            if log.mid in (MIDS + MIDS2):
                userids.append(log.uid)

        users = BackendApi.get_model_list(model_mgr, Player,
                                           list(set(userids)),
                                           using=backup_db)

        for dmmid in list({user.dmmid for user in users}):
            print dmmid

def is_cardids(cardids, rarity):
    def is_ssr(x):
        rare = str(x)[1]
        return int(rare) == rarity

    for idx in cardids:
        if is_ssr(idx):
            return True
    return False
