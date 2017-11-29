# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from defines import Defines

class Handler(AppHandler):
    """デッキ.
    """
    
    def process(self):
        
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        
        try:
            oid = int(self.request.get(Defines.URLQUERY_ID) or v_player.id)
        except:
            raise CabaretError(u'不正なアクセスです', CabaretError.Code.ILLEGAL_ARGS)
        
        deck = BackendApi.get_deck(oid, model_mgr, using=settings.DB_READONLY)
        
        cardidlist = deck.to_array()
        
        cardsetlist = BackendApi.get_cards(cardidlist, arg_model_mgr=model_mgr, using=settings.DB_READONLY)
        
        self.json_result_param['cardlist'] = [Objects.card(self, cardset, deck) for cardset in cardsetlist]
        
        self.writeAppJson()
    
def main(request):
    return Handler.run(request)
