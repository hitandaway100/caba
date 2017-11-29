# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from platinumegg.app.cabaret.models.Card import RaidDeck, CardDeleted

class Command(BaseCommand):
    """壊れたデッキを探す.
    """
    def handle(self, *args, **options):
        
        print '================================'
        print 'check_brokendeck'
        print '================================'
        
        offset = 0
        NUM = 1000
        
        while True:
            modellist = RaidDeck.fetchValues(order_by='id', limit=NUM, offset=offset)
            offset += NUM
            if not modellist:
                break
            
            for model in modellist:
                if 0 < CardDeleted.count(filters={'id__in':model.to_array()}):
                    print model.id
        
        print '---------------'
        print 'all done.'
