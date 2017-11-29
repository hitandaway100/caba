# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.application.trade.base import TradeBaseHandler
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.models.Player import PlayerTreasure, PlayerRequest,\
    PlayerDeck, PlayerPlatinumPiece, PlayerCrystalPiece
from platinumegg.app.cabaret.util.cabareterror import CabaretError
import settings
from defines import Defines
from platinumegg.lib.opensocial.util import OSAUtil


class Handler(TradeBaseHandler):
    """秘宝交換確認.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerTreasure, PlayerRequest, PlayerDeck]
    
    def process(self):
        args = self.getUrlArgs('/tradeyesno/')
        str_mid = args.get(0)
        if str_mid == 'event':
            self.__procEvent()
            return
        
        try:
            mid = int(str_mid)
            num = int(self.request.get(Defines.URLQUERY_NUMBER, 1))
        except:
            raise CabaretError(u'リクエストが正しくありません', CabaretError.Code.ILLEGAL_ARGS)
        
        model_mgr = self.getModelMgr()
        
        # プレイヤー情報.
        v_player = self.getViewerPlayer()

        cabaretking = v_player.get_cabaretking_num()

        # 秘宝交換レートリスト取得
        trademaster = BackendApi.get_trademaster(model_mgr, mid, using=settings.DB_READONLY)
        if trademaster.is_used_platinum_piece:
            use_item_name = Defines.ItemType.NAMES[Defines.ItemType.PLATINUM_PIECE]
            cabaretking = BackendApi.get_model(model_mgr, PlayerPlatinumPiece, v_player.id, using=settings.DB_READONLY).count
        elif trademaster.is_used_battle_ticket:
            use_item_name = Defines.GachaConsumeType.NAMES[Defines.GachaConsumeType.BATTLE_TICKET]
            tradeshop_urlparam = OSAUtil.addQuery(UrlMaker.trade(), Defines.URLQUERY_CTYPE, Defines.GachaConsumeType.GachaTopTopic.TICKET)
            self.html_param['url_battleticket_trade'] = self.makeAppLinkUrl(tradeshop_urlparam)
        elif trademaster.is_used_crystal_piece:
            use_item_name = Defines.ItemType.NAMES[Defines.ItemType.CRYSTAL_PIECE]
            cabaretking = BackendApi.get_model(model_mgr, PlayerCrystalPiece, v_player.id, using=settings.DB_READONLY).count
        else:
            use_item_name = "秘宝"
        self.html_param['use_item_name'] = use_item_name

        # Calculate the (possible) maximum number of items to trade
        trade_max = int(cabaretking / trademaster.rate_cabaretking)
        
        if trademaster is None:
            raise CabaretError(u'秘宝交換のマスターデータが見つかりません', CabaretError.Code.INVALID_MASTERDATA)
        elif 0 < trademaster.stock < num:
            raise CabaretError(u'秘宝交換の交換可能回数を超えています', CabaretError.Code.OVER_LIMIT)
        
        playerdata = None
        if 0 < trademaster.stock:
            playerdata = BackendApi.get_tradeplayerdata(model_mgr, v_player.id, mid, using=settings.DB_READONLY)
        
        obj_tradedata = self.makeobj(trademaster, playerdata)
        
        err_mess = None

        if not BackendApi.check_schedule(model_mgr, trademaster.schedule):
            err_mess = u'交換期間が終了しました'
        elif 0 < trademaster.stock and trademaster.stock <= obj_tradedata['trade_cnt']:
            err_mess = u'これ以上交換できません'
        elif 0 < trademaster.stock and trademaster.stock < (obj_tradedata['trade_cnt'] + num):
            err_mess = u'交換可能回数を超えます'
        elif trademaster.itype == Defines.ItemType.CARD:
            # 所持数チェック.
            cardnum = BackendApi.get_cardnum(v_player.id, arg_model_mgr=model_mgr, using=settings.DB_READONLY)
            if v_player.cardlimit < cardnum + num:
                err_mess = u'所属キャストの上限を超えます'
            trade_max = min(trade_max, v_player.cardlimit - cardnum)
        
        self.html_param['err_mess'] = err_mess
        if not err_mess and num == Defines.TradeNumChoices.ALL:
            # numをちゃんとした値に変更.
            if Defines.ItemType.TRADE_NUM_MAX.has_key(trademaster.itype):
                trade_max = min(Defines.ItemType.TRADE_NUM_MAX[trademaster.itype], trade_max)
            if 0 < trademaster.stock:
                trade_max = min(trademaster.stock - obj_tradedata['trade_cnt'], trade_max)
            num = trade_max
        
        url = OSAUtil.addQuery(UrlMaker.tradedo(mid, v_player.req_confirmkey), Defines.URLQUERY_NUMBER, num)
        obj_tradedata['url_tradedo'] = self.makeAppLinkUrl(url)
        
        self.html_param['tradedata'] = obj_tradedata
        
        self.html_param['trade_point'] = trademaster.rate_cabaretking * num
        self.html_param['trade_num'] = num
        
        self.writeAppHtml('trade/tradeyesno')
    
    def __procEvent(self):
        """イベント用特殊処理.
        """
        cur_eventmaster = self.putRaidEventParams()
        if cur_eventmaster is None:
            # イベントが終わっている.
            self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.trade()))
            return
        
        v_player = self.getViewerPlayer()
        
        self.html_param['url_tradedo'] = self.makeAppLinkUrl(UrlMaker.tradedo('event', v_player.req_confirmkey))
        
        self.writeAppHtml('raidevent/tradeyesno')
    

def main(request):
    return Handler.run(request)
