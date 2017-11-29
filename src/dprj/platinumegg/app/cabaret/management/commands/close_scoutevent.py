# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.models.ScoutEvent import ScoutEventScore,\
    CurrentScoutEventConfig, ScoutEventTanzakuCastData,\
    ScoutEventCastPerformanceResult
from platinumegg.app.cabaret.util.redisdb import ScoutEventRanking,\
    ScoutEventRankingBeginer
import settings

class Command(BaseCommand):
    """スカウトイベントのランキング報酬を配布.
    """
    def handle(self, *args, **options):
        
        print '================================'
        print 'close_scoutevent'
        print '================================'
        
        model_mgr = ModelRequestMgr()
        
        now = OSAUtil.get_now()
        
        config = BackendApi.get_current_scouteventconfig(model_mgr)
        mid = config.mid
        
        eventmaster = BackendApi.get_scouteventmaster(model_mgr, mid)
        if eventmaster is None:
            print u'スカウトが設定されていません'
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
        print 'update ranking:start'
        # ランキングを更新.
        offset = 0
        limit = 1000
        while True:
            recordlist = ScoutEventScore.fetchValues(['uid','point_total'], filters={'mid':mid}, limit=limit, offset=offset)
            
            pipe = ScoutEventRanking.getDB().pipeline()
            for record in recordlist:
                ScoutEventRanking.create(mid, record.uid, record.point_total).save(pipe)
                if BackendApi.check_scoutevent_beginer(model_mgr, record.uid, eventmaster, config, now, using=settings.DB_READONLY):
                    ScoutEventRankingBeginer.create(mid, record.uid, record.point_total).save(pipe)
            pipe.execute()
            
            if len(recordlist) < limit:
                break
            offset += limit
        print 'update ranking:end'
        
        # 報酬を渡す.
        def sendRankingPrize(ranking_cls, rankingprizes, textid, att_prize_flag):
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
                    config = CurrentScoutEventConfig.getByKeyForUpdate(CurrentScoutEventConfig.SINGLE_ID)
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
        sendRankingPrize(ScoutEventRanking, eventmaster.rankingprizes, eventmaster.rankingprize_text, 'prize_flag')
        
        print '================================'
        print 'send beginerprizes:start'
        sendRankingPrize(ScoutEventRankingBeginer, eventmaster.beginer_rankingprizes, eventmaster.beginer_rankingprize_text, 'beginer_prize_flag')
        
        tanzakumaster_list = BackendApi.get_scoutevent_tanzakumaster_by_eventid(model_mgr, eventmaster.id)
        if tanzakumaster_list:
            tanzakumaster_dict = dict([(tanzakumaster.number, tanzakumaster) for tanzakumaster in tanzakumaster_list])
            
            print '================================'
            print 'aggregate tip:start'
            # チップ投入の集計.
            query = ScoutEventTanzakuCastData.sql("WHERE `mid`=:1", eventmaster.id)
            fields = ['SUM(`tip_{}`)'.format(tanzakumaster.number) for tanzakumaster in tanzakumaster_list]
            record = query.get(','.join(fields))
            print record
            
            print 'save tip result'
            def write():
                def tr():
                    model_mgr = ModelRequestMgr()
                    performance_result = ScoutEventCastPerformanceResult.makeInstance(eventmaster.id)
                    for idx,tanzakumaster in enumerate(tanzakumaster_list):
                        tip = record[idx]
                        setattr(performance_result, 'tip_{}'.format(tanzakumaster.number), tip)
                    model_mgr.set_save(performance_result)
                    model_mgr.write_all()
                    return model_mgr, performance_result
                model_mgr, performance_result = db_util.run_in_transaction(tr)
                model_mgr.write_end()
                return performance_result
            performance_result = write()
            
            print '================================'
            print 'send tanzaku-tip prizes:start'
            # 勝利したキャスト.
            winner = performance_result.get_winner()
            print 'winner={}'.format(winner)
            
            if winner:
                # 配布する報酬.
                prize_dict = {}
                for number in winner:
                    tanzakumaster = tanzakumaster_dict[number]
                    prizelist = BackendApi.get_prizelist(model_mgr, tanzakumaster.prizes, settings.DB_READONLY)
                    if prizelist:
                        prize_dict[number] = prizelist
                winner = prize_dict.keys()
                
                LIMIT = 1000
                # 勝利したキャストに規定数以上のチップを投入していたユーザー.
                fields = ['`uid`']+['`tip_{}`'.format(number) for number in winner]
                tip_filters = ['`tip_{}`>={}'.format(number, max(1, tanzakumaster_dict[number].tip_quota)) for number in winner]
                
                while True:
                    query = ScoutEventTanzakuCastData.sql("WHERE `mid`=:1 AND `uid`>:2 AND ({}) ORDER BY `id` ASC".format(' OR '.join(tip_filters)), eventmaster.id, config.tip_prize_flag)
                    records = query.fetch(','.join(fields), LIMIT)
                    if not records:
                        break
                    
                    def tr(tip_prize_flag):
                        model_mgr = ModelRequestMgr()
                        config = CurrentScoutEventConfig.getByKeyForUpdate(CurrentScoutEventConfig.SINGLE_ID)
                        if config.tip_prize_flag != tip_prize_flag:
                            raise CabaretError(u'整合が取れていないので終了します')
                        
                        uid_max = 0
                        for data in records:
                            uid = data[0]
                            # 報酬付与.
                            for idx, number in enumerate(winner):
                                # 短冊のマスター.
                                tanzakumaster = tanzakumaster_dict[number]
                                # 規定チップを満たしているかを確認.
                                if max(1, tanzakumaster.tip_quota) <= data[idx+1]:
                                    BackendApi.tr_add_prize(model_mgr, uid, prize_dict[number], tanzakumaster.prize_text)
                            uid_max = max(uid_max, uid)
                        
                        config.tip_prize_flag = uid_max
                        model_mgr.set_save(config)
                        model_mgr.write_all()
                        return model_mgr, config
                    try:
                        tmp_model_mgr, wrote_config = db_util.run_in_transaction(tr, config.tip_prize_flag)
                    except CabaretError, err:
                        print 'error...{}'.format(err.value)
                        return
                    
                    print 'save end...{}'.format(wrote_config.tip_prize_flag)
                    
                    tmp_model_mgr.write_end()
                    print 'cache end...{}'.format(wrote_config.tip_prize_flag)
                    
                    config = wrote_config
            else:
                print 'winner...None'
            
        else:
            print 'tanzaku...not include'
        
        print '================================'
        print 'all done..'

