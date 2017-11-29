# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.models.ReprintTicketTradeShop import ReprintTicketTradeShopPlayerData
from platinumegg.app.cabaret.util.cabareterror import CabaretError
import time
import settings
from defines import Defines


class Command(BaseCommand):
    """現在開催中のユーザーの復刻チケット交換回数の初期化
    """
    def handle(self, *args, **options):
        print '================================'
        print 'init_reprintticket'
        print '================================'

        model_mgr = ModelRequestMgr()

        # メンテナンス確認
        appconfig = BackendApi.get_appconfig(model_mgr)
        if not appconfig.is_maintenance():
            print u'メンテナンスモードにしてください'
            return
        print 'check maintenance...OK\n'

        # 在開催中の復刻チケット
        reprintticket_tradeshopmaster = BackendApi.get_current_reprintticket_tradeshopmaster(model_mgr, using=settings.DB_READONLY)
        ticketids = [master.id for master in reprintticket_tradeshopmaster
                     if master.ticket_id == Defines.GachaConsumeType.GachaTicketType.REPRINT_TICKET]
        print "Current Reprint ticket ids: ", ticketids

        # ユーザーの復刻チケットのデータ取得
        playerdatalist = ReprintTicketTradeShopPlayerData.fetchValues(filters={'mid__in': ticketids})

        offset = 0
        limit = 3000

        print "Number of player data entries = %d" % len(playerdatalist)
        print "Reset users' reprint ticket count to 0..."
        while self.reset_reprintticket(playerdatalist[offset:offset+limit]):
            offset += limit

        print '================================'
        print 'all done.'

    def reset_reprintticket(self, playerdatalist):
        if playerdatalist:
            model_mgr = ModelRequestMgr()

            def tr_write(playerdatalist):
                for data in playerdatalist:
                    data.cnt = 0
                    print "uid: %d, mid: %d, cnt => %d" % (data.uid, data.mid, data.cnt)
                    model_mgr.set_save(data)
                model_mgr.write_all()
                return model_mgr

            try:
                tmp_model_mgr = db_util.run_in_transaction(tr_write, playerdatalist)
            except CabaretError, err:
                print "An error occured when resetting users' reprint ticket count"
                print 'error...%s' % err.value
                return

            tmp_model_mgr.write_end()
            time.sleep(0.15)
            return True

        return False

