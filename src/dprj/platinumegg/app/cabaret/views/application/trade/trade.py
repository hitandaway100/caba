# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.application.trade.base import TradeBaseHandler
from platinumegg.app.cabaret.util.api import Objects, BackendApi
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.models.Player import PlayerTreasure, PlayerDeck, PlayerPlatinumPiece
from platinumegg.lib.opensocial.util import OSAUtil
import settings
from defines import Defines


class Handler(TradeBaseHandler):
    """秘宝交換リスト.
    表示するもの.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerTreasure, PlayerDeck]
    
    def process(self):
        
        model_mgr = self.getModelMgr()
        
        # プレイヤー情報.
        v_player = self.getViewerPlayer()
        obj_player = Objects.player(self, v_player)
        
        # 初期タブ指定
        is_battle_ticket_page = int(self.request.get(Defines.URLQUERY_CTYPE, 0)) == Defines.GachaConsumeType.GachaTopTopic.TICKET

        # 秘宝交換レートリスト取得
        tradelist = BackendApi.get_trademaster_all(model_mgr, using=settings.DB_READONLY)
        tradelist.sort(key=lambda x:(x.schedule<<32)+x.rate_cabaretking, reverse=True)

        # カード所持数.
        cardnum = BackendApi.get_cardnum(v_player.id, model_mgr, using=settings.DB_READONLY)
        cardrest = v_player.cardlimit - cardnum
        is_cardnum_max = cardrest < 1
        
        platinum_piece_num = BackendApi.get_platinum_piece(model_mgr, v_player.id)
        crystal_piece_num = BackendApi.get_crystal_piece(model_mgr, v_player.id)

        now = OSAUtil.get_now()
        current_battleevent = BackendApi.get_current_battleeventconfig(model_mgr, using=settings.DB_READONLY)
        if current_battleevent.starttime < now < current_battleevent.epilogue_endtime and is_battle_ticket_page:
            # retrieve the trade items that CAN be traded with a battle ticket
            tradelist = [trade_item for trade_item in tradelist if trade_item.is_used_battle_ticket]
            self.html_param['is_battle_ticket_page'] = True
            url = OSAUtil.addQuery(UrlMaker.trade(), Defines.URLQUERY_CTYPE, Defines.GachaConsumeType.GachaTopTopic.TICKET)
            self.html_param['url_battle_ticket'] = self.makeAppLinkUrl(url)
        else:
            # retrieve the trade items that CANNOT be traded with a battle ticket
            tradelist = [trade_item for trade_item in tradelist if not trade_item.is_used_battle_ticket]
            self.html_param['is_battle_ticket_page'] = False

        battleticket = BackendApi.get_additional_gachaticket_nums(model_mgr, v_player.id, [Defines.GachaConsumeType.GachaTicketType.BATTLE_TICKET], using=settings.DB_READONLY)
        if battleticket:
            battle_ticket_num = battleticket[Defines.GachaConsumeType.GachaTicketType.BATTLE_TICKET].num
        else:
            battle_ticket_num = 0

        self.html_param['platinum_piece_num'] = platinum_piece_num
        self.html_param['platinum_piece_name'] = Defines.ItemType.NAMES[Defines.ItemType.PLATINUM_PIECE]
        self.html_param['battle_ticket_num'] = battle_ticket_num
        self.html_param['battle_ticket_name'] = Defines.GachaConsumeType.NAMES[Defines.GachaConsumeType.BATTLE_TICKET]
        self.html_param['crystal_piece_num'] = crystal_piece_num
        self.html_param['crystal_piece_name'] = Defines.ItemType.NAMES[Defines.ItemType.CRYSTAL_PIECE]

        cabaretking = v_player.get_cabaretking_num()
        
        obj_tradelist = []
        obj_tradelist_use_platinum_piece = []
        obj_tradelist_use_battle_ticket = []
        obj_tradelist_use_crystal_piece = []

        limited_masters = {}    # ストック制限が有るマスター.
        slide_cards = {}        # スライド表示するカード.
        header_img_list = []    # ヘッダ画像.
        
        for trademaster in tradelist:
            if not BackendApi.check_schedule(model_mgr, trademaster.schedule, using=settings.DB_READONLY):
                continue
            
            if trademaster.stock:
                limited_masters[trademaster.id] = trademaster
            
            data = self.makeobj(trademaster)
            data['url_tradeyesno'] = self.makeAppLinkUrl(UrlMaker.tradeyesno(trademaster.id))
            err_mess = None
            
            # 最大交換可能数.
            if trademaster.is_used_platinum_piece:
                trade_max = int(platinum_piece_num / trademaster.rate_cabaretking)
            elif trademaster.is_used_battle_ticket:
                trade_max = int(battle_ticket_num / trademaster.rate_cabaretking)
            elif trademaster.is_used_crystal_piece:
                trade_max = int(crystal_piece_num / trademaster.rate_cabaretking)
            else:
                trade_max = int(cabaretking / trademaster.rate_cabaretking)
            data['ori_trade_max'] = trade_max
            
            if trademaster.itype == Defines.ItemType.CARD and is_cardnum_max:
                err_mess = u'所属キャストが上限に達しています'
            elif trade_max == 0:
                if trademaster.is_used_platinum_piece:
                    err_mess = u'%sが不足しています' % Defines.ItemType.NAMES[Defines.ItemType.PLATINUM_PIECE]
                elif trademaster.is_used_battle_ticket:
                    err_mess = u'%sが不足しています' % Defines.GachaConsumeType.NAMES[Defines.GachaConsumeType.BATTLE_TICKET]
                elif trademaster.is_used_crystal_piece:
                    err_mess = u'%sが不足しています' % Defines.ItemType.NAMES[Defines.ItemType.CRYSTAL_PIECE]
                else:
                    err_mess = u'%sが不足しています' % Defines.ItemType.NAMES[Defines.ItemType.CABARETKING_TREASURE]
            data['err_mess'] = err_mess
            
            if trademaster.itype == Defines.ItemType.CARD:
                trade_max = min(trade_max, cardrest)
            if Defines.ItemType.TRADE_NUM_MAX.has_key(trademaster.itype):
                trade_max = min(Defines.ItemType.TRADE_NUM_MAX[trademaster.itype], trade_max)
            data['trade_max'] = trade_max
            
            data['is_used_platinum_piece'] = trademaster.is_used_platinum_piece
            data['is_used_battle_ticket'] = trademaster.is_used_battle_ticket
            data['is_used_crystal_piece'] = trademaster.is_used_crystal_piece
            if trademaster.is_used_platinum_piece:
                obj_tradelist_use_platinum_piece.append(data)
            elif trademaster.is_used_battle_ticket:
                obj_tradelist_use_battle_ticket.append(data)
            elif trademaster.is_used_crystal_piece:
                obj_tradelist_use_crystal_piece.append(data)
            else:
                obj_tradelist.append(data)
            
            # スライド.
            if trademaster.slidecapture and trademaster.itype == Defines.ItemType.CARD:
                slide_cards[trademaster.itemid] = self.makeAppLinkUrlImg(trademaster.slidecapture)
            
            if trademaster.header:
                header_img_list.append(self.makeAppLinkUrlImg(trademaster.header))
        
        playdata_dict = BackendApi.get_tradeplayerdata_dict(model_mgr, v_player.id, limited_masters.keys(), using=settings.DB_READONLY)
        self.reflect_use_status(model_mgr, obj_tradelist, limited_masters, playdata_dict)
        self.reflect_use_status(model_mgr, obj_tradelist_use_platinum_piece, limited_masters, playdata_dict)
        self.reflect_use_status(model_mgr, obj_tradelist_use_battle_ticket, limited_masters, playdata_dict)
        self.reflect_use_status(model_mgr, obj_tradelist_use_crystal_piece, limited_masters, playdata_dict)

        # スライド.
        obj_slidelist = []
        if slide_cards:
            cardmasters = BackendApi.get_cardmasters(slide_cards.keys(), model_mgr, using=settings.DB_READONLY)
            for cardid, img in slide_cards.items():
                cardmaster = cardmasters.get(cardid)
                if not cardmaster:
                    continue
                obj_slidelist.append((
                    Objects.cardmaster(self, cardmaster),
                    img,
                ))
        
        self.putFromBackPageLinkUrl()
        
        self.html_param['player'] = obj_player
        self.html_param['tradelists'] = [
            obj_tradelist_use_crystal_piece,
            obj_tradelist_use_platinum_piece,
            obj_tradelist_use_battle_ticket,
            obj_tradelist,
        ]
        self.html_param['headerlist'] = header_img_list
        self.html_param['slidelist'] = obj_slidelist
        
        self.putRaidEventParams()

        self.writeAppHtml('trade/trade')
    
    def reflect_use_status(self, model_mgr, tradelist, limited_masters, playdata_dict):
        for obj_trade in tradelist:
            mid = obj_trade['id']
            master = limited_masters.get(mid)
            playdata = playdata_dict.get(mid)
            if master is None or master.stock < 1:
                continue
            
            trade_cnt = BackendApi.get_trade_cnt(model_mgr, master, playdata, using=settings.DB_READONLY)
            obj_trade['trade_cnt'] = trade_cnt
            if master.stock and master.stock <= trade_cnt:
                obj_trade['err_mess'] = u'これ以上交換できません'
                obj_trade['trade_max'] = 0
            else:
                # 交換可能数を在庫数で制限.
                obj_trade['trade_max'] = min(master.stock - trade_cnt, obj_trade['trade_max'])
def main(request):
    return Handler.run(request)
