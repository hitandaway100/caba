# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.models.Player import PlayerGachaPt, PlayerRequest
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.views.application.gacha.base import GachaHandler
from platinumegg.app.cabaret.util.url_maker import UrlMaker
import urllib
from platinumegg.app.cabaret.util.cabareterror import CabaretError
import settings_sub
from platinumegg.lib.platform.api.objects import PaymentData
from platinumegg.app.cabaret.util.gacha import GachaUtil
from platinumegg.app.cabaret.models.PaymentEntry import GachaPaymentEntry
import settings
class Handler(GachaHandler):
    """引抜実行アニメ.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerGachaPt, PlayerRequest]
    
    def process(self):
        paymentId = self.request.get('paymentId')
        
        if paymentId:
            self.procPayment(paymentId)
        else:
            self.procFree()
    
    def procPayment(self, paymentId):
        """課金用フロー.
        """
        status = BackendApi.get_restful_paymentrecord_status(self, paymentId)
        lottery_point = None
        if status == PaymentData.Status.COMPLETED:
            # 購入書き込み.
            entry = GachaPaymentEntry.getByKey(paymentId)
            model_mgr = self.getModelMgr()
            gachamaster = BackendApi.get_gachamaster(model_mgr, entry.iid, using=settings.DB_READONLY)
            if gachamaster.point_rate:
                lottery_point = BackendApi.lottery_rates(gachamaster.point_rate)
                self.writePlayPaymentGacha(paymentId,player_trade_point=lottery_point)
            else:
                entry = self.writePlayPaymentGacha(paymentId)
            self.__buy_num = entry.inum
            self.set_masterid(entry.iid)
        elif status == PaymentData.Status.CANCEL:
            # キャンセル書き込み.
            self.writeGachaCancel(paymentId)
            self.writeAppHtml('gacha/cancel')
            return
        elif status == PaymentData.Status.TIMEOUT:
            # キャンセル書き込み.
            self.writeGachaTimeout(paymentId)
            self.writeAppHtml('gacha/timeout')
            return
        else:
            raise CabaretError(u'不正なアクセスです', CabaretError.Code.ILLEGAL_ARGS)
        
        playdata = self.getGachaPlayData()
        self.writeSwf(playdata,lottery_point=lottery_point)
    
    def procFree(self):
        """無料用フロー.
        """
        args = self.getUrlArgs('/gachaanim/')
        try:
            mid = int(args.get(0))
            key = urllib.unquote(args.get(1))
        except:
            raise CabaretError(u'引数が想定外です', CabaretError.Code.ILLEGAL_ARGS)
        self.set_masterid(mid)
        
        v_player = self.getViewerPlayer()
        if v_player.req_alreadykey != key:
            # 結果が見当たらない.
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'結果アニメを出せない')
            url = UrlMaker.gacha()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        
        playdata = self.getGachaPlayData()
        self.writeSwf(playdata)
    
    def writeSwf(self, playdata, lottery_point=None):
        """Swfに出力.
        """
        gachamaster = self.getGachaMaster()
        v_player = self.getViewerPlayer()
        effectpath = GachaUtil.makeGachaEffectPath(gachamaster)
        dataUrl = self.makeAppLinkUrlEffectParamGet(GachaUtil.makeGachaDataUrl(v_player, gachamaster, lottery_point=lottery_point))
        self.appRedirectToEffect2(effectpath, dataUrl)

def main(request):
    return Handler.run(request)
