# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.models.Player import PlayerDeck,\
    PlayerGold, PlayerGachaPt, PlayerKey, PlayerCrossPromotion
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
import settings_sub
import urllib
import settings
from platinumegg.lib.opensocial.util import OSAUtil
from defines import Defines
from platinumegg.app.cabaret.views.application.trade.base import TradeBaseHandler

class Handler(TradeBaseHandler):
    """秘宝交換書き込み.
    """
    
    def process(self):
        args = self.getUrlArgs('/tradedo/')
        str_mid = args.get(0)
        if str_mid == 'event':
            self.__procEvent(args)
            return
        
        try:
            mid = int(str_mid)
            confirmkey = urllib.unquote(args.get(1))
            num = int(self.request.get(Defines.URLQUERY_NUMBER, 1))
        except:
            raise CabaretError(u'リクエストが正しくありません', CabaretError.Code.ILLEGAL_ARGS)
        
        model_mgr = self.getModelMgr()
        
        trademaster = BackendApi.get_trademaster(model_mgr, mid, using=settings.DB_READONLY)
        if trademaster is None:
            raise CabaretError(u'秘宝交換のマスターデータが見つかりません', CabaretError.Code.ILLEGAL_ARGS)
        
        # プレイヤー情報.
        v_player = self.getViewerPlayer()
        
        # 書き込み
        try:
            model_mgr = db_util.run_in_transaction(self.tr_write_trade, v_player.id, trademaster, confirmkey, num)
            model_mgr.write_end()
        except CabaretError, err:
            if settings_sub.IS_LOCAL:
                raise
            elif err.code == CabaretError.Code.ALREADY_RECEIVED:
                pass
            else:
                url = UrlMaker.tradeyesno(mid)
                self.appRedirect(self.makeAppLinkUrlRedirect(url))
                return
        
        # リダイレクト.
        url = OSAUtil.addQuery(UrlMaker.tradecomplete(mid), Defines.URLQUERY_NUMBER, num)
        url = self.makeAppLinkUrlRedirect(url)
        self.appRedirect(url)
    
    def tr_write_trade(self, uid, trademaster, confirmkey, num):
        """秘宝 or プラチナの欠片 or クリスタルの欠片 交換書き込み.
        """
        model_mgr = ModelRequestMgr()
        player = BackendApi.get_players(self, [uid], [PlayerDeck, PlayerGold, PlayerGachaPt, PlayerKey], model_mgr=model_mgr)[0]
        BackendApi.tr_trade_item(model_mgr, player, trademaster, confirmkey, num)
        if PlayerCrossPromotion.is_session():
            BackendApi.update_player_cross_promotion(model_mgr, player.id, "is_trade_treasure")
        model_mgr.write_all()
        return model_mgr
    
    def __procEvent(self, args):
        """イベント用特殊処理.
        """
        try:
            confirmkey = urllib.unquote(args.get(1))
        except:
            raise CabaretError(u'リクエストが正しくありません', CabaretError.Code.ILLEGAL_ARGS)
        
        model_mgr = self.getModelMgr()
        cur_eventmaster = self.getCurrentEventMaster()
        if cur_eventmaster is None:
            # イベントが終わっている.
            self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.trade()))
            return
        
        v_player = self.getViewerPlayer()
        uid = v_player.id
        
        scorerecord = BackendApi.get_raidevent_scorerecord(model_mgr, cur_eventmaster.id, uid, using=settings.DB_DEFAULT)
        num = 0
        if scorerecord:
            num = int(scorerecord.point / cur_eventmaster.pointratio)
        if num < 1:
            self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.trade()))
            return
        
        # 書き込み
        try:
            model_mgr = db_util.run_in_transaction(self.tr_write_eventtrade, uid, cur_eventmaster, num, confirmkey)
            model_mgr.write_end()
        except CabaretError, err:
            if settings_sub.IS_LOCAL:
                raise
            elif err.code == CabaretError.Code.ALREADY_RECEIVED:
                pass
            else:
                url = UrlMaker.tradeyesno('event')
                self.appRedirect(self.makeAppLinkUrlRedirect(url))
                return
        # リダイレクト.
        url = OSAUtil.addQuery(UrlMaker.tradecomplete('event'), Defines.URLQUERY_NUMBER, num)
        url = OSAUtil.addQuery(url, Defines.URLQUERY_ID, cur_eventmaster.id)
        url = self.makeAppLinkUrlRedirect(url)
        self.appRedirect(url)
    
    @staticmethod
    def tr_write_eventtrade(uid, eventmaster, num, confirmkey):
        """イベント用書き込み.
        """
        model_mgr = ModelRequestMgr()
        BackendApi.tr_trade_raidevent_score(model_mgr, uid, eventmaster, num, confirmkey)
        model_mgr.write_all()
        return model_mgr
    
    

def main(request):
    return Handler.run(request)
