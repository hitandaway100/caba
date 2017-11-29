# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.adminhandler import AdminHandler
import settings_sub
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.lib.platform.api.objects import PaymentLogRequestData, PaymentData
from platinumegg.lib.platform.api.request import ApiNames
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from platinumegg.app.cabaret.util.datetime_util import DateTimeUtil
import datetime
from platinumegg.app.cabaret.models.PaymentEntry import GachaPaymentEntry,\
    ShopPaymentEntry
import urllib2
from platinumegg.lib.apperror import AppError
from platinumegg.lib.dbg import DbgLogger
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr


class Handler(AdminHandler):
    """PaymentLogAPI実行ページ.
    実行するのは集計対象日の翌日0:30以降でないといけないらしいけど0:45以降に実行するようにした方がいいかも.
    集計対象の課金レコードは対象日の前日22:00から対象日の翌日0:45まででexecutedTimeが対象日のもののみ.
    """
    
    TARGET_DATE_FORMAT = "%Y%m%d"
    
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
        elif self.request.remote_addr == '211.9.52.235':
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
            # メンテ中は送信しない.
            self.send(200, 'maintenance')
            return
        
        args = self.getUrlArgs('/paymentlog_post/')
        str_target_date = args.get(0)
        if str_target_date:
            target_date = DateTimeUtil.strToDateTime(str_target_date, Handler.TARGET_DATE_FORMAT)
        else:
            # 未指定の場合は前日分.
            target_date = DateTimeUtil.toBaseTime(OSAUtil.get_now() - datetime.timedelta(days=1), 0)
        
        model_cls_list = (
            GachaPaymentEntry,
            ShopPaymentEntry,
        )
        post_nums = {
            str_target_date : {
                'sp' : 0,
                'pc' : 0,
            }
        }
        self.__logs = []
        for model_cls in model_cls_list:
            overwrite_sp = post_nums[str_target_date].get('sp', 0) < 1
            overwrite_pc = post_nums[str_target_date].get('pc', 0) < 1
            
            tmp_post_nums = self.work(model_cls, target_date, overwrite_sp, overwrite_pc) or {}
            for str_date,nums in tmp_post_nums.items():
                dic = post_nums[str_date] = post_nums.get(str_date) or {}
                for k,v in nums.items():
                    dic[k] = dic.get(k, 0) + v
            
            if self.response.isEnd:
                return
        
        # 送信した件数.
        self.__logs.append(u'nums:')
        for str_date,nums in post_nums.items():
            self.__logs.append(u'%s:sp=%s,pc=%s' % (str_date, nums.get('sp', 0), nums.get('pc', 0)))
        
        self.__logs.insert(0, 'OK')
        self.send(200, '\n'.join(self.__logs))
    
    def work(self, model_cls, target_date, overwrite_sp=True, overwrite_pc=True):
        self.__logs.append('overwrite_sp=%s,overwrite_pc=%s' % (overwrite_sp, overwrite_pc))
        
        s_date = target_date - datetime.timedelta(seconds=7200)
        e_date = target_date + datetime.timedelta(days=1, seconds=2700)
        str_target_date = target_date.strftime(Handler.TARGET_DATE_FORMAT)
        
        filters = {
            'state' : PaymentData.Status.COMPLETED,
            'ctime__gte' : s_date,
            'ctime__lt' : e_date,
        }
        LIMIT = PaymentLogRequestData.ENTRY_NUM_MAX
        offset = 0
        overwrite_flags = {
            'sp' : overwrite_sp,
            'pc' : overwrite_pc,
        }
        request_key_format = target_date.strftime('PaymentLog:%Y%m%d:{device}:{offset}')
        
        post_nums = {
            str_target_date : {
                'sp' : 0,
                'pc' : 0,
            }
        }
        def addPostNum(executedtime, device, cnt=1):
            str_date = executedtime.strftime(Handler.TARGET_DATE_FORMAT)
            nums = post_nums[str_date] = post_nums.get(str_date) or {
                'sp' : 0,
                'pc' : 0,
            }
            nums[device] += cnt
        
        while True:
            
            modellist = model_cls.fetchValues(['id','uid','price','inum'], filters=filters, limit=LIMIT, offset=offset, order_by='ctime', using=settings.DB_READONLY)
            if len(modellist) < 1:
                break
            
            requestdata_table = {}
            def getRequestData(device, executedtime):
                str_date = executedtime.strftime(Handler.TARGET_DATE_FORMAT)
                if str_target_date != str_date:
                    # 当日のレコードのみにする.
                    return None
                
                requestdata = requestdata_table.get(device)
                if requestdata is None:
                    requestdata = PaymentLogRequestData(executedtime, device, overwrite_flags[device])
                    requestdata_table[device] = requestdata
                
                return requestdata
            
            model_mgr = ModelRequestMgr()
            for model in modellist:
                # PC版をリリース前にPaymentEntryにdevice判定用のカラムを付けた方がいいかも.->と思ったけど結局executedTimeを取らなきゃいけなくなったのでこのままで.
                player = BackendApi.get_player(self, model.uid, [], using=settings.DB_READONLY, model_mgr=model_mgr)
                record = BackendApi.get_restful_paymentrecord(self, model.id, player.dmmid)
                is_pc = False
                if not str(record.paymentItems[0].itemId).isdigit():
                    # 無理やりだけど..
                    is_pc = True
                
                executedtime = record.executeTime
                if not isinstance(executedtime, datetime.datetime):
                    executedtime = DateTimeUtil.strToDateTime(executedtime, "%Y-%m-%d %H:%M:%S")
                
                device = 'pc' if is_pc else 'sp'
                requestdata = getRequestData(device, executedtime)
                if requestdata:
                    requestdata.addPaymentEntry(model.id, model.price, model.inum)
                    self.__logs.append(u'%s' % model.id)
                addPostNum(executedtime, device)
            
            for requestdata in requestdata_table.values():
                if len(requestdata.paymentList) < 1:
                    continue
                request = self.osa_util.makeApiRequest(ApiNames.PaymentLog, requestdata)
                reqkey = request_key_format.format(device=requestdata.device,offset=offset)
                self.addAppApiRequest(reqkey, request)
                
                overwrite_flags[requestdata.device] = False
            
            ret_data = self.execute_api()
            if ret_data:
                try:
                    for reqkey in ret_data.keys():
                        response_data = ret_data[reqkey].get()
                        if not response_data['is_success']:
                            raise AppError('PaymentLogApi Error:%s:data=%s' % (response_data['message'], response_data['data']))
                except urllib2.HTTPError, er:
                    if er.fp is None:
                        error_message = str(er)
                    else:
                        error_message = er.read()
                    error_message = 'HttpError:%s' % error_message
                    self.addlogerror('PaymentLog Failure:%s' % error_message)
                    self.send(200, error_message)
                    return
                except AppError, er:
                    error_message = 'AppError:%s' % er.value
                    self.addlogerror('PaymentLog Failure:%s' % error_message)
                    self.send(200, error_message)
                    return
                except Exception:
                    DbgLogger.write_error(self.osa_util.logger.to_string())
                    raise
            
            offset += LIMIT
        return post_nums

def main(request):
    return Handler.run(request)
