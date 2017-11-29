# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
import settings
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.models.raidevent.RaidEvent import RaidEventScore
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from defines import Defines
from collections import Counter
from platinumegg.app.cabaret.models.Card import CardMaster
from django.db import connections

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)


class Command(BaseCommand):
    """秘宝の集計.
    """
    def handle(self, *args, **options):
        uid_list = self.get_userid_raid_ranking(100)
        self.set_status(uid_list)

    def get_userid_raid_ranking(self, count):
        model_mgr = ModelRequestMgr()
        scores = RaidEventScore.fetchValues(order_by='-point_total', limit=count, using=backup_db)
        return [score.uid for score in scores]

    def set_status(self, uid_list):
        TIARA = Defines.MasterData.TIARA_ID
        RING_DIAMOND = 41003
        RING_PLATINUM = 41004
        SSR_COST_MIN, SSR_COST_MAX = self.get_cost(Defines.Rarity.SPECIALSUPERRARE)
        SR_COST_MIN, SR_COST_MAX = self.get_cost(Defines.Rarity.SUPERRARE)
        HKLEVEL_MIN, HKLEVEL_MAX = self.get_hklevel()

        column = ['ranking', 'user_id']
        cnt_column = ['5_total', '4_total']
        cnt_column.extend(self.gen_column(rare=Defines.Rarity.SPECIALSUPERRARE, type='cost', max=SSR_COST_MAX, min=SSR_COST_MIN))
        cnt_column.extend(self.gen_column(rare=Defines.Rarity.SUPERRARE, type='cost', max=SR_COST_MAX, min=SR_COST_MIN))
        cnt_column.extend(self.gen_column(rare=Defines.Rarity.SPECIALSUPERRARE, type='hklevel', max=HKLEVEL_MAX, min=HKLEVEL_MIN))
        cnt_column.extend(self.gen_column(rare=Defines.Rarity.SUPERRARE, type='hklevel', max=HKLEVEL_MAX, min=HKLEVEL_MIN))
        cnt_column.extend(['ring_diamond', 'ring_platinum', 'tiara'])
        column.extend(cnt_column)

        statuses = [column]

        for i, uid in enumerate(uid_list, 1):
            card_list = BackendApi.get_card_list(uid)
            card_cnt = Counter()
            for card in card_list:
                if self.is_item(card.master.id):
                    card_cnt['{rare}_total'.format(rare=card.master.rare)] += 1
                    card_cnt['{rare}_cost_{value}'.format(rare=card.master.rare, value=card.master.cost)] += 1
                    card_cnt['{rare}_hklevel_{value}'.format(rare=card.master.rare, value=card.master.hklevel)] += 1
                else:
                    if card.master.id == RING_DIAMOND:
                        card_cnt['ring_diamond'] += 1
                    elif card.master.id == RING_PLATINUM:
                        card_cnt['ring_platinum'] += 1
                    elif card.master.id == TIARA:
                        card_cnt['tiara'] += 1
            status = [i, uid]
            status.extend([card_cnt[c] for c in cnt_column])
            statuses.append(status)
        self.output_list(statuses)

    def gen_list_by_counter(self, cnt, max, min):
        return [cnt[i] for i in xrange(max, min-1, -1)]

    def output_list(self, statuses):
        for s in statuses:
            print ', '.join(map(str, s))

    def is_item(self, card_id):
        return card_id < 40000

    def get_cost(self, rare):
        sql = "select min(c.cost), max(c.cost) from cabaret_cardmaster c inner join cabaret_cardsortmaster s on c.id = s.id where s.rare = '{}' and c.id < 40000;".format(rare)
        return self.get_data(sql)

    def get_hklevel(self):
        sql = "select min(hklevel), max(hklevel) from cabaret_cardsortmaster where id < 40000;"
        return self.get_data(sql)

    def get_data(self, sql):
        CardMaster.sql('', using=backup_db)
        cursor = connections[backup_db].cursor()
        cursor.execute(sql)
        return cursor.fetchall()[0]

    def gen_column(self, rare, type, max, min):
        return ['{rare}_{type}_{value}'.format(rare=rare, type=type, value=i) for i in range(max, min-1, -1)]
