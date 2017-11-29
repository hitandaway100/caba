# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.datetime_util import DateTimeUtil
from platinumegg.app.cabaret.models.UserLog import UserLogEvolution
from platinumegg.app.cabaret.models.Card import Card
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.card import CardSet
import settings_sub

class Command(BaseCommand):
    """壊れた引き継ぎ接客力を修復.
    """
    def handle(self, *args, **options):
        
        print '================================'
        print 'recov_takeover'
        print '================================'
        
        is_update = 0 < len(args) and args[0] == 'update'
        
        # 修正対象のcardidのリスト.
        if settings_sub.IS_DEV:
            tmp_cards = Card.fetchValues(filters={'mid__gte': 23203, 'mid__lte': 23205})
            TARGET_CARDID_LIST = [card.id for card in tmp_cards]
        else:
            tmp_cards = Card.fetchValues(filters={'mid__gte': 23203, 'mid__lte': 23205})
            TARGET_CARDID_LIST = [card.id for card in tmp_cards]

            # TARGET_CARDID_LIST = (
            #     243554710460995,
            #     259875586181903,
            #     264149078647399,
            #     267898585091933,
            #     289150083275628,
            #     303770151954557,
            #     326108276855142,
            #     2370821955526,
            #     59785944768327,
            #     97268124365984,
            #     164467182686565,
            #     191985038136826,
            #     207399675767609,
            #     207399675767612,
            #     226937481993457,
            #     253566279230399,
            #     298779399950377,
            #     326348795024926,
            #     407317518485754,
            #     425957676551555,
            # )
        # 対象のキャストが本番で公開された時間.
        CTIME_MIN = DateTimeUtil.strToDateTime('201603181400', "%Y%m%d%H%M")
        
        model_mgr = ModelRequestMgr()

        for cardid in TARGET_CARDID_LIST:
            # カードを取得.
            card = Card.getByKey(cardid)
            if card is None:
                print '%s...None' % cardid
                continue
            cardmaster = BackendApi.get_cardmasters([card.mid], model_mgr).get(card.mid)
            
            # このカードのハメ管理履歴を絞り込み.
            log_dict = {}
            for model in UserLogEvolution.fetchValues(filters={'uid':card.uid,'ctime__gte':CTIME_MIN}, order_by='ctime'):
                if cardid == model.data['material']['id']:
                    print '%s...material' % cardid
                    break
                elif cardid != model.data['base']['id']:
                    continue
                log_dict[model.data['base']['mid']] = model
            
            midlist = BackendApi.get_cardmasterid_by_albumhklevel(model_mgr, cardmaster.album)
            masters = dict([(model.hklevel, model) for model in BackendApi.get_cardmasters(midlist, model_mgr).values()])
            
            tmp_basecard = None
            for hklevel in xrange(1, cardmaster.hklevel):
                basemaster = masters[hklevel]
                logdata = log_dict[basemaster.id]
                
                tmp_basecard = CardSet(tmp_basecard.card if tmp_basecard else Card.makeInstance(cardid), basemaster)
                tmp_basecard.card.mid = basemaster.id
                tmp_basecard.card.level = logdata.data['base']['level']
                
                takeover = tmp_basecard.get_evolution_takeover()
                takeover *= 2
                tmp_basecard.card.takeover += takeover
            
            if card.takeover == tmp_basecard.card.takeover:
                print '%s...equal' % cardid
                continue
            
            if is_update:
                def tr(cardid, master, takeover):
                    card = Card.getByKeyForUpdate(cardid)
                    if master.id != card.mid:
                        # これは危険.
                        raise CabaretError()
                    
                    model_mgr = ModelRequestMgr()
                    card.takeover = takeover;
                    model_mgr.set_save(card)
                    
                    def writeEnd():
                        BackendApi.save_cardidset(CardSet(card, master))
                    model_mgr.add_write_end_method(writeEnd)
                    model_mgr.write_all()
                    
                    return model_mgr
                try:
                    db_util.run_in_transaction(tr, tmp_basecard.id, cardmaster, tmp_basecard.card.takeover).write_end()
                except CabaretError:
                    print '%s...danger' % cardid
                    continue
            print '%s...update %s=>%s' % (cardid, card.takeover, tmp_basecard.card.takeover)
        
        print '================================'
        print 'all done..'
