# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.present import PrizeData
from platinumegg.app.cabaret.models.Item import Item
from platinumegg.app.cabaret.models.Item import ItemMaster
import settings

TEXTID = 100


class Command(BaseCommand):
    """At the end of ProduceEvent, exchange ProduceEvent only item for existing item."""
    def handle(self, *args, **options):
        model_mgr = ModelRequestMgr()

        config = BackendApi.get_current_produce_event_config(model_mgr)
        eventmaster = BackendApi.get_produce_event_master(model_mgr, config.mid, using=settings.DB_DEFAULT)
        if not eventmaster:
            raise CabaretError(u'EventMasterData not found. ID: {}'.format(config.mid), CabaretError.Code.INVALID_MASTERDATA)

        self.check_itemmaster(model_mgr, eventmaster.useitem)
        self.check_itemmaster(model_mgr, eventmaster.changeitem)

        items = Item.fetchValues(fields=['uid'], filters={'mid': eventmaster.useitem})
        if not items:
            raise CabaretError(u'No data.', CabaretError.Code.NOT_DATA)

        sorted_items = sorted(items, key=lambda item: item.uid)

        for item in sorted_items:
            num_with_key = BackendApi.get_item_nums(model_mgr, item.uid, [eventmaster.useitem], using=settings.DB_READONLY)
            num = num_with_key.get(eventmaster.useitem, 0)

            print('Target... uid: {uid}, num: {num}'.format(uid=item.uid, num=num))

            db_util.run_in_transaction(self.tr_write, item.uid, eventmaster, num)

            print('{ansi}Exchange completed. uid: {uid}{reset}'.format(uid=item.uid, ansi='\x1b[0;32;40m', reset='\x1b[0m'))

    def tr_write(self, uid, eventmaster, num):
        model_mgr = ModelRequestMgr()

        BackendApi.tr_add_item(model_mgr, uid, eventmaster.useitem, -num)

        prizelist = [PrizeData.create(itemid=eventmaster.changeitem, itemnum=num)]
        BackendApi.tr_add_prize(model_mgr, uid, prizelist, TEXTID)

        model_mgr.write_all()
        model_mgr.write_end()

    def check_itemmaster(self, model_mgr, itemid):
        print(u'Checking ItemMaster... ID: {}'.format(itemid))

        model = model_mgr.get_model(ItemMaster, itemid, using=settings.DB_DEFAULT)
        if model is None:
            raise(u'MasterData not found. ID: {}'.format(itemid), CabaretError.Code.INVALID_MASTERDATA)

        print(u'Check completed. ID: {}'.format(itemid))
