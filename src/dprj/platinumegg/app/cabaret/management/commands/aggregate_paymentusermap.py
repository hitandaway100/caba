# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
import settings
import datetime
from platinumegg.app.cabaret.util.datetime_util import DateTimeUtil
import os
from platinumegg.app.cabaret.models.PaymentEntry import ShopPaymentEntry,\
    GachaPaymentEntry
from platinumegg.lib.platform.api.objects import PaymentData
from platinumegg.lib import timezone
from platinumegg.lib.strutil import StrUtil

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)

class Command(BaseCommand):
    """ユーザごとの課金額マップ.
    ユーザが増えるとメモリが足りなくなるかも.
    """
    class Writer():
        def __init__(self, path, keep_maxlength=50000):
            self._path = path
            self._size = 0
            self._data = []
            self._keep_maxlength = keep_maxlength
            self.output(overwrite=True)
        
        def add(self, text):
            print text
            self._data.append(text)
            self._size += len(text)     # 厳密には違うけど..
            if self._keep_maxlength <= self._size:
                self.output(overwrite=False)
                self._data = []
                self._size = 0
        
        def output(self, overwrite=False):
            if self._data:
                self._data.append('\n')
            data_str = StrUtil.to_s('\n'.join(self._data), 'shift-jis')
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
        print 'aggregate_paymentusermap'
        print '================================'
        
        # 対象の日付(月).
        str_date = args[0]
        target_date = DateTimeUtil.strToDateTime(str_date, "%Y%m")
        print target_date
        
        # 出力先.
        output_dir = args[1]
        path = os.path.join(output_dir, target_date.strftime("paymentusermap_%Y%m.csv"))
        
        # 書き込むデータをここに溜め込む.
        writer = Command.Writer(path)
        writer.add(','.join([u'ユーザID', u'消費ポイント']))
        
        dest_map = {}
        self.aggregate(GachaPaymentEntry, target_date, dest_map)
        self.aggregate(ShopPaymentEntry, target_date, dest_map)
        
        for data in dest_map.items():
            writer.add(u'%s,%s' % data)
        
        writer.output(overwrite=False)
        
        print '================================'
        print 'all done..'
    
    def aggregate(self, model_cls, target_date, dest_map):
        
        s_date = target_date
        tmp = target_date + datetime.timedelta(days=32)
        
        e_date = datetime.datetime(tmp.year, tmp.month, 1)
        if e_date.tzinfo is None:
            e_date = e_date.replace(tzinfo=timezone.TZ_DEFAULT)
        
        filters = {
            'state' : PaymentData.Status.COMPLETED,
            'ctime__gte' : s_date,
            'ctime__lt' : e_date,
        }
        
        LIMIT = 500
        offset = 0
        
        while True:
            modellist = model_cls.fetchValues(filters=filters, limit=LIMIT, offset=offset, order_by='ctime', using=backup_db)
            for model in modellist:
                v = model.price*model.inum
                dest_map[model.uid] = dest_map.get(model.uid, 0) + v
            
            offset += LIMIT
            
            if len(modellist) < LIMIT:
                break
    
