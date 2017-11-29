# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.models.Happening import Happening
from defines import Defines
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.models.raidevent.RaidEvent import RaidEventScore,\
    CurrentRaidEventConfig
from platinumegg.app.cabaret.util.redisdb import RaidEventRanking,\
    RaidEventRankingBeginer
import settings

class Command(BaseCommand):
    """レイドイベントのランキング報酬を配布.
    """
    def handle(self, *args, **options):
        
        print '================================'
        print 'close_raidevent'
        print '================================'
        
        model_mgr = ModelRequestMgr()
        
        now = OSAUtil.get_now()
        
        config = BackendApi.get_current_raideventconfig(model_mgr)
        mid = config.mid
        
        eventmaster = BackendApi.get_raideventmaster(model_mgr, mid)
        if eventmaster is None:
            print u'イベントが設定されていません'
            return
        print 'check eventmaster...OK'
        
        # イベント設定.
        if now < config.endtime:
            print u'イベントがまだ終了していません'
            return
        print 'check event endtime...OK'
        
        # メンテナンス確認.
        appconfig = BackendApi.get_appconfig(model_mgr)
        if not appconfig.is_maintenance():
            print u'メンテナンスモードにしてください'
            return
        print 'check maintenance...OK'
        
        print '================================'
        print 'check raid:start'
        # クリア済みのレイドを全て終了させる.
        filters = {'state__in':[Defines.HappeningState.BOSS, Defines.HappeningState.CLEAR]}
        num = Happening.count(filters)
        print 'happenings %d' % num
        
        offset = 0
        LIMIT = 200
        now = OSAUtil.get_now()
        
        def tr_clear(happeningid):
            model_mgr = ModelRequestMgr()
            happening = Happening.getByKeyForUpdate(happeningid)
            raidboss = BackendApi.get_raid(model_mgr, happeningid)
            BackendApi.tr_happening_end(model_mgr, happening, raidboss)
            model_mgr.write_all()
            return model_mgr
        
        def tr_miss(happeningid):
            model_mgr = ModelRequestMgr()
            BackendApi.tr_happening_missed(model_mgr, happeningid, force=True)
            model_mgr.write_all()
            return model_mgr
        
        while True:
            happeninglist = Happening.fetchValues(['id','state'], filters, limit=LIMIT, offset=offset)
            offset += LIMIT
            
            for happening in happeninglist:
                try:
                    if happening.state == Defines.HappeningState.CLEAR:
                        model_mgr = db_util.run_in_transaction(tr_clear, happening.id)
                    else:
                        model_mgr = db_util.run_in_transaction(tr_miss, happening.id)
                    model_mgr.write_end()
                except CabaretError, err:
                    if err.code == CabaretError.Code.ALREADY_RECEIVED:
                        pass
                    else:
                        raise
                print 'update %d end' % happening.id
            
            if len(happeninglist) < LIMIT:
                break
        
        
        print 'check raid:end'
        
        print '================================'
        print 'update ranking:start'
        # ランキングを更新.
        offset = 0
        limit = 1000
        while True:
            recordlist = RaidEventScore.fetchValues(['uid','point_total'], filters={'mid':mid}, limit=limit, offset=offset)
            
            pipe = RaidEventRanking.getDB().pipeline()
            for record in recordlist:
                RaidEventRanking.create(mid, record.uid, record.point_total).save(pipe)
                if BackendApi.check_raidevent_beginer(ModelRequestMgr(), record.uid, eventmaster, config, now, using=settings.DB_DEFAULT):
                    # 初心者.
                    RaidEventRankingBeginer.create(mid, record.uid, record.point_total).save(pipe)
            pipe.execute()
            
            if len(recordlist) < limit:
                break
            offset += limit
        print 'update ranking:end'
        
        def sendRankingPrize(ranking_cls, rankingprizes, textid, att_prize_flag):
            # 報酬を渡す.
            for idx, data in enumerate(rankingprizes):
                if idx < getattr(config, att_prize_flag):
                    print 'skip...%d' % idx
                    continue
                
                prizeidlist = data['prize']
                rank_min = data['rank_min']
                rank_max = data['rank_max']
                
                prizelist = BackendApi.get_prizelist(model_mgr, prizeidlist)
                uidlist = []
                
                for rank in xrange(rank_min, rank_max+1):
                    data = ranking_cls.fetchByRank(mid, rank)
                    dic = dict(data)
                    uidlist.extend(dic.keys())
                    if len(set(uidlist)) != len(uidlist):
                        raise CabaretError(u'ランキング取得がなにかおかしい..%d' % rank)
                def tr():
                    model_mgr = ModelRequestMgr()
                    config = CurrentRaidEventConfig.getByKeyForUpdate(CurrentRaidEventConfig.SINGLE_ID)
                    if getattr(config, att_prize_flag) != idx:
                        raise CabaretError(u'整合が取れていないので終了します')
                    for uid in uidlist:
                        BackendApi.tr_add_prize(model_mgr, uid, prizelist, textid)
                    setattr(config, att_prize_flag, idx + 1)
                    model_mgr.set_save(config)
                    model_mgr.write_all()
                    return model_mgr, config
                try:
                    tmp_model_mgr, wrote_config = db_util.run_in_transaction(tr)
                except CabaretError, err:
                    print 'error...%s' % err.value
                    return
                
                print 'save end...%d' % idx
                
                tmp_model_mgr.write_end()
                print 'cache end...%d' % idx
                
                setattr(config, att_prize_flag, getattr(wrote_config, att_prize_flag))
        
        print '================================'
        print 'send prizes:start'
        sendRankingPrize(RaidEventRanking, eventmaster.rankingprizes, eventmaster.rankingprize_text, 'prize_flag')
        
        print '================================'
        print 'send beginerprizes:start'
        sendRankingPrize(RaidEventRankingBeginer, eventmaster.beginer_rankingprizes, eventmaster.beginer_rankingprize_text, 'beginer_prize_flag')
        
        print '================================'
        print 'all done..'
