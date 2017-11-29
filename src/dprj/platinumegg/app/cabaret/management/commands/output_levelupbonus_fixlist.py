# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
import settings_sub
import os
from platinumegg.app.cabaret.models.UserLog import UserLogLevelUpBonus
from platinumegg.app.cabaret.models.LevelUpBonus import LevelUpBonusPlayerData
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
import settings

class Command(BaseCommand):
    def handle(self, *args, **options):
        model_mgr = ModelRequestMgr()
        levelupbonus_logs =  UserLogLevelUpBonus.all(using=settings.DB_READONLY)
        
        leveldatas = {}
        for levelupbonus_log in levelupbonus_logs:
            if not leveldatas.has_key(levelupbonus_log.uid) or leveldatas[levelupbonus_log.uid] < levelupbonus_log.level:
                leveldatas[levelupbonus_log.uid] = levelupbonus_log.level
        
        for k, v in leveldatas.items():
            print "{},{}".format(k, v)
