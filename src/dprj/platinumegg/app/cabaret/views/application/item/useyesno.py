# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from defines import Defines
from platinumegg.app.cabaret.models.Player import PlayerAp, PlayerFriend,\
    PlayerDeck, PlayerRequest
import settings_sub
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.cabaclub_store import CabaclubStoreSet


class Handler(AppHandler):
    """アイテム使用確認.
    表示するもの.
        使用するアイテム情報.
        使用確認へのURL.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerAp, PlayerFriend, PlayerDeck, PlayerRequest]
    
    def process(self):
        args = self.getUrlArgs('/item_useyesno/')
        try:
            mid = int(args.get(0))
            use_num = int(self.request.get(Defines.URLQUERY_NUMBER, 1))
            if use_num < 1:
                raise CabaretError()
        except:
            raise CabaretError(u'リクエストが正しくありません', CabaretError.Code.ILLEGAL_ARGS)
        
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        # 使用するアイテム情報.
        num = BackendApi.get_item_nums(model_mgr, v_player.id, [mid], using=settings.DB_READONLY).get(mid, 0)
        if num < 1:
            # 手に入れたことすらない.
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'リクエストが正しくありません', CabaretError.Code.ILLEGAL_ARGS)
            url = UrlMaker.itemlist()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        
        master = BackendApi.get_itemmaster(model_mgr, mid, using=settings.DB_READONLY)
        self.html_param['item'] = Objects.item(self, master, num)
        self.html_param['use_num'] = use_num
        
        if num < use_num:
            self.html_param['is_not_enough'] = True
        elif mid in Defines.ItemEffect.ACTION_RECOVERY_ITEMS:
            if v_player.get_ap() == v_player.get_ap_max():
                self.html_param['is_overlimit'] = True
        # テンション全回復.
        elif mid in Defines.ItemEffect.TENSION_RECOVERY_ITEMS:
            if v_player.get_bp() == v_player.get_bp_max():
                self.html_param['is_overlimit'] = True
            
        elif mid == Defines.ItemEffect.CARD_BOX_EXPANSION:
            if Defines.CARDLIMITITEM_MAX < (v_player.cardlimititem + master.evalue):
                self.html_param['is_overlimit'] = True
        elif mid in Defines.ItemEffect.SCOUT_GUM_ITEMS:
            eventmaster = BackendApi.get_current_scouteventmaster(model_mgr, using=settings.DB_READONLY)
            if eventmaster is None:
                self.html_param['is_noevent'] = True
            else:
                playdata = BackendApi.get_event_playdata(model_mgr, eventmaster.id, v_player.id, using=settings.DB_READONLY)
                now = OSAUtil.get_now()
                if now <= playdata.feveretime:
                    self.html_param['is_fever'] = True
        elif mid == Defines.ItemEffect.CABACLUB_SCOUTMAN:
            # 店舗.
            cabaclubstoremaster = None
            if Defines.FromPages.CABACLUB_STORE == self.getFromPageName():
                args = self.getFromPageArgs()
                if args:
                    cabaclubstoremaster = BackendApi.get_cabaretclub_store_master(model_mgr, int(args[0]), using=settings.DB_READONLY)
            if cabaclubstoremaster is None:
                raise CabaretError(u'店舗が存在しません', CabaretError.Code.ILLEGAL_ARGS)
            playerdata = BackendApi.get_cabaretclub_storeplayerdata(model_mgr, v_player.id, cabaclubstoremaster.id, using=settings.DB_READONLY)
            storeset = CabaclubStoreSet(cabaclubstoremaster, playerdata)
            if not storeset.is_alive(OSAUtil.get_now()):
                self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.cabaclubstore(cabaclubstoremaster.id)))
                return
            # 使用可能にする.
            self.html_param['item']['master']['useable'] = True
            # 残りを確認.
            rest = cabaclubstoremaster.scoutman_add_max - storeset.playerdata.scoutman_add
            if rest < (master.evalue * use_num):
                self.html_param['is_overlimit'] = True
        elif mid == Defines.ItemEffect.CABACLUB_PREFERENTIAL:
            itemdata = BackendApi.get_cabaretclub_item_playerdata(model_mgr, v_player.id, using=settings.DB_READONLY)
            storeset = CabaclubStoreSet(None, None, itemdata=itemdata)
            if storeset.get_current_preferential_item_id(OSAUtil.get_now()) == mid:
                self.html_param['is_overlimit'] = True
        elif mid == Defines.ItemEffect.CABACLUB_BARRIER:
            itemdata = BackendApi.get_cabaretclub_item_playerdata(model_mgr, v_player.id, using=settings.DB_READONLY)
            storeset = CabaclubStoreSet(None, None, itemdata=itemdata)
            if storeset.get_current_barrier_item_id(OSAUtil.get_now()) == mid:
                self.html_param['is_overlimit'] = True
        
        # アイテム結果URLを取得.
#        url = OSAUtil.addQuery(UrlMaker.item_use(mid, num), Defines.URLQUERY_NUMBER, use_num)
        url = OSAUtil.addQuery(UrlMaker.item_use2(mid, v_player.req_confirmkey), Defines.URLQUERY_NUMBER, use_num)
        self.html_param['url_use'] = self.makeAppLinkUrl(url)
        
        self.putFromBackPageLinkUrl()
        
        if mid in Defines.ItemEffect.SCOUT_GUM_ITEMS:
            eventmaster = BackendApi.get_current_scouteventmaster(model_mgr, using=settings.DB_READONLY)
            if eventmaster is not None:
                self.html_param['url_scoutevent_scouttop'] = self.makeAppLinkUrl(UrlMaker.scoutevent())
        
        self.writeAppHtml('item/useyesno')

def main(request):
    return Handler.run(request)
