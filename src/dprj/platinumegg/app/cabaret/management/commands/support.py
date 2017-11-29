# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
import settings
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.datetime_util import DateTimeUtil
from platinumegg.app.cabaret.models.Happening import Raid, RaidMaster
from platinumegg.app.cabaret.models.raidevent.RaidEvent import RaidEventRaidMaster
from platinumegg.app.cabaret.util.happening import RaidBoss

class Command(BaseCommand):
    """ユーザサポート用に何かを探したりしたい.
    """
    class Writer():
        def __init__(self, path, keep_maxlength=50000):
            self._path = path
            self._size = 0
            self._data = []
            self._keep_maxlength = keep_maxlength
            self.output(overwrite=True)
        
        def add(self, text):
            self._data.append(text)
            self._size += len(text)     # 厳密には違うけど..
            if self._keep_maxlength <= self._size:
                self.output(overwrite=False)
                self._data = []
                self._size = 0
        
        def output(self, overwrite=False):
            if self._data:
                self._data.append('\n')
            data_str = '\n'.join(self._data)
            if overwrite:
                mode = 'w'
            else:
                mode = 'a'
            f = None
            try:
                f = open(self._path, mode)
                f.write(data_str)
                f.close()
            except:
                if f:
                    f.close()
                raise
    
    def handle(self, *args, **options):
        
        print '================================'
        print 'support'
        print '================================'
        
        # 出力先.
        path = OSAUtil.get_now().strftime(args[0])
        
        # 書き込むデータをここに溜め込む.
        writer = Command.Writer(path)
        
        # レイドマスター.
        model_mgr = ModelRequestMgr()
        raid_all = dict([(master.id, master) for master in model_mgr.get_mastermodel_all(RaidMaster, using=settings.DB_READONLY)])
        eventraid_all = dict([(master.mid, master) for master in model_mgr.get_mastermodel_all(RaidEventRaidMaster, using=settings.DB_READONLY)])
        
        # 対象のユーザ.
        UIDLIST = [16268, 29339]
        UIDSET = set(UIDLIST)
        
        UNKNOWNS = [
            56272661512882,
            56272661512893,
            87759066759449,
            99127845191766,
            128943508160593,
            136047384068178,
            137099651055617,
            137550622621716,
            143374598275073,
            149615185756161,
            157689724272723,
            165957536317441,
            172352742621192,
            183549722361857,
            193870528774147,
        ]
        
        # 対象の時間.
        filters = {
            'ctime__gte' : DateTimeUtil.strToDateTime("2014-01-07 15:00:00", "%Y-%m-%d %H:%M:%S"),
            'ctime__lt' : DateTimeUtil.strToDateTime("2014-01-13 19:00:00", "%Y-%m-%d %H:%M:%S"),
            'hp' : 0,
        }
        LIMIT = 1000
        
        offset = 0
        
        timebonus_time_min = DateTimeUtil.strToDateTime("2014-01-13 17:00:00", "%Y-%m-%d %H:%M:%S")
        timebonus_time_max = DateTimeUtil.strToDateTime("2014-01-13 19:00:00", "%Y-%m-%d %H:%M:%S")
        
        # 対象のハプニング.
        while True:
            raidlist = Raid.fetchValues(filters=filters, order_by='id', limit=LIMIT, offset=offset)
            
            for raid in raidlist:
                raidboss = RaidBoss(raid, raid_all[raid.mid], eventraid_all.get(raid.mid))
                if raid.id in UNKNOWNS:
                    print raid.id
                
                uidset = set(raidboss.getDamageRecordUserIdList())
                targetlist = list(UIDSET & uidset)
                if not targetlist:
                    continue
                
                helppoints = raidboss.getHelpEventPoints()
                for uid in targetlist:
                    owner = 0
                    mvp = 0
                    helppoint = 0
                    
                    if uid == raidboss.raid.oid:
                        # 発見者報酬.
                        owner = raidboss.get_owner_eventpoint()
                    else:
                        # 協力者報酬.
                        helppoint = helppoints.get(uid, 0)
                    
                    # MVP報酬.
                    mvpuidlist = raidboss.getMVPList()
                    for mvpuid in mvpuidlist:
                        if uid == mvpuid:
                            mvp += raidboss.get_mvp_eventpoint()
                    if not (owner or mvp or helppoint):
                        print raidboss.id
                    else:
                        text = '%s,%s,%s,%s,%s' % (uid, owner, mvp, helppoint, raid.ctime.strftime("%Y-%m-%d %H:%M"))
                        writer.add(text)
#                        print text
                
            if len(raidlist) < LIMIT:
                break
            offset += LIMIT
        
        writer.output(overwrite=False)
        
        print '================================'
        print 'all done..'
    
