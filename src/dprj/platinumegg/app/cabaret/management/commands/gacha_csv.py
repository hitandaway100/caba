# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from platinumegg.app.cabaret.models.Gacha import GachaMaster, GachaBoxMaster,\
    GachaPlayData, GachaGroupMaster
from defines import Defines
import settings
from platinumegg.app.cabaret.util.gacha import GachaBox, GachaMasterSet
from platinumegg.app.cabaret.models.Schedule import ScheduleMaster
from platinumegg.app.cabaret.models.Card import CardMaster, CardSortMaster
from platinumegg.lib.strutil import StrUtil

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)

class Command(BaseCommand):
    """期間限定のガチャに入っていたカードのCSV.
    """
    def handle(self, *args, **options):
        
        print '================================'
        print 'copy_img'
        print '================================'
        
        out = args[0]
        
        # ガチャのマスターを取得.
        gachalist = GachaMaster.fetchValues(filters={'consumetype__in':Defines.GachaConsumeType.PAYMENT_TYPES, 'schedule__gt':0}, using=backup_db)
        
        # ガチャのボックスデータを作成.
        read_boxids = []
        
        card_dict = {}
        for gacha in gachalist:
            if gacha.boxid in read_boxids:
                continue
            
            schedule = ScheduleMaster.getByKey(gacha.schedule, using=backup_db)
            name = u'%s(%s-%s)' % (gacha.name, schedule.stime.strftime('%m/%d'), schedule.stime.strftime('%m/%d'))
            
            boxmaster = GachaBoxMaster.getByKey(gacha.boxid, using=backup_db)
            gachamasterset = GachaMasterSet(gacha, boxmaster, schedule)
            
            gachabox = GachaBox(gachamasterset, GachaPlayData.makeInstance(GachaPlayData.makeID(0, gacha.boxid)), blank=True)
            grouplist = GachaGroupMaster.getByKey(gachabox.get_group_id_list(), using=backup_db)
            
            # カードIDとガチャのIDをひもづける.
            for group in grouplist:
                if 1 < len(group.table):
                    continue
                cardid = group.table[0]['id']
                arr = card_dict[cardid] = card_dict.get(cardid) or []
                arr.append(name)
        
        # カードマスターを取得.
        cardmasterlist = CardMaster.getByKey(card_dict.keys(), order_by='id', using=backup_db)
        
        # CSVを作成.
        rows = []
        def makeRow(row):
            arr = []
            for v in row:
                s = u'%s' % v
                s = s.replace('"', '""')
                arr.append(u'"%s"' % s)
            return u','.join(arr)
        
        for cardmaster in cardmasterlist:
            cardsortmaster = CardSortMaster.getByKey(cardmaster.id, using=backup_db)
            
            row = [cardmaster.id, cardmaster.name, Defines.Rarity.NAMES[cardsortmaster.rare], Defines.CharacterType.NAMES[cardsortmaster.ctype]]
            row.extend(card_dict[cardmaster.id])
            str_row = makeRow(row)
            print str_row
            rows.append(str_row)
        csv_data = StrUtil.to_s(u'\n'.join(rows), dest_enc='shift-jis')
        
        f = None
        try:
            f = open(out, "w")
            f.write(csv_data)
            f.close()
        except:
            if f:
                f.close()
                f = None
            raise
        
        print '================================'
        print 'output:%s' % out
        print 'all done..'
