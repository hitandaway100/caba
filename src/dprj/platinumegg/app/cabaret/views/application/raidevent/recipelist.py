# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.application.raidevent.base import RaidEventBaseHandler
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from defines import Defines
from platinumegg.app.cabaret.models.Player import PlayerDeck


class Handler(RaidEventBaseHandler):
    """レイドイベント交換一覧ページ.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerDeck]
    
    def process(self):
        
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
        
        # レシピを取得.
        recipe_idlist = BackendApi.get_raidevent_recipeid_by_eventid(model_mgr, eventid, using=settings.DB_READONLY)
        recipelist = BackendApi.get_raidevent_recipemaster_list(model_mgr, recipe_idlist, using=settings.DB_READONLY)
        
        # レシピ毎の交換回数.
        mixdata_dict = BackendApi.get_raidevent_mixdata_dict(model_mgr, uid, recipe_idlist, using=settings.DB_READONLY)
        
        # カード所持数.
        cardnum = BackendApi.get_cardnum(uid, model_mgr, using=settings.DB_READONLY)
        cardrest = v_player.cardlimit - cardnum
        self.html_param['is_cardnum_max'] = cardrest < 1
        
        # HTML用のObjectを作成.
        obj_recipelist = []
        for recipemaster in recipelist:
            err_mess = None
            
            mixdata = mixdata_dict.get(recipemaster.id)
            
            obj_recipe = BackendApi.make_raidevent_recipe_htmlobj(self, recipemaster, mixdata)
            
            # 最大交換可能数.
            trade_max = None
            if recipemaster.itype == Defines.ItemType.CARD:
                card_trade_max = int(cardrest / recipemaster.itemnum)
                if card_trade_max < 1:
                    err_mess = u'所属キャストが上限を超えます'
                trade_max = min(Defines.ItemType.TRADE_NUM_MAX.get(recipemaster.itype, card_trade_max), card_trade_max)
            elif Defines.ItemType.TRADE_NUM_MAX.has_key(recipemaster.itype):
                trade_max = Defines.ItemType.TRADE_NUM_MAX[recipemaster.itype]
            obj_recipe['trade_max'] = trade_max
            obj_recipe['err_mess'] = err_mess
            
            obj_recipelist.append(obj_recipe)
        self.html_param['recipelist'] = obj_recipelist
        
        self.putEventTopic(eventid)
        
        self.writeHtml(eventmaster, 'presenttrade')
    

def main(request):
    return Handler.run(request)
