# -*- coding: utf-8 -*-
import time

from django.core.management.base import BaseCommand
from django.db import connections, transaction

from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.models.Gacha import GachaBoxResetPlayerData
from platinumegg.app.cabaret.models.base.queryset import Query

import settings
from defines import Defines

class Command(BaseCommand):
    """BOXガチャのリセット情報等の修正.
    """
    def handle(self, *args, **options):
        print '================================'
        print 'repair_boxgachaplayerdata'
        print '================================'

        model_mgr = ModelRequestMgr()
        try:
            target_uid = int(args[0])
        except:
            print 'invalid argument'
            return
        is_write = (args[1] if len(args) == 2 else '0') == 'write'

        try:
            if is_write:
                db_util.run_in_transaction(self.tr, target_uid)
                print('id : {}'.format(target_uid))
            else:
                data = model_mgr.get_model(GachaBoxResetPlayerData, target_uid, using=settings.DB_DEFAULT)
                print 'id : {}, resetcount: {}, is_get_targetrarity: {}'.format(data.id, data.resetcount, data.is_get_targetrarity)
        except:
            print 'error: {}'.format(target_uid)

        print '================================'
        print 'all done.'

    def tr(self, target_uid):
        model_mgr = ModelRequestMgr()

        def forUpdate(model, inserted):
            model.resetcount = 2
        model_mgr.add_forupdate_task(GachaBoxResetPlayerData, target_uid, forUpdate)

        model_mgr.write_all()
        model_mgr.write_end()
