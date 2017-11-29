# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from defines import Defines
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.url_maker import UrlMaker
import settings
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.models.Shop import ShopItemMaster
from platinumegg.app.cabaret.models.Gacha import GachaMaster


class Handler(AppHandler):
    """課金履歴一覧ページ.
    """
    
    CONTENT_NUM = 10
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        
        kind = self.request.get('_kind')
        is_complete = self.request.get('_comp') == '1'
        page = str(self.request.get(Defines.URLQUERY_PAGE))
        if page.isdigit():
            page = int(page)
        else:
            page = 0
        
        table = {
            'gacha' : self.procGacha,
            'shop' : self.procShop,
        }
        table.get(kind, self.procGacha)(is_complete, page)
    
    def procShop(self, is_complete, page):
        """ショップの課金情報.
        """
        v_player = self.getViewerPlayer()
        
        offset = page * Handler.CONTENT_NUM
        limit = Handler.CONTENT_NUM + 1
        paymentlist = BackendApi.get_shoppaymententry_list(v_player.id, is_complete, limit, offset, using=settings.DB_READONLY)
        has_nextpage = True if limit == len(paymentlist) else False
        paymentlist = paymentlist[:Handler.CONTENT_NUM]
        
        def urlmaker(payment):
            return UrlMaker.shopresult(payment.iid)
        obj_paymentlist = self.makePaymentObjList(paymentlist, ShopItemMaster, urlmaker)
        
        self.writeHtml(obj_paymentlist, 'shop', is_complete, page, has_nextpage)
    
    def procGacha(self, is_complete, page):
        """ガチャの課金情報.
        """
        v_player = self.getViewerPlayer()
        
        offset = page * Handler.CONTENT_NUM
        limit = Handler.CONTENT_NUM + 1
        paymentlist = BackendApi.get_gachapaymententry_list(v_player.id, is_complete, limit, offset, using=settings.DB_READONLY)
        has_nextpage = True if limit == len(paymentlist) else False
        paymentlist = paymentlist[:Handler.CONTENT_NUM]
        
        def urlmaker(payment):
            return UrlMaker.gachaanim(payment.iid, '')
        obj_paymentlist = self.makePaymentObjList(paymentlist, GachaMaster, urlmaker)
        
        self.writeHtml(obj_paymentlist, 'gacha', is_complete, page, has_nextpage)
    
    def makePaymentObjList(self, paymentlist, master_cls, urlmaker):
        """HTML埋め込み用のオブジェクトに課金情報.
        """
        model_mgr = self.getModelMgr()
        
        master_idlist = [payment.iid for payment in paymentlist]
        masters = BackendApi.get_model_dict(model_mgr, master_cls, master_idlist, using=settings.DB_READONLY)
        
        obj_paymentlist = []
        for payment in paymentlist:
            obj = self.makePaymentObj(payment, masters.get(payment.iid), urlmaker(payment))
            obj_paymentlist.append(obj)
        return obj_paymentlist
    
    def makePaymentObj(self, paymententry, goodsmaster, url_continue):
        """HTML用のオブジェクトにする.
        """
        if goodsmaster:
            name = goodsmaster.name
        else:
            name = u'不明の商品'
        return {
            'name' : name,
            'ctime' : paymententry.ctime.strftime(u"%m月%d日 %H:%M"),
            'unitPrice' : paymententry.price,
            'num' : paymententry.inum,
            'url_continue' : self.makeAppLinkUrl(OSAUtil.addQuery(url_continue, 'paymentId', paymententry.id))
        }
    
    def writeHtml(self, obj_paymentlist, kind, is_complete, page, has_nextpage):
        """html描画.
        """
        self.html_param['kind'] = kind
        self.html_param['is_complete'] = is_complete
        self.html_param['paymentlist'] = obj_paymentlist
        
        self.putPagenation(kind, is_complete, page, has_nextpage)
        
        self.writeAppHtml('support/paymentlist')
    
    def putPagenation(self, kind, is_complete, page, has_nextpage):
        """ページング.
        """
        urlbase = UrlMaker.support_paymentlist()
        if kind:
            urlbase = OSAUtil.addQuery(urlbase, '_kind', kind)
        if is_complete:
            urlbase = OSAUtil.addQuery(urlbase, '_comp', 1)
        if 0 < page:
            self.html_param['url_page_prev'] = self.makeAppLinkUrl(OSAUtil.addQuery(urlbase, Defines.URLQUERY_PAGE, page - 1))
        if has_nextpage:
            self.html_param['url_page_next'] = self.makeAppLinkUrl(OSAUtil.addQuery(urlbase, Defines.URLQUERY_PAGE, page + 1))

def main(request):
    return Handler.run(request)
