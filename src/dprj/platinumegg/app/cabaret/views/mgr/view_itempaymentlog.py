# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.adminhandler import AdminHandler
from defines import Defines
import settings
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.models.Shop import ShopItemMaster
from platinumegg.app.cabaret.util.alert import AlertCode
from platinumegg.lib.platform.api.objects import PaymentData
from platinumegg.app.cabaret.models.PaymentEntry import ShopPaymentEntry
backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)

class Handler(AdminHandler):
    """アイテム毎課金履歴確認.
    """
    def process(self):
        
        uid = self.__get_uid()
        itemtype_list = self.__get_itemtypelist()
        is_complete = self.request.get('_is_complete') == '1'
        
        self.html_param['_itemtype_list'] = itemtype_list
        self.html_param['_is_complete'] = is_complete
        
        if itemtype_list:
            paymentlist = self.procItem(uid, itemtype_list, is_complete)
            if not paymentlist:
                self.putAlertToHtmlParam(u'見つかりませんでした', AlertCode.WARNING)
            self.html_param['paymentlist'] = paymentlist
        
        self.html_param['Defines'] = Defines
        self.html_param['itemlist'] = self.makeShopItemObjList()
        self.html_param['url_view_itempaymentlog'] = self.makeAppLinkUrlAdmin(UrlMaker.mgr_infomations('view_itempaymentlog'))
        
        self.writeAppHtml('infomations/view_itempaymentlog')
    
    def __get_uid(self):
        serchtype = self.request.get('_serchtype')
        v = self.request.get('_value')
        
        self.html_param['_serchtype'] = serchtype
        self.html_param['_value'] = v
        
        uid = None
        if v != '':
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
    
    def __get_itemtypelist(self):
        """
        """
        cnt = 0
        dest = []
        itemtype = self.request.get('_itemtype')
        if itemtype:
            dest.append(itemtype)
        
        while True:
            itemtype = self.request.get('_itemtype%d' % cnt)
            if not itemtype:
                break
            dest.append(itemtype)
            cnt += 1
        return dest
    
    def procItem(self, uid, itemtype_list, is_complete):
        """アイテムの課金情報.
        """
        if uid:
            wuid = 'uid = %s and ' % (uid)
        else:
            wuid = ''
        if is_complete:
            state = PaymentData.Status.COMPLETED
        else:
            state = PaymentData.Status.START
        sql = '''select id, date_format(ctime, '%%%%Y-%%%%m-%%%%d') as date, count(*) as num, sum(inum) as volume, sum(price * inum) as tprice from cabaret_shoppaymententry where %s iid in (%s) and state = %s group by date order by date desc;''' % (wuid, ','.join(list(set(itemtype_list))), state)
        query = ShopPaymentEntry.sql("", using=backup_db)
        paymentlist = query.execute_all(sql, [], using=backup_db)
        
        obj_paymentlist = self.makePaymentObjList(paymentlist)
        
        return obj_paymentlist
    
    def procShop(self, uid, is_complete):
        """ショップの課金情報.
        """
        paymentlist = BackendApi.get_shoppaymententry_list(uid, is_complete, using=backup_db)
        obj_paymentlist = self.makePaymentObjList(paymentlist, ShopItemMaster)
        return obj_paymentlist
    
    def makePaymentObjList(self, paymentlist):
        """HTML埋め込み用のオブジェクトに課金情報.
        """
        obj_paymentlist = []
        for payment in paymentlist:
            obj = self.makePaymentObj(payment)
            obj_paymentlist.append(obj)
        return obj_paymentlist
    
    def makePaymentObj(self, paymententry):
        """HTML用のオブジェクトにする.
        """
        (_, date, num, volume, price) = paymententry
        return {
            'date' : date,
            'num' : num,
            'volume' : volume,
            'tprice' : price,
        }
    
    def makeShopItemObjList(self):
        """HTML埋め込み用のオブジェクト.
        """
        model_mgr = self.getModelMgr()
        
        shopmasterlist = model_mgr.get_mastermodel_all(ShopItemMaster, using=backup_db)
        
        item = []
        for shopitem in shopmasterlist:
            item.append((shopitem.id, shopitem.name))
        
        return {
            'item' : item
        }

def main(request):
    return Handler.run(request)
