# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from platinumegg.app.cabaret.models.Player import Player
import settings
from platinumegg.app.cabaret.models.Item import Item
from platinumegg.app.cabaret.kpi.operator import KpiOperator

class Command(BaseCommand):
    """KPI用のデータを再集計.
    """
    def handle(self, *args, **options):
        
        print '================================'
        print 'reload_kpi'
        print '================================'
        
        uid_max = Player.max_value('id', using=settings.DB_READONLY)
        
        for uid in xrange(1, uid_max+1):
            itemlist = Item.fetchByOwner(uid, using=settings.DB_READONLY)
            if not itemlist:
                continue
            
            ope = KpiOperator()
            for item in itemlist:
                ope.set_save_itemnum(item.uid, item.mid, item.rnum, item.vnum)
            ope.save()
            
            print uid
        
        print '================================'
        print 'all done...'

