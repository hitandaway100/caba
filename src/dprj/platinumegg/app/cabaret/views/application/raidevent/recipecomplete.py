# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.application.raidevent.base import RaidEventBaseHandler
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from platinumegg.app.cabaret.models.Player import PlayerDeck, PlayerRequest


class Handler(RaidEventBaseHandler):
    """レイドイベント交換結果ページ.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerDeck, PlayerRequest]
    
    def process(self):
        
        args = self.getUrlArgs('/raideventrecipecomplete/')
        recipe_id = args.getInt(0)
        
        trade_num = self.getRecipeTradeNum()
        self.html_param['trade_num'] = trade_num
        
        model_mgr = self.getModelMgr()
        eventmaster = self.getCurrentRaidTicketEvent()
        
        eventid = eventmaster.id
        
        # レシピ.
        recipemaster = None
        if recipe_id:
            recipemaster = BackendApi.get_raidevent_recipemaster(model_mgr, recipe_id, using=settings.DB_READONLY)
        if recipemaster is None or recipemaster.eventid != eventid:
            url = UrlMaker.raidevent_recipe_list()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        
        # レシピのHTMLデータ.
        obj_recipe = BackendApi.make_raidevent_recipe_htmlobj(self, recipemaster)
        self.html_param['recipe'] = obj_recipe
        
        # イベント情報.
        config = BackendApi.get_current_raideventconfig(model_mgr, using=settings.DB_READONLY)
        self.html_param['raidevent'] = Objects.raidevent(self, eventmaster, config)
        
        self.putEventTopic(eventid)
        
        # 交換所TOP.
        url = UrlMaker.raidevent_recipe_list()
        self.html_param['url_raidevent_recipelist'] = self.makeAppLinkUrl(url)
        
        self.writeHtml(eventmaster, 'presenttradecomp')

def main(request):
    return Handler.run(request)
