# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.adminhandler import AdminHandler
import settings_sub
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.lib.platform.api.objects import PaymentData
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from platinumegg.app.cabaret.util.datetime_util import DateTimeUtil
import datetime
from platinumegg.app.cabaret.models.PaymentEntry import GachaPaymentEntry,\
    ShopPaymentEntry
from platinumegg.lib.strutil import StrUtil
import os
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)

class Handler(AdminHandler):
    """課金ログの集計.
    """
    class Writer():
        def __init__(self, path, keep_maxlength=50000):
            self._path = path
            self._size = 0
            self._data = []
            self._keep_maxlength = keep_maxlength
            self.output(overwrite=True)
        
        def add(self, text):
#            print text
            self._data.append(text)
            self._size += len(text)     # 厳密には違うけど..
            if self._keep_maxlength <= self._size:
                self.output(overwrite=False)
                self._data = []
                self._size = 0
        
        def output(self, overwrite=False):
            print 'output start'
            if self._data:
                self._data.append('')
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
            print 'output end'
    
    @classmethod
    def get_timeout_time(cls):
        return 86400
    
    @classmethod
    def get_default_status(cls):
        """デフォルトで返すHttpStatus.
        """
        return 200
    
    def checkUser(self):
        # 認証.
        if settings_sub.IS_LOCAL:
            return
        elif self.request.remote_addr.startswith('10.116.41.'):
            return
        elif self.request.remote_addr in self.appparam.developer_ip:
            return
        self.response.set_status(404)
        raise CabaretError(u'NotFound!!', CabaretError.Code.NOT_AUTH)
    
    def send(self, status, msg=None):
        self.response.set_status(status)
        self.response.send(body=msg)
    
    def process(self):
        
        model_mgr = self.getModelMgr()
        appconfig = BackendApi.get_appconfig(model_mgr, using=settings.DB_READONLY)
        if appconfig.is_maintenance():
            # メンテ中は実行しない.
            self.send(200, 'maintenance')
            return
        
        args = self.getUrlArgs('/aggregate_paymententry/')
        str_target_date = args.get(0)
        if str_target_date:
            target_date = DateTimeUtil.strToDateTime(str_target_date, "%Y%m")
        else:
            # 未指定の場合は前月分.
            last_date = DateTimeUtil.strToDateTime(OSAUtil.get_now().strftime("%Y%m"), "%Y%m") - datetime.timedelta(days=1)
            target_date = DateTimeUtil.strToDateTime(last_date.strftime("%Y%m"), "%Y%m")
        
        def makeWriter(name):
            # 出力先.
            path = os.path.join(settings_sub.KPI_ROOT, target_date.strftime("paymententry/paymententry_"+name+"_%Y%m.csv"))
            
            # 書き込むデータをここに溜め込む.
            writer = Handler.Writer(path)
            writer.add(','.join([u'ペイメントID', u'単価', u'購入個数', u'合計ポイント', u'executedTime']))
            
            return writer
        
        writer_sp = makeWriter("sp")
        writer_pc = makeWriter("pc")
        
        model_cls_list = (
            GachaPaymentEntry,
            ShopPaymentEntry,
        )
        self.__logs = []
        for model_cls in model_cls_list:
            self.work(model_cls, target_date, writer_sp, writer_pc)
            if self.response.isEnd:
                return
        print 'all end'
        writer_sp.output()
        writer_pc.output()
        print 'all output'
        
        self.__logs.insert(0, 'OK')
        print 'log insert'
        
        self.send(200, '\n'.join(self.__logs))
        print 'complete'
    
    def work(self, model_cls, target_date, writer_sp, writer_pc):
        
        s_executed_date = target_date
        e_executed_date = DateTimeUtil.strToDateTime((s_executed_date + datetime.timedelta(days=31)).strftime("%Y%m"), "%Y%m")
        
        # 前後1日を余分に.
        s_date = s_executed_date - datetime.timedelta(days=1)
        e_date = e_executed_date + datetime.timedelta(days=1)
        
        filters = {
            'state' : PaymentData.Status.COMPLETED,
            'ctime__gte' : s_date,
            'ctime__lt' : e_date,
        }
        LIMIT = 500
        offset = 0
        
        while True:
            model_mgr = ModelRequestMgr()
            
            modellist = model_cls.fetchValues(filters=filters, limit=LIMIT, offset=offset, order_by='ctime', using=backup_db)
            for model in modellist:
                
                player = BackendApi.get_player(self, model.uid, [], using=settings.DB_READONLY, model_mgr=model_mgr)
                
                try:
                    record = BackendApi.get_restful_paymentrecord(self, model.id, player.dmmid)
                except:
                    if not settings_sub.IS_DEV:
                        raise
                    else:
                        # クロスプロモで共有した環境のレコード.
                        continue
                
                if record.executeTime is None or not (s_executed_date <= record.executeTime < e_executed_date):
                    # 集計対象の日付ではない.
                    continue
                
                persons = BackendApi.get_dmmplayers(self, [player], using=settings.DB_READONLY, do_execute=False)
                person = persons[player.dmmid]
                if person and getattr(person, 'userType', None) == "staff":
                    # 優待アカウント.
                    self.__logs.append("%s=>staff" % model.id)
                    continue
                
                if str(record.paymentItems[0].itemId).isdigit():
                    writer = writer_sp
                else:
                    writer = writer_pc
                writer.add(','.join([model.id, str(model.price), str(model.inum), str(model.price*model.inum), record.executeTime.strftime("%Y-%m-%d %H:%M:%S")]))
                
                self.__logs.append(model.id)
            
            offset += LIMIT
            
            if len(modellist) < LIMIT:
                break

def main(request):
    return Handler.run(request)
