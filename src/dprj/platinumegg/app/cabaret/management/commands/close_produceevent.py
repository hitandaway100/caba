# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from platinumegg.app.cabaret.models.produce_event.ProduceEvent import \
    CurrentProduceEventConfig
from platinumegg.app.cabaret.models.produce_event.ProduceEvent import \
    ProduceEventScore
from platinumegg.app.cabaret.models.Item import Item
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.present import PrizeData
from platinumegg.app.cabaret.util.redisdb import ProduceEventRanking
from platinumegg.lib.opensocial.util import OSAUtil
import settings


class Command(BaseCommand):
    """プロデュースイベント終了処理.
    - ランキング報酬配布
    """
    def handle(self, *args, **options):
        print(u'Execute end process of ProduceEvent.\n')

        print(u'Start preparation...')
        model_mgr = ModelRequestMgr()
        now = OSAUtil.get_now()

        cur_config = BackendApi.get_current_produce_event_config(
            model_mgr, using=settings.DB_READONLY
        )
        mid = cur_config.mid
        eventmaster = BackendApi.get_produce_event_master(
            model_mgr, mid, using=settings.DB_READONLY
        )

        print(u'  Check ProduceEventMaster...')
        if eventmaster is None:
            raise CabaretError(
                u'EventMasterData does not exist.',
                CabaretError.Code.INVALID_MASTERDATA
            )
        print(u'  -> OK')

        print(u'  Check ProduceEvent status...')
        if now < cur_config.endtime:
            raise CabaretError(
                u'ProduceEvent has not ended yet.',
                CabaretError.Code.NOT_REGISTERD
            )
        print(u'  -> OK')

        print(u'  Check maintenance mode or not...')
        appconfig = BackendApi.get_appconfig(model_mgr)
        if not appconfig.is_maintenance():
            raise CabaretError(
                u'Please enable maintenance mode.',
                CabaretError.Code.MAINTENANCE
            )
        print(u'  -> OK')

        print(u'All checked.\n')

        print(u'Update ranking score.')
        self.update_ranking_score(mid)

        print(u'Start send ranking prize.')
        self.send_ranking_prize(
            model_mgr,
            mid,
            ProduceEventRanking,
            eventmaster.rankingprizes,
            eventmaster.rankingprize_text
        )

        print(u'\nStart exchange ProduceEvent only item for existing item.')
        items = Item.fetchValues(
            fields=['uid'], filters={'mid': eventmaster.useitem})
        if not items:
            raise CabaretError(u'No data.', CabaretError.Code.NOT_DATA)

        sorted_items = sorted(items, key=lambda item: item.uid)

        for item in sorted_items:
            num_with_key = BackendApi.get_item_nums(
                model_mgr,
                item.uid,
                [eventmaster.useitem], using=settings.DB_READONLY)
            num = num_with_key.get(eventmaster.useitem, 0)

            print('Exchange. uid: {} , num: {}'.format(item.uid, num))

            db_util.run_in_transaction(
                self.tr_exchange_item, item.uid, eventmaster, num)

#            print('{ansi}Exchange completed. uid: {uid}{reset}'.format(
#                uid=item.uid, ansi='\x1b[0;32;40m', reset='\x1b[0m'))
            print('Exchange completed. uid: {uid}'.format(
                uid=item.uid))
        print '================================'
        print 'Exchange end'     
         
        print '\n================================'
        print 'all done..'
    def update_ranking_score(self, mid):
        MAX = ProduceEventScore.count()
        BATCH_SIZE = 1000

        for i in xrange(MAX/BATCH_SIZE+1):
            scorelist = ProduceEventScore.fetchValues(
                ['uid','point'],
                filters={'mid':mid},
                offset=i*BATCH_SIZE+1,
                limit=(i+1)*BATCH_SIZE
            )
            pipe = ProduceEventRanking.getDB().pipeline()
            for score in scorelist:
                ProduceEventRanking.create(
                    mid, score.uid, score.point).save(pipe
                    )
            pipe.execute()
#        print(u'All updated.\n'.format(
#            ansi='\x1b[0;32;40m', ansi_reset='\x1b[0m'))
        print(u'All updated.')

    def send_ranking_prize(self, model_mgr, mid, ranking_cls, \
                           rankingprizes, textid):
        for rankingprize in rankingprizes:
            prizeidlist = rankingprize['prize']
            rank_min = rankingprize['rank_min']
            rank_max = rankingprize['rank_max']

            prizelist = BackendApi.get_prizelist(
                model_mgr, prizeidlist, using=settings.DB_READONLY
            )
            uidlist = []

            for rank in xrange(rank_min, rank_max+1):
                data = ranking_cls.fetchByRank(mid, rank)
                dic = dict(data)
                uidlist.extend(dic.keys())
                if len(set(uidlist)) != len(uidlist):
                    raise CabaretError(
                        u'Ranking data is invalid.',
                        CabaretError.Code.UNKNOWN
                    )

            print(u'  Send prize between rank {} ~ {}'.format(
                rank_min, rank_max
            ))
            for uid in uidlist:
                print('    Send to uid: {}'.format(uid))
                try:
                    db_util.run_in_transaction(
                        self.tr_send_ranking_prize, uid, prizelist, textid
                    )
                except CabaretError as err:
                    print('Error...{}'.format(err))
#                print(u'    {ansi}Send end.{ansi_reset}'.format(
#                    ansi='\x1b[0;32;40m', ansi_reset='\x1b[0m'))
                print(u'    Send end.')
#            print(u'  {ansi}Send end rank {rank_min} ~ \
#{rank_max}.{ansi_reset}'.format(
#                ansi='\x1b[0;32;40m', ansi_reset='\x1b[0m',
#                rank_min=rank_min, rank_max=rank_max))
            print(u'  Send end rank {rank_min} ~ \
{rank_max}'.format(
                rank_min=rank_min, rank_max=rank_max))
    def tr_send_ranking_prize(self, uid, prizelist, textid):
        model_mgr = ModelRequestMgr()
        config = CurrentProduceEventConfig.getByKeyForUpdate(
            CurrentProduceEventConfig.SINGLE_ID
        )
        BackendApi.tr_add_prize(model_mgr, uid, prizelist, textid)
        model_mgr.write_all()
        model_mgr.write_end()

    def tr_exchange_item(self, uid, eventmaster, num):
        model_mgr = ModelRequestMgr()

        BackendApi.tr_add_item(model_mgr, uid, eventmaster.useitem, -num)

        prizelist = [PrizeData.create(itemid=eventmaster.changeitem, itemnum=num)]
        TEXTID = 252
        BackendApi.tr_add_prize(model_mgr, uid, prizelist, TEXTID)

        model_mgr.write_all()
        model_mgr.write_end()
