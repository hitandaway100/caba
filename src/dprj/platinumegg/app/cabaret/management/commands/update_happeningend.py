# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from platinumegg.lib.opensocial.util import OSAUtil
import datetime
from platinumegg.app.cabaret.models.Happening import Happening
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util import db_util
from defines import Defines
from platinumegg.app.cabaret.util.cabareterror import CabaretError
import settings

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)

class Command(BaseCommand):
    """成功したハプニングを更新する.
    """
    def handle(self, *args, **options):
        
        print '================================'
        print 'update_happeningend'
        print '================================'
        
        # 有効期限.
        now = OSAUtil.get_now()
        limittime = now - datetime.timedelta(seconds=600)
        
        # レイド発生中で期限切れのハプニングを取得.
        happeninglist = Happening.fetchValues(['id'], {'state':Defines.HappeningState.CLEAR, 'etime__lte':limittime}, limit=30000, using=backup_db)
        
        def tr(happeningid):
            model_mgr = ModelRequestMgr()
            happening = Happening.getByKeyForUpdate(happeningid)
            raidboss = BackendApi.get_raid(model_mgr, happening.id, happening_eventvalue=happening.event)
            BackendApi.tr_happening_end(model_mgr, happening, raidboss)
            model_mgr.write_all()
            return model_mgr
        
        for happening in happeninglist:
            try:
                model_mgr = db_util.run_in_transaction(tr, happening.id)
                model_mgr.write_end()
            except CabaretError, err:
                if err.code == CabaretError.Code.ALREADY_RECEIVED:
                    pass
                else:
                    raise
            print 'update %d end' % happening.id
        
        print '================================'
        print 'all end..'
        print 'update num = %d' % len(happeninglist)
