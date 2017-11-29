# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.application.shop.base import ShopHandler
from platinumegg.lib.platform.api.request import ApiNames
from platinumegg.lib.platform.api.objects import PaymentGetRequestData,\
    PaymentData
import settings_sub
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.lib.opensocial.util import OSAUtil
from defines import Defines


class Handler(ShopHandler):
    """ショップ課金コールバック.
    """
    @classmethod
    def get_default_status(cls):
        """デフォルトで返すHttpStatus.
        """
        return 500
    
    def checkUser(self):
        pass
    def check_process_pre(self):
        return True
    
    def processError(self, error_message):
        self.osa_util.logger.error(error_message)
        self.response.set_status(500)
        self.response.end()
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        
        v_player = self.getViewerPlayer()
        
        # セッションを切っておく.
        client = OSAUtil.get_cache_client()
        client.delete(self.osa_util.viewer_id, namespace='session')
        client.delete('payment_checked:%s' % v_player.id)
        
        paymentId = self.request.get('paymentId')
        
        if not settings_sub.IS_LOCAL:
            if not paymentId:
                raise "paymentId is None"
            # APIで課金情報を取得.
            data = PaymentGetRequestData()
            data.paymentId = paymentId
            data.guid = self.osa_util.viewer_id
            
            request = self.osa_util.makeApiRequest(ApiNames.PaymentGet, data)
            self.addAppApiRequest('payment_check', request)
            ret_data = self.execute_api()
            paymentdata = ret_data['payment_check'].get()
            if paymentdata.status != PaymentData.Status.START:
                raise "Illegal status"
        
        model_mgr, entry = db_util.run_in_transaction(Handler.tr_update_entry, v_player.id, paymentId)
        model_mgr.write_end()
        
        if settings_sub.IS_LOCAL:
            url = UrlMaker.shopresult(entry.iid)
            url = OSAUtil.addQuery(url, 'paymentId', paymentId)
            url = OSAUtil.addQuery(url, Defines.URLQUERY_STATE, PaymentData.Status.COMPLETED)
            self.response.set_status(200)
            self.appRedirect(self.makeAppLinkUrl(url, add_frompage=False))
        else:
            self.response.set_status(200)
            self.response.end()
    
    @staticmethod
    def tr_update_entry(uid, paymentId):
        """課金レコードを作成.
        """
        model_mgr = ModelRequestMgr()
        entry = BackendApi.tr_update_shoppaymententry(model_mgr, uid, paymentId, PaymentData.Status.START)
        model_mgr.write_all()
        return model_mgr, entry

def main(request):
    return Handler.run(request)
