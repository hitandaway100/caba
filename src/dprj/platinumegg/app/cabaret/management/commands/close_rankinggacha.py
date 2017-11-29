# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.redisdb import RankingGachaSingleRanking, RankingGachaTotalRanking
import settings
from platinumegg.app.cabaret.models.Gacha import GachaMaster, RankingGachaScore,\
    RankingGachaClose, RankingGachaWholeData, RankingGachaWholePrizeQueue,\
    RankingGachaWholePrizeData
from platinumegg.app.cabaret.models.Player import Player

class Command(BaseCommand):
    """ランキングガチャのランキング報酬を配布.
    """
    def handle(self, *args, **options):
        
        print '================================'
        print 'close_rankinggacha'
        print '================================'
        
        model_mgr = ModelRequestMgr()
        
        now = OSAUtil.get_now()
        
        # メンテナンス確認.
        appconfig = BackendApi.get_appconfig(model_mgr)
        if not appconfig.is_maintenance():
            print u'メンテナンスモードにしてください'
            return
        print 'check maintenance...OK'
        
        print '================================'
        print 'check master'
        group = int(args[0])
        master_list = BackendApi.get_rankinggacha_master_by_group(model_mgr, group, using=settings.DB_READONLY)
        if not master_list:
            print u'ランキングガチャではありません'
            return
        boxidlist = [master.id for master in master_list]
        master_dict = dict([(master.id, master) for master in master_list])
        gachamaster_list = GachaMaster.fetchValues(filters={'boxid__in':boxidlist}, using=settings.DB_READONLY)
        gachamaster_list = [gachamaster.id for gachamaster in gachamaster_list if BackendApi.check_schedule(model_mgr, gachamaster.schedule, using=settings.DB_READONLY, now=now)]
        if gachamaster_list:
            print u'ガチャが開いています.id=%s' % gachamaster_list
            return
        print 'check master...OK'
        
        print '================================'
        print 'update ranking:start'
        # ランキングを更新.
        for master in master_list:
            offset = 0
            limit = 1000
            flag_support_totalranking = master.is_support_totalranking
            
            while True:
                recordlist = RankingGachaScore.fetchValues(filters={'mid':master.id}, limit=limit, offset=offset)
                
                pipe = RankingGachaSingleRanking.getDB().pipeline()
                for record in recordlist:
                    RankingGachaSingleRanking.create(master.id, record.uid, record.single).save(pipe)
                    if flag_support_totalranking:
                        RankingGachaTotalRanking.create(master.id, record.uid, record.total).save(pipe)
                pipe.execute()
                
                if len(recordlist) < limit:
                    break
                offset += limit
        print 'update ranking:end'
        
        print '================================'
        print 'send ranking prizes:start'
        for master in master_list:
            boxid = master.id
            
            close_model = RankingGachaClose.getByKey(boxid)
            if close_model is None:
                close_model = RankingGachaClose.makeInstance(boxid)
                close_model.insert()
            
            print 'start...single'
            close_model = self.__send_prize(model_mgr, master.singleprizes, master.singleprize_text, close_model, 'prize_flag_single', RankingGachaSingleRanking)
            
            if flag_support_totalranking:
                print 'start...total'
                close_model = self.__send_prize(model_mgr, master.totalprizes, master.totalprize_text, close_model, 'prize_flag_total', RankingGachaTotalRanking)
        
        print '================================'
        print 'send whole prizes:start'
        # 勝利したBOX.
        wholedata_list = RankingGachaWholeData.getByKey(boxidlist)
        arr = [(wholedata.id, wholedata.point) for wholedata in wholedata_list]
        arr.sort(key=lambda x:x[1], reverse=True)
        winner = []
        point_max = None
        for boxid, point in arr:
            if point_max is not None and point < point_max:
                break
            elif point < 1:
                break
            winner.append(boxid)
            point_max = point
        print 'winner:%s' % winner
        
        queuelist = RankingGachaWholePrizeQueue.fetchValues(filters={'boxid__in':boxidlist})
        queuelist.sort(key=lambda x:x.id)
        
        boxidlist.sort()
        close_model_boxid = boxidlist[0]
        close_model = RankingGachaClose.getByKey(close_model_boxid)
        
        uid_max = Player.max_value('id')
        for uid in xrange(close_model.prize_flag_whole+1, uid_max+1):
            # 全員について検証.
            data = RankingGachaWholePrizeData.getByKey(uid)
            if data is None:
                # 未プレイ.
                continue
            
            # スコア情報.
            firstpoint_dict = dict([(scoredata.mid, scoredata.firstpoint) for scoredata in RankingGachaScore.getByKey([RankingGachaScore.makeID(uid, boxid) for boxid in boxidlist])])
            
            # 未受け取り分.
            queuelist_not_received = [queue for queue in queuelist if data.queueid < queue.id and firstpoint_dict.get(queue.boxid) and firstpoint_dict[queue.boxid] <= queue.point]
            
            # 勝利判定.
            win_boxidlist = list(set(firstpoint_dict.keys()) & set(winner))
            
            if not (queuelist_not_received or win_boxidlist):
                # 未受け取りの報酬が無い 且つ 敗北.
                continue
            
            try:
                model_mgr, close_model = db_util.run_in_transaction(self.__tr_send_wholeprize, uid, queuelist_not_received, master_dict, win_boxidlist, close_model_boxid)
                model_mgr.write_end()
                print '%d...receive' % uid
            except CabaretError, err:
                if err.code == CabaretError.Code.ALREADY_RECEIVED:
                    # 受取済みのキューを指定していた.
                    model_mgr, close_model = db_util.run_in_transaction(self.__tr_send_wholeprize, uid, [], master_dict, win_boxidlist, close_model_boxid)
                    model_mgr.write_end()
                    print '%d...already' % uid
                else:
                    raise
        
        print '================================'
        print 'all done..'
    
    def __tr_send_wholeprize(self, uid, queuelist, rankingmaster_dict, win_boxidlist, close_model_boxid):
        close_model = RankingGachaClose.getByKeyForUpdate(close_model_boxid)
        if uid <= close_model.prize_flag_whole:
            raise CabaretError(u'整合が取れていないので終了します(総計)')
        
        model_mgr = ModelRequestMgr()
        # 受け取っていない報酬.
        if queuelist:
            BackendApi.tr_rankinggacha_receive_wholeprize(model_mgr, uid, queuelist, rankingmaster_dict)
        
        # 勝利報酬.
        for win_boxid in win_boxidlist:
            master = rankingmaster_dict[win_boxid]
            textid = master.wholewinprize_text
            prizelist = BackendApi.get_prizelist(model_mgr, master.wholewinprizes)
            if prizelist:
                BackendApi.tr_add_prize(model_mgr, uid, prizelist, textid)
        
        close_model.prize_flag_whole = uid
        model_mgr.set_save(close_model)
        
        model_mgr.write_all()
        
        return model_mgr, close_model
    
    def __send_prize(self, model_mgr, rankingprizes, textid, close_model, flag_att, ranking_cls):
        """報酬を送信.
        """
        boxid = close_model.id
        
        # 報酬を渡す.
        for idx, data in enumerate(rankingprizes):
            prize_flag = getattr(close_model, flag_att)
            
            if idx < prize_flag:
                print 'skip...%d' % idx
                continue
            
            prizeidlist = data['prize']
            rank_min = data['rank_min']
            rank_max = data['rank_max']
            
            prizelist = BackendApi.get_prizelist(model_mgr, prizeidlist)
            uidlist = []
            
            for rank in xrange(rank_min, rank_max+1):
                data = ranking_cls.fetchByRank(boxid, rank)
                dic = dict(data)
                uidlist.extend(dic.keys())
                if len(set(uidlist)) != len(uidlist):
                    raise CabaretError(u'ランキング取得がなにかおかしい..%d' % rank)
            def tr():
                model_mgr = ModelRequestMgr()
                close_model = RankingGachaClose.getByKeyForUpdate(boxid)
                prize_flag = getattr(close_model, flag_att)
                
                if prize_flag != idx:
                    raise CabaretError(u'整合が取れていないので終了します')
                
                for uid in uidlist:
                    BackendApi.tr_add_prize(model_mgr, uid, prizelist, textid)
                
                setattr(close_model, flag_att, idx + 1)
                close_model.utime = OSAUtil.get_now()
                model_mgr.set_save(close_model)
                model_mgr.write_all()
                return model_mgr, close_model
            try:
                tmp_model_mgr, wrote_close_model = db_util.run_in_transaction(tr)
            except CabaretError, err:
                print 'error...%s' % err.value
                return
            
            print 'save end...%d' % idx
            
            tmp_model_mgr.write_end()
            print 'cache end...%d' % idx
            
            close_model = wrote_close_model
        return close_model
