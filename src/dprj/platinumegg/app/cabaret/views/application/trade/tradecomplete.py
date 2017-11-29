# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.application.trade.base import TradeBaseHandler
from platinumegg.app.cabaret.util.api import Objects, BackendApi
from platinumegg.app.cabaret.models.Player import PlayerTreasure, PlayerGachaPt
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from defines import Defines
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.lib.opensocial.util import OSAUtil



class Handler(TradeBaseHandler):
    """秘宝交換結果.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerTreasure, PlayerGachaPt]
    
    def process(self):
        args = self.getUrlArgs('/tradecomplete/')
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
        obj_player = Objects.player(self, v_player)
        
        # 秘宝交換レートリスト取得.
        trademaster = BackendApi.get_trademaster(model_mgr, mid, using=settings.DB_READONLY)
        if trademaster is None:
            raise CabaretError(u'交換できません', CabaretError.Code.INVALID_MASTERDATA)
        
        # 所持数.
        item_num = BackendApi.get_tradeitem_current_num(model_mgr, v_player, trademaster.itype, trademaster.itemid, using=settings.DB_READONLY)
        playerdata = None
        if 0 < trademaster.stock:
            playerdata = BackendApi.get_tradeplayerdata(model_mgr, v_player.id, mid, using=settings.DB_READONLY)

        obj_tradedata = self.makeobj(trademaster, playerdata)
        if trademaster.is_used_platinum_piece:
            have_piece_num = BackendApi.get_platinum_piece(model_mgr, v_player.id)
            
            self.html_param['trade_item_name_short'] = Defines.ItemType.NAMES[Defines.ItemType.PLATINUM_PIECE]
            self.html_param['trade_item_name_long'] = Defines.ItemType.NAMES[Defines.ItemType.PLATINUM_PIECE]
            self.html_param['item_num_before'] = have_piece_num + obj_tradedata['rate_cabaretking'] * num
            self.html_param['item_num_after'] = have_piece_num
        elif trademaster.is_used_battle_ticket:
            battleticket = BackendApi.get_additional_gachaticket_nums(model_mgr, v_player.id, [Defines.GachaConsumeType.GachaTicketType.BATTLE_TICKET], using=settings.DB_READONLY)
            if battleticket:
                battle_ticket_num = battleticket[Defines.GachaConsumeType.GachaTicketType.BATTLE_TICKET].num
            else:
                battle_ticket_num = 0
            self.html_param['trade_item_name_short'] ="チケット"
            self.html_param['trade_item_name_long'] = Defines.GachaConsumeType.NAMES[Defines.GachaConsumeType.BATTLE_TICKET]
            self.html_param['item_num_before'] = battle_ticket_num + obj_tradedata['rate_cabaretking'] * num
            self.html_param['item_num_after'] = battle_ticket_num
            tradeshop_urlparam = OSAUtil.addQuery(UrlMaker.trade(), Defines.URLQUERY_CTYPE, Defines.GachaConsumeType.GachaTopTopic.TICKET)
            self.html_param['url_trade'] = self.makeAppLinkUrl(tradeshop_urlparam)
        elif trademaster.is_used_crystal_piece:
            crystal_piece_num = BackendApi.get_crystal_piece(model_mgr, v_player.id)
            self.html_param['trade_item_name_short'] = Defines.ItemType.NAMES[Defines.ItemType.CRYSTAL_PIECE]
            self.html_param['trade_item_name_long'] = Defines.ItemType.NAMES[Defines.ItemType.CRYSTAL_PIECE]
            self.html_param['item_num_before'] = crystal_piece_num + obj_tradedata['rate_cabaretking'] * num
            self.html_param['item_num_after'] = crystal_piece_num
        else:
            self.html_param['trade_item_name_short'] = "秘宝"
            self.html_param['trade_item_name_long'] = "キャバ王の秘宝"
            self.html_param['item_num_before'] = obj_player['cabaretking'] + obj_tradedata['rate_cabaretking'] * num
            self.html_param['item_num_after'] = obj_player['cabaretking']
        
        self.html_param['player'] = obj_player
        self.html_param['tradedata'] = obj_tradedata
        self.html_param['item_num'] = item_num
        self.html_param['trade_num'] = num
        
        # リンク.
        self.html_param['obj_lead'] = self.makePrizeGetLinkParam(trademaster.itype, trademaster.itemid)
        if trademaster.itype == Defines.ItemType.ADDITIONAL_GACHATICKET:
            if trademaster.itemid in {
                    Defines.GachaConsumeType.GachaTicketType.REPRINT_TICKET,
                    Defines.GachaConsumeType.GachaTicketType.CASTTRADE_TICKET}:
                self.html_param['obj_lead'] = {
                    'url': self.makeAppLinkUrl(UrlMaker.reprintticket_tradeshop()),
                    'text': '交換する',
                }
        self.writeAppHtml('trade/tradecomplete')
    
    def __procEvent(self):
        """イベント用特殊処理.
        """
        try:
            eventid = int(self.request.get(Defines.URLQUERY_ID))
            ticketnum = int(self.request.get(Defines.URLQUERY_NUMBER))
        except:
            raise CabaretError(u'リクエストが正しくありません', CabaretError.Code.ILLEGAL_ARGS)
        
        model_mgr = self.getModelMgr()
        
        config = BackendApi.get_current_raideventconfig(model_mgr, using=settings.DB_READONLY)
        eventmaster = None
        if config.mid == eventid:
            eventmaster = BackendApi.get_raideventmaster(model_mgr, eventid, using=settings.DB_READONLY)
        if eventmaster is None:
            self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.trade()))
            return
        
        self.putRaidEventParams(eventmaster)
        
        self.html_param['add_num'] = ticketnum
        
        self.writeAppHtml('raidevent/tradecomplete')
    

def main(request):
    return Handler.run(request)
