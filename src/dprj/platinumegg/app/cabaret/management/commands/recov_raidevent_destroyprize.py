# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.present import PrizeData
from platinumegg.app.cabaret.models.raidevent.RaidEvent import RaidEventScore,\
    RaidEventFlags, RaidEventMaster
from platinumegg.app.cabaret.util.api import BackendApi

class Command(BaseCommand):
    """壊れたレイドイベント討伐報酬の修復.
    """
    def handle(self, *args, **options):
        
        print '================================'
        print 'recov_raidevent_destroyprize'
        print '================================'
        
        TEST_MODE = True
        
        LIMIT = 500
        
        # 対象のイベント.
        mid = 7
        master = RaidEventMaster.getByKey(mid)
        textid = master.destroyprize_text
        
        # 対象の討伐回数.
        destroy = 200
        
        # 配付する報酬.
        prize = PrizeData.create(cardid=13100, cardnum=1)
        
        offset = 0
        while True:
            # 撃破済みのユーザーを取得.
            scorelist = RaidEventScore.fetchValues(filters={'mid':mid, 'destroy__gte':destroy}, order_by='id', limit=LIMIT, offset=offset)
            if not scorelist:
                break
            
            offset += LIMIT
            
            idlist = [RaidEventFlags.makeID(score.uid, mid) for score in scorelist]
            flags = RaidEventFlags.getByKey(idlist)
            for flag in flags:
                # 受け取りフラグを確認.
                if not destroy in flag.destroyprize_flags:
                    # 未受け取り.
                    print '%s...no' % flag.uid
                    continue
                
                # 配布.
                if not TEST_MODE:
                    def tr(uid, mid, prize, textid):
                        model_mgr = ModelRequestMgr()
                        BackendApi.tr_add_prize(model_mgr, uid, [prize], textid)
                        model_mgr.write_all()
                        return model_mgr
                    db_util.run_in_transaction(tr, flag.uid, mid, prize, textid).write_end()
                print '%s...send' % flag.uid
        
        print '================================'
        print 'all done..'
