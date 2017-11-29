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
    """BOXガチャのリセット情報等の初期化.
    """
    def handle(self, *args, **options):
        print '================================'
        print 'init_boxgachadetail'
        print '================================'

        model_mgr = ModelRequestMgr()

        # メンテナンス確認
        appconfig = BackendApi.get_appconfig(model_mgr)
        if not appconfig.is_maintenance():
            print u'メンテナンスモードにしてください'
            return
        print 'check maintenance...OK\n'

        delete_target_model_cls_list = (
            GachaBoxResetPlayerData,
        )
        def tr():
            for model_cls in delete_target_model_cls_list:
                tablename = model_cls.get_tablename()
                query_string = 'truncate table `{}`;'.format(tablename)
                Query.execute_update(query_string, [], False)
                print 'delete...{}'.format(tablename)
        db_util.run_in_transaction(tr)

        print '================================'
        print 'all done.'
