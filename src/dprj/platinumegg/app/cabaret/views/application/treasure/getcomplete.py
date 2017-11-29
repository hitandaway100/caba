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
        args = self.getUrlArgs('/treasuregetcomplete/')
        midlist = None
        try:
            str_idlist = self.request.get(Defines.URLQUERY_ID)
            ttype = int(args.get(0))
            if str_idlist:
                midlist = [int(str_getid) for str_getid in str_idlist.split(',') if str_getid]
            else:
                midlist = [int(args.get(1))]
            if not Defines.TreasureType.NAMES.has_key(ttype) or not midlist or Defines.TreasureType.POOL_LIMIT[ttype] < len(midlist):
                raise CabaretError()
        except:
            raise CabaretError(u'リクエストが正しくありません', CabaretError.Code.ILLEGAL_ARGS)
        
        model_mgr = self.getModelMgr()
        
        # 宝箱のデータ
        treasuremaster_dict = BackendApi.get_treasuremaster_dict(model_mgr, ttype, midlist, using=settings.DB_READONLY)
        
        obj_treasure_list = []
        infos = {}
        for mid in midlist:
            treasuremaster = treasuremaster_dict.get(mid)
            if treasuremaster is None:
                raise CabaretError(u'宝箱のマスターデータが存在しません', CabaretError.Code.NOT_DATA)
            if not infos.has_key(mid):
                infos[mid] = BackendApi.make_treasureiteminfo_list(self, [treasuremaster])[0]
            obj_treasure_list.append(infos[mid])
        self.html_param['treasure_get_data_list'] = obj_treasure_list
        
        # 持っている宝箱.
        self.putTreasureListParams(ttype, do_check_all=False, using=settings.DB_DEFAULT)
        
        self.writeAppHtml('treasure/opend')

def main(request):
    return Handler.run(request)
