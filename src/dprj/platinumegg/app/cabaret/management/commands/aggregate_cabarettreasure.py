# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from platinumegg.app.cabaret.models.Player import PlayerTreasure
import settings
from platinumegg.app.cabaret.models.UserLog import UserLogTrade
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.models.Trade import TradeMaster
from platinumegg.lib.opensocial.util import OSAUtil

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)

class Command(BaseCommand):
    """秘宝の集計.
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
        print 'aggregate_cabarettreasure'
        print '================================'
        
        # 出力先.
        path = OSAUtil.get_now().strftime(args[0])
        
        # 書き込むデータをここに溜め込む.
        writer = Command.Writer(path)
        
        # 今のユーザIDの最大値を取得.
        uid_max = PlayerTreasure.max_value('id', 0, using=backup_db)
        
        # 交換できるもの.
        model_mgr = ModelRequestMgr()
        trade_all = dict([(model.id, model) for model in model_mgr.get_mastermodel_all(TradeMaster, fetch_deleted=True, using=backup_db)])
        
        for uid in xrange(1, uid_max+1):
            # 現在の所持数.
            player = PlayerTreasure.getByKey(uid, using=backup_db)
            if player is None:
                continue
            
            cabaretking = player.get_cabaretking_num()
            row = [str(uid), str(cabaretking)]
            
            # ユーザログを集計して消費量を求める.
            userloglist = UserLogTrade.fetchValues(filters={'uid':uid}, using=backup_db)
            consumed = 0
            for userlog in userloglist:
                trademaster = trade_all.get(userlog.mid, None)
                if trademaster:
                    consumed += trademaster.rate_cabaretking
            row.append('%s' % (cabaretking + consumed))
            rowtext = ','.join(row)
            print rowtext
            writer.add(rowtext)
        
        writer.output(overwrite=False)
        
        print '================================'
        print 'all done..'
    
