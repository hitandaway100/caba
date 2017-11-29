# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.api import BackendApi
from defines import Defines
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.cabareterror import CabaretError
import settings
from platinumegg.app.cabaret.models.Gacha import GachaTicket

TICKET_TYPE = Defines.GachaConsumeType.GachaTicketType

class Command(BaseCommand):
    """レイドイベントのチケット換金.
    """
    def handle(self, *args, **options):
        print '================================'
        print 'trade sp ticket'
        print '================================'

        model_mgr = ModelRequestMgr()

        # メンテナンス確認.
        appconfig = BackendApi.get_appconfig(model_mgr)
        if not appconfig.is_maintenance():
            print u'メンテナンスモードにしてください'
            return
        print 'check maintenance...OK'

        offset = 0
        limit = 1000

        while self.ticket_trade(offset, limit):
            offset += 1000
            limit += 1000

    def ticket_trade(self, offset, limit):
        delete_tickets = GachaTicket.fetchValues(
            filters={'mid': TICKET_TYPE.FIXEDSR_SP_SSR_20PERCENT},
            limit=limit, offset=offset, using=settings.DB_DEFAULT
        )

        # 対象者が残っていない場合終了.
        if not delete_tickets:
            return False

        try:
            db_util.run_in_transaction(self.tr, delete_tickets)
        except:
            print('error... offset: {}, limit: {}'.format(offset, limit))

        return True

    def tr(self, delete_tickets):
        model_mgr = ModelRequestMgr()
        for i, ticket in enumerate(delete_tickets):
            print('uid: {}, mid: {}, num: {}->{}'.format(
                ticket.uid, ticket.mid, ticket.num, ticket.num-ticket.num))

            # 旧チケットの削除.
            BackendApi.tr_add_additional_gachaticket(
                model_mgr,
                ticket.uid,
                TICKET_TYPE.FIXEDSR_SP_SSR_20PERCENT,
                -ticket.num
            )

            # 新チケットの配布.
            BackendApi.tr_add_additional_gachaticket(
                model_mgr,
                ticket.uid,
                TICKET_TYPE.SP_SSR_20PERCENT_LC_10PERCENT,
                ticket.num
            )
        model_mgr.write_all()
        model_mgr.write_end()
