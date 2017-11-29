# -*- coding: utf-8 -*-
import datetime
import settings
from defines import Defines
from platinumegg.app.cabaret.kpi.csv.base import KpiCSVBase
from platinumegg.app.cabaret.models.Card import CardMaster
from platinumegg.app.cabaret.models.Player import PlayerConsumePoint
from platinumegg.app.cabaret.util.datetime_util import DateTimeUtil
from platinumegg.app.cabaret.kpi.models.login import WeeklyLoginSet
from platinumegg.app.cabaret.kpi.models.card import RingGetNumHash
from platinumegg.app.cabaret.kpi.models.payment import DailyPaymentPointSet

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)

class Manager(KpiCSVBase):
    """指輪ユーザデータ.
    """
    def __init__(self, date, output_dir):
        KpiCSVBase.__init__(self, date, output_dir)
    
    def get_data(self):
        
        result = []
        
        # 指輪のマスターデータ.
        master_dict = dict([(master.id, master.name) for master in CardMaster.fetchValues(filters={'ckind' : Defines.CardKind.EVOLUTION}, using=backup_db)])
        if not master_dict:
            return None
        midlist = master_dict.keys()
        waylist = Defines.CardGetWayType.NAMES.keys()
        
        titles = [u'ユーザID']
        for mid in midlist:
            for way in waylist:
                result.append(u'%s(%s)' % (master_dict[mid].name, Defines.CardGetWayType.NAMES[way]))
        titles.extend([u'直近一ヶ月の課金額',u'生涯課金額'])
        result.append(titles)
        
        # 7日前.
        s_time = DateTimeUtil.toBaseTime(self.date - datetime.timedelta(days=7), 0)
        e_time = self.date
        
        # 過去1週間以内にログインしたユーザー.
        str_uidlist = WeeklyLoginSet.getUserIdListByRange(s_time, e_time)
        
        redisdb = RingGetNumHash.getDB()
        keys = [RingGetNumHash.makeKey(self.date, mid) for mid in midlist]
        
        union_key = DailyPaymentPointSet.makeUnionSortSet(s_time, e_time)
        
        for str_uid in str_uidlist:
            row = []
            
            uid = int(str_uid)
            row.append(uid)
            
            # 各カードの枚数.
            members = [RingGetNumHash.makeMember(uid, way) for way in waylist]
            for key in keys:
                values = redisdb.hmget(key, members)
                for v in values:
                    v = int(str(v)) if str(v).isdigit() else 0
                    row.append(v)
            
            # 直近1ヶ月の課金額.
            point = redisdb.zscore(union_key, uid) or 0
            row.append(point)
            
            # 生涯課金額.
            model = PlayerConsumePoint.getByKey(uid, using=backup_db)
            row.append(model.point_total if model else 0)
            
            result.append(row)
        
        # 後片付け.
        redisdb.delete(union_key)
        
        return result
