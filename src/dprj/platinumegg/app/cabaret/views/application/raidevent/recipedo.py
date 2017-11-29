# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.application.raidevent.base import RaidEventBaseHandler
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from defines import Defines
from platinumegg.app.cabaret.models.Player import PlayerDeck,\
    PlayerGold, PlayerGachaPt, PlayerKey
import urllib
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.cabareterror import CabaretError
import settings_sub
from platinumegg.lib.opensocial.util import OSAUtil


class Handler(RaidEventBaseHandler):
    """レイドイベント交換書き込み.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerDeck]
    
    def process(self):
        
        args = self.getUrlArgs('/raideventrecipedo/')
        recipe_id = args.getInt(0)
        confirm_key = urllib.unquote(args.get(1))
        
        trade_num = self.getRecipeTradeNum()
        if not trade_num:
            return
        
        model_mgr = self.getModelMgr()
        eventmaster = self.getCurrentRaidTicketEvent()
        
        v_player = self.getViewerPlayer()
        uid = v_player.id
        eventid = eventmaster.id
        
        # レシピ.
        recipemaster = None
        if recipe_id:
            recipemaster = BackendApi.get_raidevent_recipemaster(model_mgr, recipe_id, using=settings.DB_READONLY)
        if recipemaster is None or recipemaster.eventid != eventid:
            url = UrlMaker.raidevent_recipe_list()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        
        if recipemaster.itype == Defines.ItemType.CARD:
            cardnum = BackendApi.get_cardnum(uid, model_mgr, using=settings.DB_READONLY)
            cardrest = v_player.cardlimit - cardnum
            card_trade_max = int(cardrest / recipemaster.itemnum)
            if card_trade_max < trade_num:
                url = UrlMaker.raidevent_recipe_list()
                self.appRedirect(self.makeAppLinkUrlRedirect(url))
                return
        
        try:
            model_mgr = db_util.run_in_transaction(self.tr_write, uid, eventmaster, recipemaster, trade_num, confirm_key)
            model_mgr.write_end()
        except CabaretError, err:
            if settings_sub.IS_LOCAL:
                raise
            elif err.code == CabaretError.Code.ALREADY_RECEIVED:
                pass
            else:
                url = UrlMaker.raidevent_recipe_yesno(recipe_id)
                self.appRedirect(self.makeAppLinkUrlRedirect(url))
                return
        
        # 結果ページヘ.
        url = UrlMaker.raidevent_recipe_complete(recipe_id)
        url = OSAUtil.addQuery(url, Defines.URLQUERY_NUMBER, trade_num)
        self.appRedirect(self.makeAppLinkUrlRedirect(url))
    
    def tr_write(self, uid, eventmaster, recipemaster, trade_num, requestkey):
        """書き込み.
        """
        model_mgr = ModelRequestMgr()
        player = BackendApi.get_players(self, [uid], [PlayerDeck, PlayerGold, PlayerGachaPt, PlayerKey], model_mgr=model_mgr)[0]
        BackendApi.tr_raidevent_trade_item(model_mgr, player, eventmaster, recipemaster, trade_num, requestkey)
        model_mgr.write_all()
        return model_mgr

def main(request):
    return Handler.run(request)
