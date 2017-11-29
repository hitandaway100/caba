# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.lib.opensocial.util import OSAUtil
import settings_sub
from platinumegg.app.cabaret.models.Mission import PanelMissionData
import settings
from defines import Defines

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)

class Command(BaseCommand):
    """お詫びを一括配布.
    """
    def handle(self, *args, **options):
        print '================================'
        print 'upate_store'
        print '================================'
        model_mgr = ModelRequestMgr()

        try:
            target_id = int(args[0])
        except:
            print 'invalid argument'
            return
        is_write = (args[1] if len(args) == 2 else '0') == 'write'

        try:
            if is_write:
                db_util.run_in_transaction(self.tr, target_id)
            else:
                data = model_mgr.get_model(PanelMissionData, target_id, using=settings.DB_DEFAULT)
                print('id: {}, uid: {}, mid: {}, cnt5: {}, etime5: {}'.format(
                    data.id, data.uid, data.mid, data.cnt5, data.etime5)
                )
        except:
            print('error: {}'.format(target_id))

    def tr(self, target_id):
        model_mgr = ModelRequestMgr()

        def forUpdate(model, inserted):
            model.cnt5 = 100
            model.etime5 = OSAUtil.get_now()
        model_mgr.add_forupdate_task(PanelMissionData, target_id, forUpdate)

        model_mgr.write_all()
        model_mgr.write_end()
