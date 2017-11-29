# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.adminhandler import AdminHandler
from platinumegg.app.cabaret.util.api import BackendApi
import settings
backup_db = getattr(settings, 'DB_BACKUP', settings.DB_READONLY)

class Handler(AdminHandler):
    """DMM側の課金履歴を確認.
    """
    def process(self):
        
        paymentId = self.request.get('_paymentId')
        if paymentId:
            model_mgr = self.getModelMgr()
            
            paymententry = BackendApi.get_gachapaymententry(model_mgr, paymentId, using=backup_db)
            if paymententry is None:
                paymententry = BackendApi.get_shoppaymententry(model_mgr, paymentId, using=backup_db)
            
            if paymententry:
                player = BackendApi.get_player(self, paymententry.uid, [], using=settings.DB_READONLY, model_mgr=model_mgr)
                dmmid = player.dmmid
            else:
                dmmid = self.request.get('_dmmId')
            
            paymentdata = BackendApi.get_restful_paymentrecord(self, paymentId, dmmid)
            self.html_param['payment_record'] = paymentdata
        
        self.writeAppHtml('infomations/view_dmmpayment')
    
def main(request):
    return Handler.run(request)
