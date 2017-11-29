# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.application.raidevent.base import RaidEventBaseHandler
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from defines import Defines
from platinumegg.app.cabaret.models.Player import PlayerDeck, PlayerRequest
from platinumegg.lib.opensocial.util import OSAUtil


class Handler(RaidEventBaseHandler):
    """レイドイベント交換確認ページ.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerDeck, PlayerRequest]
    
    def process(self):
        
        args = self.getUrlArgs('/raideventrecipeyesno/')
        recipe_id = args.getInt(0)
        
        trade_num = self.getRecipeTradeNum(include_all=True)
        if trade_num < 0:
            return
        
        model_mgr = self.getModelMgr()
        eventmaster = self.getCurrentRaidTicketEvent()
        
        v_player = self.getViewerPlayer()
        uid = v_player.id
        eventid = eventmaster.id
        
        # 素材のマスターデータを取得.
        material_htmldata = self.putMaterialHtml()
        if not material_htmldata:
            url = UrlMaker.raidevent_top(eventid)
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        
        # レシピ.
        recipemaster = None
        if recipe_id:
            recipemaster = BackendApi.get_raidevent_recipemaster(model_mgr, recipe_id, using=settings.DB_READONLY)
        if recipemaster is None or recipemaster.eventid != eventid:
            url = UrlMaker.raidevent_recipe_list()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        
        # レシピの交換回数.
        mixdata = BackendApi.get_raidevent_mixdata(model_mgr, uid, recipe_id, using=settings.DB_READONLY)
        
        # レシピのHTMLデータ.
        obj_recipe = BackendApi.make_raidevent_recipe_htmlobj(self, recipemaster, mixdata)
        self.html_param['recipe'] = obj_recipe
        
        # 在庫数.
        trade_max = (recipemaster.stock - obj_recipe['trade_cnt']) if 0 < recipemaster.stock else None
        
        # 素材数を確認.
        for i in xrange(Defines.RAIDEVENT_MATERIAL_KIND_MAX):
            need_num = obj_recipe['materialnum%d' % i]
            if need_num == 0:
                continue
            material = material_htmldata.get(i)
            material_num = material['num'] if material else 0
            trade_max_per_material = int(material_num / need_num)
            trade_max = min(trade_max, trade_max_per_material) if trade_max is not None else trade_max_per_material
        
        if trade_max is None:
            url = UrlMaker.raidevent_recipe_list()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        
        # タイプごとの最大交換可能数.
        if recipemaster.itype == Defines.ItemType.CARD:
            cardnum = BackendApi.get_cardnum(uid, model_mgr, using=settings.DB_READONLY)
            cardrest = v_player.cardlimit - cardnum
            card_trade_max = int(cardrest / recipemaster.itemnum)
            trade_max = min(trade_max, Defines.ItemType.TRADE_NUM_MAX.get(recipemaster.itype, card_trade_max), card_trade_max)
        elif Defines.ItemType.TRADE_NUM_MAX.has_key(recipemaster.itype):
            trade_max = min(trade_max, Defines.ItemType.TRADE_NUM_MAX[recipemaster.itype])
        obj_recipe['trade_max'] = trade_max
        
        if trade_num == Defines.TradeNumChoices.ALL:
            trade_num = trade_max
        
        if trade_max < 1 or trade_max < trade_num:
            url = UrlMaker.raidevent_recipe_list()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        
        self.putEventTopic(eventid)
        
        # 交換.
        url = UrlMaker.raidevent_recipe_do(recipe_id, v_player.req_confirmkey)
        url = OSAUtil.addQuery(url, Defines.URLQUERY_NUMBER, trade_num)
        self.html_param['url_raidevent_recipedo'] = self.makeAppLinkUrl(url)
        
        # キャンセル.
        url = UrlMaker.raidevent_recipe_list()
        self.html_param['url_raidevent_recipelist'] = self.makeAppLinkUrl(url)
        
        self.html_param['trade_num'] = trade_num
        
        self.writeHtml(eventmaster, 'presenttradeyesno')

def main(request):
    return Handler.run(request)
