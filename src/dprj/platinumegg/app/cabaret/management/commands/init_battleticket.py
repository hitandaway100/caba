# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
import settings
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.models.Gacha import GachaTicket
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.datetime_util import DateTimeUtil
import datetime

class Command(BaseCommand):
    """バトルチケット所持数初期化.
    """
    battleticket_id = 23

    def handle(self, *args, **options):
        print '================================'
        print 'init_battleticket'
        print '================================'
        model_mgr = ModelRequestMgr()
        # メンテナンス確認.
        appconfig = BackendApi.get_appconfig(model_mgr)
        if not appconfig.is_maintenance():
            print u'メンテナンスモードにしてください'
            return

        limit, offset = 1000, 0
        while self.initialize(limit=limit, offset=offset):
            offset += limit

        print '================================'
        print 'all done.'

    # バトルチケット初期化.
    def initialize(self, limit, offset):
        """ バトルチケットの初期化を行なう.
        """
        # バトルチケットの取得.
        tickets = GachaTicket.fetchValues(filters={'mid': self.battleticket_id}, limit=limit, offset=offset, using=settings.DB_DEFAULT)
        if len(tickets) <= 0:
            return None

        def tr():
            model_mgr = ModelRequestMgr()
            for ticket in tickets:
                if ticket.num == 0:
                    continue
                print 'mid: {}, num: {} => 0'.format(ticket.mid, ticket.num)
                ticket.num = 0
                model_mgr.set_save(ticket)
            model_mgr.write_all()
            model_mgr.write_end()
            return model_mgr
        try:
            db_util.run_in_transaction(tr)
        except CabaretError, err:
            print 'error...%s' % err.value
            return
        return True
