# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.models.Player import PlayerKey, PlayerDeck
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from defines import Defines
import settings
from platinumegg.app.cabaret.views.application.treasure.base import TreasureHandler

class Handler(TreasureHandler):
    """宝箱所持リスト.
    表示するもの.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerKey, PlayerDeck]
    
    def process(self):
        try:
            args = self.getUrlArgs('/treasurelist/')
            ttype = int(args.get(0, Defines.TreasureType.GOLD))
            if not Defines.TreasureType.NAMES.has_key(ttype):
                raise CabaretError()
            do_check_all = self.request.get(Defines.URLQUERY_FLAG) != "1"
        except:
            raise CabaretError(u'リクエストが正しくありません', CabaretError.Code.ILLEGAL_ARGS)
        
        self.putTreasureListParams(ttype, do_check_all=do_check_all)
        
        model_mgr = self.getModelMgr()
        
        # サムネ一覧.
        tablemasterlist = BackendApi.get_public_treasuretablemaster_list(model_mgr, ttype, using=settings.DB_READONLY)
        self.html_param['thumbnaillist'] = [self.makeAppLinkUrlImg(tablemaster.thumb) for tablemaster in tablemasterlist]
        
        self.writeAppHtml('treasure/list')
    

def main(request):
    return Handler.run(request)
