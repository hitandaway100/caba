# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.adminhandler import AdminHandler
from defines import Defines
import settings
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.models.Shop import ShopItemMaster
from platinumegg.app.cabaret.models.Gacha import GachaMaster
from platinumegg.app.cabaret.util.alert import AlertCode
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.datetime_util import DateTimeUtil

backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)

class Handler(AdminHandler):
    """課金履歴確認.
    """
    def process(self):
        
        uid = self.__get_uid()
        logtype = self.request.get('_logtype')
        is_complete = self.request.get('_is_complete') == '1'
        str_stime = self.request.get('_stime') or ''
        str_etime = self.request.get('_etime') or ''
        
        self.html_param['_logtype'] = logtype
        self.html_param['_is_complete'] = is_complete
        self.html_param['_stime'] = str_stime
        self.html_param['_etime'] = str_etime
        
        def to_datetime(st):
            try:
                return DateTimeUtil.strToDateTime(st, '%Y/%m/%d %H:%M:%S')
            except:
                return None
        
        table = {
            'gacha' : self.procGacha,
            'shop' : self.procShop,
        }
        if uid and table.has_key(logtype):
            paymentlist = table[logtype](uid, is_complete, to_datetime(str_stime), to_datetime(str_etime))
            if not paymentlist:
                self.putAlertToHtmlParam(u'見つかりませんでした', AlertCode.WARNING)
            self.html_param['paymentlist'] = paymentlist
        
        self.html_param['Defines'] = Defines
        self.html_param['url_view_paymentlog'] = self.makeAppLinkUrlAdmin(UrlMaker.mgr_infomations('view_paymentlog'))
        
        self.writeAppHtml('infomations/view_paymentlog')
    
    def __get_uid(self):
        serchtype = self.request.get('_serchtype')
        v = self.request.get('_value')
        
        self.html_param['_serchtype'] = serchtype
        self.html_param['_value'] = v
        
        uid = None
        if serchtype == 'uid':
            uid = str(v)
            if uid and uid.isdigit():
                uid = int(uid)
            else:
                uid = None
        elif serchtype == 'dmmid':
            dmmid = str(v)
            uid = BackendApi.dmmid_to_appuid(self, [dmmid], using=backup_db).get(dmmid)
        return uid
    
    def procShop(self, uid, is_complete, stime, etime):
        """ショップの課金情報.
        """
        paymentlist = BackendApi.get_shoppaymententry_list(uid, is_complete, using=backup_db)
        if stime or etime:
            stime = stime or OSAUtil.get_datetime_min()
            etime = etime or OSAUtil.get_datetime_min()
            paymentlist = [payment for payment in paymentlist if stime <= payment.ctime < etime]
        obj_paymentlist = self.makePaymentObjList(paymentlist, ShopItemMaster)
        return obj_paymentlist
    
    def procGacha(self, uid, is_complete, stime, etime):
        """ガチャの課金情報.
        """
        paymentlist = BackendApi.get_gachapaymententry_list(uid, is_complete, using=backup_db)
        if stime or etime:
            stime = stime or OSAUtil.get_datetime_min()
            etime = etime or OSAUtil.get_datetime_min()
            paymentlist = [payment for payment in paymentlist if stime <= payment.ctime < etime]
        obj_paymentlist = self.makePaymentObjList(paymentlist, GachaMaster)
        return obj_paymentlist
    
    def makePaymentObjList(self, paymentlist, master_cls):
        """HTML埋め込み用のオブジェクトに課金情報.
        """
        model_mgr = self.getModelMgr()
        
        master_idlist = [payment.iid for payment in paymentlist]
        masters = BackendApi.get_model_dict(model_mgr, master_cls, master_idlist, using=backup_db)
        
        obj_paymentlist = []
        for payment in paymentlist:
            obj = self.makePaymentObj(payment, masters.get(payment.iid))
            obj_paymentlist.append(obj)
        return obj_paymentlist
    
    def makePaymentObj(self, paymententry, goodsmaster):
        """HTML用のオブジェクトにする.
        """
        if goodsmaster:
            name = goodsmaster.name
        else:
            name = u'不明の商品'
        return {
            'name' : name,
            'ctime' : paymententry.ctime.strftime(u"%m月%d日 %H:%M:%S"),
            'unitPrice' : paymententry.price,
            'num' : paymententry.inum,
        }

def main(request):
    return Handler.run(request)
