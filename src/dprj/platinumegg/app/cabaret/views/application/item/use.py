# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.models.Player import PlayerAp, PlayerFriend,\
    PlayerDeck, PlayerGold, PlayerGachaPt
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from defines import Defines
import settings_sub

class Handler(AppHandler):
    """旧アイテム使用書き込み.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerAp, PlayerFriend, PlayerDeck, PlayerGold, PlayerGachaPt]
    
    def redirectWithError(self, err, url=None):
        if settings_sub.IS_LOCAL:
            raise err
        elif url is None:
            url = UrlMaker.itemlist()
        self.appRedirect(self.makeAppLinkUrlRedirect(url))
    
    def process(self):
        
        try:
            args = self.getUrlArgs('/item_use/')
            mid = int(args.get(0))
            before_num = int(args.get(1))
            usenum = int(self.request.get(Defines.URLQUERY_NUMBER) or 1)
        except:
            self.redirectWithError(CabaretError(u'リクエストが正しくありません', CabaretError.Code.ILLEGAL_ARGS))
            return
        
        if not mid in Defines.ItemEffect.USE_ABLE:
            self.redirectWithError(CabaretError(u'このアイテムは使用できません', CabaretError.Code.ILLEGAL_ARGS))
            return
        elif Defines.ItemEffect.USE_NUM_MAX.get(mid, usenum) < usenum:
            url = UrlMaker.item_useyesno(mid)
            self.redirectWithError(CabaretError(u'一度に使用できる上限数を超えています', CabaretError.Code.ILLEGAL_ARGS), url)
            return
        
        model_mgr = ModelRequestMgr()
        
        # プレイヤー情報.
        v_player = self.getViewerPlayer()
        
        # 所持数.
        num = BackendApi.get_item_nums(model_mgr, v_player.id, [mid], using=settings.DB_DEFAULT).get(mid, None)
        if before_num != num or (num is not None and num < usenum):
            # 正しく処理できない.
            url = UrlMaker.item_useyesno(mid) if num is not None else None
            self.redirectWithError(CabaretError(u'正しく処理できません出来ませんでした', CabaretError.Code.ILLEGAL_ARGS), url)
            return
        self.__before_num = num
        self.__after_num = self.__before_num - usenum
        
        # マスターデータ.
        itemmaster = BackendApi.get_itemmaster(model_mgr, mid, using=settings.DB_READONLY)
        
        # 書き込み.
        table = {
            Defines.ItemEffect.CARD_BOX_EXPANSION : self.writeBoxExpansion,
        }
        table.update(**dict.fromkeys(Defines.ItemEffect.ACTION_RECOVERY_ITEMS, self.writeApRecover))
        table.update(**dict.fromkeys(Defines.ItemEffect.TENSION_RECOVERY_ITEMS, self.writeBpRecover))
        table.update(**dict.fromkeys(Defines.ItemEffect.GACHA_PT_ACQUISITION_ITEMS, self.writeAddGachaPoint))
        table.update(**dict.fromkeys(Defines.ItemEffect.GOLD_ACQUISITION_ITEMS, self.writeAddGold))
        
        func = table.get(mid)
        if not func:
            raise CabaretError(u'未実装のアイテムです', CabaretError.Code.UNKNOWN)
        
        self.__before_value = 0
        self.__after_value = 0
        
        errcode = CabaretError.Code.UNKNOWN
        try:
            func(itemmaster, usenum)
            errcode = CabaretError.Code.OK
        except CabaretError,e:
            if e.code == CabaretError.Code.ALREADY_RECEIVED:
                # 既にDBに反映済み.
                errcode = e.code
            elif e.code == CabaretError.Code.OVER_LIMIT:
                # 既にDBに反映済み.
                errcode = e.code
            else:
                raise
        
        # リダイレクト.
        url = UrlMaker.item_usecomplete(mid, errcode, self.__before_num, self.__after_num, self.__before_value, self.__after_value)
        url = self.makeAppLinkUrlRedirect(url)
        self.appRedirect(url)
    
    def tr_consume_item(self, model_mgr, uid, itemmaster, usenum):
        """アイテム消費書き込み.
        """
        BackendApi.tr_add_item(model_mgr, uid, itemmaster.id, -usenum, self.__before_num)
    
    def writeApRecover(self, itemmaster, usenum):
        """体力回復.
        """
        v_player = self.getViewerPlayer()
        model_mgr, player = db_util.run_in_transaction(self.tr_write_aprecover, v_player.id, itemmaster, usenum)
        model_mgr.write_end()
        # 結果に渡す値を設定.
        self.__before_value = v_player.get_ap()
        self.__after_value = player.get_ap()
    
    def tr_write_aprecover(self, uid, itemmaster, usenum):
        """体力回復書き込み.
        """
        model_mgr = ModelRequestMgr()
        # アイテム消費.
        self.tr_consume_item(model_mgr, uid, itemmaster, usenum)
        # 体力加算.
        player = BackendApi.get_players(self, [uid], [PlayerFriend], model_mgr=model_mgr)[0]
        if itemmaster.id == Defines.ItemEffect.ACTION_ALL_RECOVERY:
            # 全回復.
            BackendApi.tr_max_ap(model_mgr, player)
        else:
            # 設定値分回復.
            BackendApi.tr_add_ap(model_mgr, player, itemmaster.evalue * usenum)
        model_mgr.write_all()
        return model_mgr, player
    
    def writeBpRecover(self, itemmaster, usenum):
        """気力回復.
        """
        v_player = self.getViewerPlayer()
        model_mgr, player = db_util.run_in_transaction(self.tr_write_bp_recover, v_player.id, itemmaster, usenum)
        model_mgr.write_end()
        # 結果に渡す値を設定.
        self.__before_value = v_player.get_bp()
        self.__after_value = player.get_bp()
    
    def tr_write_bp_recover(self, uid, itemmaster, usenum):
        """気力回復書き込み.
        """
        model_mgr = ModelRequestMgr()
        # アイテム消費.
        self.tr_consume_item(model_mgr, uid, itemmaster, usenum)
        # 気力加算.
        player = BackendApi.get_players(self, [uid], [PlayerFriend], model_mgr=model_mgr)[0]
        if itemmaster.id == Defines.ItemEffect.TENSION_ALL_RECOVERY:
            # 全回復.
            BackendApi.tr_max_bp(model_mgr, player)
        else:
            # 設定値分回復.
            BackendApi.tr_add_bp(model_mgr, player, itemmaster.evalue * usenum)
        model_mgr.write_all()
        return model_mgr, player
    
    def writeBoxExpansion(self, itemmaster, usenum):
        """BOX拡張.
        """
        v_player = self.getViewerPlayer()
        model_mgr = db_util.run_in_transaction(self.tr_write_box_expansion, v_player.id, itemmaster, usenum)
        model_mgr.write_end()
        # 結果に渡す値を設定.
        self.__before_value = v_player.cardlimit
        v_player.setModel(model_mgr.get_wrote_model(PlayerDeck, v_player.id))
        self.__after_value = v_player.cardlimit
    
    def tr_write_box_expansion(self, uid, itemmaster, usenum):
        """BOX拡張書き込み.
        """
        model_mgr = ModelRequestMgr()
        # アイテム消費.
        self.tr_consume_item(model_mgr, uid, itemmaster, usenum)
        # BOX拡張.
        BackendApi.tr_add_card_limit(model_mgr, uid, itemmaster.evalue * usenum, is_lvup=False)
        model_mgr.write_all()
        return model_mgr
    
    def writeAddGold(self, itemmaster, usenum):
        """キャバゴールド加算.
        """
        v_player = self.getViewerPlayer()
        model_mgr = db_util.run_in_transaction(self.tr_write_add_gold, v_player.id, itemmaster, usenum)
        model_mgr.write_end()
        # 結果に渡す値を設定.
        self.__before_value = v_player.gold
        self.__after_value = self.__before_value  + itemmaster.evalue * usenum
    
    def tr_write_add_gold(self, uid, itemmaster, usenum):
        """キャバゴールド加算書き込み.
        """
        model_mgr = ModelRequestMgr()
        # アイテム消費.
        self.tr_consume_item(model_mgr, uid, itemmaster, usenum)
        # キャバゴールドを加算.
        BackendApi.tr_add_gold(model_mgr, uid, itemmaster.evalue * usenum)
        model_mgr.write_all()
        return model_mgr
    
    def writeAddGachaPoint(self, itemmaster, usenum):
        """引抜Pt加算.
        """
        v_player = self.getViewerPlayer()
        model_mgr = db_util.run_in_transaction(self.tr_write_add_gachapoint, v_player.id, itemmaster, usenum)
        model_mgr.write_end()
        # 結果に渡す値を設定.
        self.__before_value = v_player.gachapt
        self.__after_value = self.__before_value  + itemmaster.evalue * usenum
    
    def tr_write_add_gachapoint(self, uid, itemmaster, usenum):
        """引抜Pt加算書き込み.
        """
        model_mgr = ModelRequestMgr()
        # アイテム消費.
        self.tr_consume_item(model_mgr, uid, itemmaster, usenum)
        # 引抜Ptを加算.
        BackendApi.tr_add_gacha_pt(model_mgr, uid, itemmaster.evalue * usenum)
        model_mgr.write_all()
        return model_mgr

def main(request):
    return Handler.run(request)
