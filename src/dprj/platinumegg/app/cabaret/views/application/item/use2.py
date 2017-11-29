# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.models.Player import PlayerAp, PlayerFriend,\
    PlayerDeck, PlayerGold, PlayerGachaPt, PlayerRequest
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from defines import Defines
import settings_sub
import urllib
from platinumegg.app.cabaret.models.Item import Item
from platinumegg.lib.opensocial.util import OSAUtil


class Handler(AppHandler):
    """新アイテム使用書き込み.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerRequest, PlayerAp, PlayerFriend, PlayerDeck, PlayerGold, PlayerGachaPt]
    
    def redirectWithError(self, err, url=None):
        if settings_sub.IS_LOCAL:
            raise err
        elif url is None:
            url = UrlMaker.itemlist()
        self.appRedirect(self.makeAppLinkUrlRedirect(url))
    
    def process(self):
        
#        v_player = self.getViewerPlayer()
        try:
            #if self.is_pc:
            #    mid = int(self.request.get(Defines.URLQUERY_ITEM))
            #    confirmkey = v_player.req_confirmkey
            #else:
            #    args = self.getUrlArgs('/item_use2/')
            #    mid = int(args.get(0))
            #    confirmkey = urllib.unquote(args.get(1))
            args = self.getUrlArgs('/item_use2/')
            mid = int(args.get(0))
            confirmkey = urllib.unquote(args.get(1))
            usenum = int(self.request.get(Defines.URLQUERY_NUMBER) or 1)
        except:
            self.redirectWithError(CabaretError(u'リクエストが正しくありません', CabaretError.Code.ILLEGAL_ARGS))
            return
        
        if not mid in Defines.ItemEffect.USE_ABLE and not mid in Defines.ItemEffect.CABACLUB_STORE_ITEMS:
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
        if num is None or num < usenum:
            # 正しく処理できない.
            url = None
            if num is not None:
                # 所持数情報が間違っているのかもしれないので消しておく.
                url = UrlMaker.item_useyesno(mid)
                model_mgr.delete_models_from_cache(Item, [Item.makeID(v_player.id, mid)])
            self.redirectWithError(CabaretError(u'正しく処理できません出来ませんでした', CabaretError.Code.ILLEGAL_ARGS), url)
            return
        
        self.__before_num = num
        self.__after_num = self.__before_num - usenum
        
        # マスターデータ.
        itemmaster = BackendApi.get_itemmaster(model_mgr, mid, using=settings.DB_READONLY)
        
        # 書き込み.
        table = {
            Defines.ItemEffect.CARD_BOX_EXPANSION : self.writeBoxExpansion,
            Defines.ItemEffect.CABACLUB_SCOUTMAN : self.writeUseCabaClubScoutMan,
            Defines.ItemEffect.CABACLUB_PREFERENTIAL : self.writeUseCabaClubPreferentialItem,
            Defines.ItemEffect.CABACLUB_BARRIER : self.writeUseCabaClubBarrierItem,
        }
        table.update(**dict.fromkeys(Defines.ItemEffect.ACTION_RECOVERY_ITEMS, self.writeApRecover))
        table.update(**dict.fromkeys(Defines.ItemEffect.TENSION_RECOVERY_ITEMS, self.writeBpRecover))
        table.update(**dict.fromkeys(Defines.ItemEffect.GACHA_PT_ACQUISITION_ITEMS, self.writeAddGachaPoint))
        table.update(**dict.fromkeys(Defines.ItemEffect.GOLD_ACQUISITION_ITEMS, self.writeAddGold))
        table.update(**dict.fromkeys(Defines.ItemEffect.SCOUT_GUM_ITEMS, self.writeUseGum))
        
        func = table.get(mid)
        if not func:
            raise CabaretError(u'未実装のアイテムです', CabaretError.Code.UNKNOWN)
        
        self.__before_value = 0
        self.__after_value = 0
        
        errcode = CabaretError.Code.UNKNOWN
        try:
            func(itemmaster, usenum, confirmkey)
            errcode = CabaretError.Code.OK
        except CabaretError,e:
            if e.code == CabaretError.Code.ALREADY_RECEIVED:
                # 既にDBに反映済み.
                errcode = e.code
                self.__after_num = BackendApi.get_item_nums(ModelRequestMgr(), v_player.id, [mid], using=settings.DB_DEFAULT).get(mid, 0)
                self.__before_num = self.__after_num + usenum
            elif e.code == CabaretError.Code.OVER_LIMIT:
                # これ以上使用できない.
                model_mgr.delete_models_from_cache(Item, [Item.makeID(v_player.id, mid)])
                
                errcode = e.code
                self.__before_num = BackendApi.get_item_nums(ModelRequestMgr(), v_player.id, [mid], using=settings.DB_DEFAULT).get(mid, 0)
                self.__after_num = self.__before_num
            else:
                raise
        
        # リダイレクト.
        if mid in Defines.ItemEffect.SCOUT_GUM_ITEMS:
            self.__swf_params = {}
            self.__swf_params['backUrl'] = self.makeAppLinkUrl(UrlMaker.scoutevent())
            self.appRedirectToEffect('scoutevent/fever2/effect.html', self.__swf_params)
        else:
            url = UrlMaker.item_usecomplete(mid, errcode, self.__before_num, self.__after_num, self.__before_value, self.__after_value)
            url = self.makeAppLinkUrlRedirect(url)
            self.appRedirect(url)
    
    def tr_consume_item(self, model_mgr, uid, itemmaster, usenum, confirmkey):
        """アイテム消費書き込み.
        """
        # 重複確認.
        BackendApi.tr_update_requestkey(model_mgr, uid, confirmkey)
        # 消費.
        BackendApi.tr_add_item(model_mgr, uid, itemmaster.id, -usenum)
    
    def writeApRecover(self, itemmaster, usenum, confirmkey):
        """体力回復.
        """
        v_player = self.getViewerPlayer()
        model_mgr, player = db_util.run_in_transaction(self.tr_write_aprecover, v_player.id, itemmaster, usenum, confirmkey)
        model_mgr.write_end()
        # 結果に渡す値を設定.
        self.__before_value = v_player.get_ap()
        self.__after_value = player.get_ap()
    
    def tr_write_aprecover(self, uid, itemmaster, usenum, confirmkey):
        """体力回復書き込み.
        """
        model_mgr = ModelRequestMgr()
        # アイテム消費.
        self.tr_consume_item(model_mgr, uid, itemmaster, usenum, confirmkey)
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
    
    def writeBpRecover(self, itemmaster, usenum, confirmkey):
        """気力回復.
        """
        v_player = self.getViewerPlayer()
        model_mgr, player = db_util.run_in_transaction(self.tr_write_bp_recover, v_player.id, itemmaster, usenum, confirmkey)
        model_mgr.write_end()
        # 結果に渡す値を設定.
        self.__before_value = v_player.get_bp()
        self.__after_value = player.get_bp()
    
    def tr_write_bp_recover(self, uid, itemmaster, usenum, confirmkey):
        """気力回復書き込み.
        """
        model_mgr = ModelRequestMgr()
        # アイテム消費.
        self.tr_consume_item(model_mgr, uid, itemmaster, usenum, confirmkey)
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
    
    def writeBoxExpansion(self, itemmaster, usenum, confirmkey):
        """BOX拡張.
        """
        v_player = self.getViewerPlayer()
        model_mgr = db_util.run_in_transaction(self.tr_write_box_expansion, v_player.id, itemmaster, usenum, confirmkey)
        model_mgr.write_end()
        # 結果に渡す値を設定.
        self.__before_value = v_player.cardlimit
        v_player.setModel(model_mgr.get_wrote_model(PlayerDeck, v_player.id))
        self.__after_value = v_player.cardlimit
    
    def tr_write_box_expansion(self, uid, itemmaster, usenum, confirmkey):
        """BOX拡張書き込み.
        """
        model_mgr = ModelRequestMgr()
        # アイテム消費.
        self.tr_consume_item(model_mgr, uid, itemmaster, usenum, confirmkey)
        # BOX拡張.
        BackendApi.tr_add_card_limit(model_mgr, uid, itemmaster.evalue * usenum, is_lvup=False)
        model_mgr.write_all()
        return model_mgr
    
    def writeAddGold(self, itemmaster, usenum, confirmkey):
        """キャバゴールド加算.
        """
        v_player = self.getViewerPlayer()
        model_mgr = db_util.run_in_transaction(self.tr_write_add_gold, v_player.id, itemmaster, usenum, confirmkey)
        model_mgr.write_end()
        # 結果に渡す値を設定.
        self.__before_value = v_player.gold
        self.__after_value = self.__before_value  + itemmaster.evalue * usenum
    
    def tr_write_add_gold(self, uid, itemmaster, usenum, confirmkey):
        """キャバゴールド加算書き込み.
        """
        model_mgr = ModelRequestMgr()
        # アイテム消費.
        self.tr_consume_item(model_mgr, uid, itemmaster, usenum, confirmkey)
        # キャバゴールドを加算.
        BackendApi.tr_add_gold(model_mgr, uid, itemmaster.evalue * usenum)
        model_mgr.write_all()
        return model_mgr
    
    def writeAddGachaPoint(self, itemmaster, usenum, confirmkey):
        """引抜Pt加算.
        """
        v_player = self.getViewerPlayer()
        model_mgr = db_util.run_in_transaction(self.tr_write_add_gachapoint, v_player.id, itemmaster, usenum, confirmkey)
        model_mgr.write_end()
        # 結果に渡す値を設定.
        self.__before_value = v_player.gachapt
        self.__after_value = self.__before_value  + itemmaster.evalue * usenum
    
    def tr_write_add_gachapoint(self, uid, itemmaster, usenum, confirmkey):
        """引抜Pt加算書き込み.
        """
        model_mgr = ModelRequestMgr()
        # アイテム消費.
        self.tr_consume_item(model_mgr, uid, itemmaster, usenum, confirmkey)
        # 引抜Ptを加算.
        BackendApi.tr_add_gacha_pt(model_mgr, uid, itemmaster.evalue * usenum)
        model_mgr.write_all()
        return model_mgr

    def writeUseGum(self, itemmaster, usenum, confirmkey):
        """スカウトガム使用.
        """
        v_player = self.getViewerPlayer()
        model_mgr = ModelRequestMgr()
        eventmaster = BackendApi.get_current_scouteventmaster(model_mgr, using=settings.DB_READONLY)
        if eventmaster is None:
            raise CabaretError(u'Event Closed.', CabaretError.Code.EVENT_CLOSED)
        playdata = BackendApi.get_event_playdata(model_mgr, eventmaster.id, v_player.id, using=settings.DB_READONLY)
        now = OSAUtil.get_now()
        if now <= playdata.feveretime:
            raise CabaretError(u'Fever time.', CabaretError.Code.OVER_LIMIT)
        
        model_mgr = db_util.run_in_transaction(self.tr_write_use_gum, eventmaster.id, v_player.id, itemmaster, usenum, confirmkey)
        model_mgr.write_end()
        # 結果に渡す値を設定.
        self.__before_value = 0
        self.__after_value = 0
        
    def tr_write_use_gum(self, mid, uid, itemmaster, usenum, confirmkey):
        """スカウトガム使用書き込み.
        """
        model_mgr = ModelRequestMgr()
        # アイテム消費.
        self.tr_consume_item(model_mgr, uid, itemmaster, usenum, confirmkey)
        
        BackendApi.set_scoutevent_fever(model_mgr, mid, uid, itemmaster.evalue)
        
        model_mgr.write_all()
        
        return model_mgr
    
    def writeUseCabaClubScoutMan(self, itemmaster, usenum, confirmkey):
        """スカウトマン追加.
        """
        v_player = self.getViewerPlayer()
        # 店舗.
        cabaclubstoremaster = None
        if Defines.FromPages.CABACLUB_STORE == self.getFromPageName():
            args = self.getFromPageArgs()
            if args:
                cabaclubstoremaster = BackendApi.get_cabaretclub_store_master(self.getModelMgr(), int(args[0]), using=settings.DB_READONLY)
        if cabaclubstoremaster is None:
            raise CabaretError(u'店舗が存在しません', CabaretError.Code.ILLEGAL_ARGS)
        # 書き込み.
        model_mgr = db_util.run_in_transaction(self.tr_write_use_cabaclubscoutman, v_player.id, itemmaster, cabaclubstoremaster, usenum, confirmkey, OSAUtil.get_now())
        model_mgr.write_end()
    
    def tr_write_use_cabaclubscoutman(self, uid, itemmaster, cabaclubstoremaster, usenum, confirmkey, now):
        """優待券配布使用書き込み.
        """
        model_mgr = ModelRequestMgr()
        # アイテム消費.
        self.tr_consume_item(model_mgr, uid, itemmaster, usenum, confirmkey)
        # 優待券配布設定.
        BackendApi.tr_cabaclub_add_scoutman(model_mgr, uid, cabaclubstoremaster, usenum * itemmaster.evalue, now)
        # 書き込み.
        model_mgr.write_all()
        return model_mgr
    
    def writeUseCabaClubPreferentialItem(self, itemmaster, usenum, confirmkey):
        """優待券配布使用.
        """
        v_player = self.getViewerPlayer()
        # 書き込み.
        model_mgr = db_util.run_in_transaction(self.tr_write_use_cabaclubpreferentialitem, v_player.id, itemmaster, confirmkey)
        model_mgr.write_end()
        
    def tr_write_use_cabaclubpreferentialitem(self, uid, itemmaster, confirmkey):
        """優待券配布使用書き込み.
        """
        model_mgr = ModelRequestMgr()
        # アイテム消費.
        self.tr_consume_item(model_mgr, uid, itemmaster, 1, confirmkey)
        # 優待券配布設定.
        BackendApi.tr_cabaclub_set_preferential(model_mgr, uid, itemmaster, OSAUtil.get_now())
        # 書き込み.
        model_mgr.write_all()
        return model_mgr
    
    def writeUseCabaClubBarrierItem(self, itemmaster, usenum, confirmkey):
        """バリアアイテム使用.
        """
        v_player = self.getViewerPlayer()
        # 書き込み.
        model_mgr = db_util.run_in_transaction(self.tr_write_use_cabaclubbarrieritem, v_player.id, itemmaster, confirmkey)
        model_mgr.write_end()
        
    def tr_write_use_cabaclubbarrieritem(self, uid, itemmaster, confirmkey):
        """バリアアイテム使用書き込み.
        """
        model_mgr = ModelRequestMgr()
        # アイテム消費.
        self.tr_consume_item(model_mgr, uid, itemmaster, 1, confirmkey)
        # バリアアイテム設定.
        BackendApi.tr_cabaclub_set_barrier(model_mgr, uid, itemmaster, OSAUtil.get_now())
        # 書き込み.
        model_mgr.write_all()
        return model_mgr

def main(request):
    return Handler.run(request)
