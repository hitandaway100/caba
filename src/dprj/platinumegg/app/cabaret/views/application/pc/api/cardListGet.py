# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings

class Handler(AppHandler):
    """所持カード.
    """
    
    def process(self):
        
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        viewer_id = v_player.id
        
        deck = BackendApi.get_deck(viewer_id, model_mgr, using=settings.DB_READONLY)
        
        cardsetlist = BackendApi.get_card_list(viewer_id, arg_model_mgr=model_mgr, using=settings.DB_READONLY)
        
        self.json_result_param['cardlist'] = [Objects.card(self, cardset, deck) for cardset in cardsetlist]
        
        self.writeAppJson()
    
def main(request):
    return Handler.run(request)
