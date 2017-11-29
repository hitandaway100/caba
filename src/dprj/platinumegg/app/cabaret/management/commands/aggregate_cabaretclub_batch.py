# -*- coding: utf-8 -*-

from datetime import timedelta
import time

from django.core.management.base import BaseCommand

from platinumegg.app.cabaret.models.CabaretClub import CabaClubStoreMaster
from platinumegg.app.cabaret.models.CabaretClub import CabaClubStorePlayerData
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.cabaclub_store import CabaclubStoreSet
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.datetime_util import DateTimeUtil
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.lib.opensocial.util import DbgLogger
from platinumegg.lib.opensocial.util import OSAUtil
import settings

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)
BATCH_SIZE = 500

class Command(BaseCommand):
    """キャバクラシステムの定期集計."""

    def handle(self, *args, **options):
        print('===========================')
        print('aggregate_cabaretclub_batch')
        print('===========================')

        model_mgr = ModelRequestMgr()

        section_lasttime = self.get_batch_section_lasttime()

        storemaster_list = model_mgr.get_mastermodel_all(CabaClubStoreMaster, fetch_deleted=True, using=backup_db)
        storemaster_all_dict = dict([(storemaster.id, storemaster) for storemaster in storemaster_list])
        max_uid = CabaClubStorePlayerData.max_value('uid', using=backup_db)

        offset = 0
        uids = range(1, max_uid+1)
        while uids[offset:offset+BATCH_SIZE]:
            print "Done... now %d Max %d" % (offset, max_uid)
            for uid in uids[offset:offset+BATCH_SIZE]:
                self.update_cabaretclub_proceed(uid, storemaster_all_dict, section_lasttime)
            offset += BATCH_SIZE
            time.sleep(1)

        print "all done."

    def update_cabaretclub_proceed(self, uid, storemaster_all_dict, section_lasttime):
        store_list = CabaClubStorePlayerData.fetchByOwner(uid, using=settings.DB_READONLY)
        if not store_list:
            return

        open_stores = [store for store in store_list if store.is_open]
        for store in open_stores:
            storemaster = storemaster_all_dict[store.mid]
            store_set = CabaclubStoreSet(storemaster, store)
            lasttime = min(section_lasttime, store_set.get_limit_time()-timedelta(microseconds=1))
            if (lasttime-store.utime).total_seconds() < storemaster.customer_interval:
                return

            try:
                db_util.run_in_transaction(self.tr_write, uid, storemaster, lasttime)
            except CabaretError as err:
                if err.code == CabaretError.Code.ALREADY_RECEIVED:
                    pass
                else:
                    DbgLogger.write_error(err.value)
                    raise

    def get_batch_section_lasttime(self):
        """バッチで確認する時間の境界."""
        now = OSAUtil.get_now()
        basetime = DateTimeUtil.toBaseTime(now, now.hour)
        return basetime - timedelta(microseconds=1)

    def tr_write(self, uid, storemaster, now):
        """店舗の時間を進める."""
        model_mgr = ModelRequestMgr()
        BackendApi.tr_cabaclubstore_advance_the_time_with_checkalive(model_mgr, uid, storemaster, now)
        model_mgr.write_all()
        model_mgr.write_end()
        print "Done %d" % uid
