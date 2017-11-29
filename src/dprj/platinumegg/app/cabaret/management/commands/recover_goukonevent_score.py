# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
import settings
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.models.battleevent.BattleEvent import BattleEventRank,\
    BattleEventScore, BattleEventScorePerRank
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.models.Player import PlayerExp

class Command(BaseCommand):
    """バトルイベントスコアの修正.
    """
    
    def handle(self, *args, **options):
        
        print '================================'
        print 'recover_goukonevent_score'
        print '================================'
        is_write = (args[0] if args else None) in ('1', 1)
        
        model_mgr = ModelRequestMgr()
        config = BackendApi.get_current_battleeventconfig(model_mgr, using=settings.DB_READONLY)
        mid = config.mid
        eventmaster = BackendApi.get_battleevent_master(model_mgr, mid, using=settings.DB_READONLY)
        eventrankmaster_list = BackendApi.get_battleevent_rankmaster_by_eventid(model_mgr, mid, using=settings.DB_READONLY)
        eventrankmaster_dict = dict([(eventrankmaster.rank, eventrankmaster) for eventrankmaster in eventrankmaster_list])
        
        uid = PlayerExp.max_value('id')
        LIMIT = 500
        while 0 < uid:
            filters = {'mid':eventmaster.id, 'uid__lte':uid}
            
            scorerecord_list = BattleEventScore.fetchValues(filters=filters, order_by='-uid', limit=LIMIT, offset=0, using=settings.DB_READONLY)
            rankrecord_list = BattleEventRank.getByKey([BattleEventRank.makeID(scorerecord.uid, eventmaster.id) for scorerecord in scorerecord_list], using=settings.DB_READONLY)
            rankrecord_dict = dict([(rankrecord.uid, rankrecord) for rankrecord in rankrecord_list])
            
            for scorerecord in scorerecord_list:
                uid = min(uid, scorerecord.uid)
                
                if scorerecord.point_total < 1:
                    print '%s...zero' % scorerecord.uid
                    continue
                
                rankrecord = rankrecord_dict.get(scorerecord.uid)
                if rankrecord is None:
                    print '%s...rank None' % scorerecord.uid
                    continue
                
                eventrankmaster = eventrankmaster_dict.get(rankrecord.rank)
                if eventrankmaster is None:
                    print '%s...rank Unknown' % scorerecord.uid
                    continue
                
                p_key = BattleEventScorePerRank.makeID(scorerecord.uid, BattleEventScorePerRank.makeMid(mid, eventrankmaster.rank))
                if BackendApi.get_model(model_mgr, BattleEventScorePerRank, p_key, using=settings.DB_DEFAULT):
                    print '%s...Already' % scorerecord.uid
                    continue
                
                if is_write:
                    try:
                        db_util.run_in_transaction(Command.tr_write, eventmaster, eventrankmaster, rankrecord).write_end()
                    except:
                        print '%s...ERROR' % scorerecord.uid
                        continue
                print '%s...SUCCESS' % scorerecord.uid
            uid -= 1
    
    @staticmethod
    def tr_write(eventmaster, eventrankmaster, rankrecord):
        """書き込み.
        """
        model_mgr = ModelRequestMgr()
        
        uid = rankrecord.uid
        eventid = eventmaster.id
        p_key = BattleEventScore.makeID(uid, eventid)
        scorerecord = BattleEventScore.getByKeyForUpdate(p_key)
        
        # ランク別の獲得ポイント.
        p_key = BattleEventScorePerRank.makeID(uid, BattleEventScorePerRank.makeMid(eventid, eventrankmaster.rank))
        model = BackendApi.get_model(model_mgr, BattleEventScorePerRank, p_key, using=settings.DB_DEFAULT)
        if model is None:
            model = BattleEventScorePerRank.makeInstance(p_key)
            model.insert()
        else:
            raise CabaretError(u'Already')
        point_pre = model.point
        model.point = max(scorerecord.point_total, model.point)
        model_mgr.set_save(model)
        
        # ポイント達成報酬.
        point_min = point_pre+1
        point_max = model.point
        table = eventrankmaster.get_battlepointprizes(point_min, point_max)
        prizelist = None
        if table:
            keys = table.keys()
            keys.sort()
            prizeidlist = []
            for key in keys:
                prizeidlist.extend(table[key])
            prizelist = BackendApi.get_prizelist(model_mgr, prizeidlist)
            BackendApi.tr_add_prize(model_mgr, uid, prizelist, eventrankmaster.battlepointprize_text)
        
        model_mgr.write_all()
        
        return model_mgr
