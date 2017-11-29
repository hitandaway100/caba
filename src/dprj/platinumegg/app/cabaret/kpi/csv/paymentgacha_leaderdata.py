# -*- coding: utf-8 -*-
import datetime
import settings
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.kpi.csv.base import KpiCSVBase
from platinumegg.app.cabaret.models.Card import CardMaster
from platinumegg.app.cabaret.models.Gacha import GachaMaster
from platinumegg.app.cabaret.models.Player import PlayerConsumePoint
from platinumegg.app.cabaret.kpi.models.gacha import PaymentGachaLastPlayTimeSortedSet,\
    PaymentGachaPlayerLeaderHash

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)

class Manager(KpiCSVBase):
    """課金ユーザのリーダー調査用のデータ.
    """
    def __init__(self, date, output_dir):
        KpiCSVBase.__init__(self, date, output_dir)
    
    def get_data(self):
        
        # 直近2週間で取ってきてみる.
        DAYS = 14
        date_from = self.date - datetime.timedelta(days=DAYS)
        date_to = OSAUtil.get_now()
        
        # ガチャのマスターデータ.
        gachamaster_dict = dict([(master.id, master) for master in GachaMaster.fetchValues(fetch_deleted=True, using=backup_db)])
        # カードのマスターデータ.
        cardmaster_dict = dict([(master.id, master) for master in CardMaster.fetchValues(fetch_deleted=True, using=backup_db)])
        
        # 対象のユーザー.
        uidlist = PaymentGachaLastPlayTimeSortedSet.fetchByDate(date_from, date_to)
        
        result = [
            ['ユーザID', '生涯課金額', 'ガチャ1', 'ガチャを回した時のリーダー1', 'ガチャ2', 'ガチャを回した時のリーダー2', 'ガチャ3', 'ガチャを回した時のリーダー3']
        ]
        
        for uid in uidlist:
            row = [uid]
            
            # 生涯課金額.
            model = PlayerConsumePoint.getByKey(uid, using=backup_db)
            row.append(model.point_total if model else 0)
            
            redisdata = PaymentGachaPlayerLeaderHash.getByUserIDList([uid]).get(uid) or {}
            items = list(redisdata.items())
            items.sort(key=lambda x:x[1]['date'], reverse=True)
            
            for gachaid, data in items:
                # 引いたガチャ.
                gachamaster = gachamaster_dict[gachaid]
                # その時のリーダー.
                cardmaster = cardmaster_dict[data['card']]
                
                row.extend([u'%s(ID:%d)' % (gachamaster.name, gachamaster.id), u'%s(ID:%d)' % (cardmaster.name, cardmaster.id)])
            result.append(row)
        
        return result
