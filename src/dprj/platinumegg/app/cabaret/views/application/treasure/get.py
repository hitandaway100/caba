# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from defines import Defines
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
import settings_sub
from platinumegg.lib.opensocial.util import OSAUtil


class Handler(AppHandler):
    """宝箱所持リスト.
    表示するもの.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        
        getidlist = None
        try:
            str_idlist = self.request.get(Defines.URLQUERY_ID)
            
            args = self.getUrlArgs('/treasureget/')
            ttype = int(args.get(0))
            if str_idlist:
                getidlist = [int(str_getid) for str_getid in str_idlist.split(',') if str_getid]
            else:
                getidlist = [int(args.get(1))]
            if not Defines.TreasureType.NAMES.has_key(ttype) or not getidlist or Defines.TreasureType.POOL_LIMIT[ttype] < len(getidlist):
                raise CabaretError()
        except:
            raise CabaretError(u'リクエストが正しくありません', CabaretError.Code.ILLEGAL_ARGS)
        
        model_mgr = self.getModelMgr()
        
        # プレイヤー情報.
        v_player = self.getViewerPlayer()
        
        try:
            model_mgr, treasuresetlist = db_util.run_in_transaction(self.tr_write_get_treasure, v_player.id, ttype, getidlist)
            model_mgr.write_end()
        except CabaretError, err:
            if settings_sub.IS_LOCAL:
                raise
            elif err.code == CabaretError.Code.ALREADY_RECEIVED:
                # 受取済み.
                treasuresetlist = BackendApi.get_treasureset_list(model_mgr, ttype, getidlist, deleted=True)
            else:
                url = UrlMaker.treasurelist(ttype)
                self.appRedirect(self.makeAppLinkUrlRedirect(url))
                return
        
        str_treasuremidlist = [str(treasureset.master.id) for treasureset in treasuresetlist]
        # リダイレクト.
        url = UrlMaker.treasuregetcomplete(ttype)
        url = OSAUtil.addQuery(url, Defines.URLQUERY_ID, ','.join(str_treasuremidlist))
        url = self.makeAppLinkUrlRedirect(url)
        self.appRedirect(url)
    
    @staticmethod
    def tr_write_get_treasure(uid, ttype, getidlist):
        """宝箱書き込み.
        """
        model_mgr = ModelRequestMgr()
        treasuresetlist = BackendApi.tr_open_treasure(model_mgr, uid, ttype, getidlist)
        model_mgr.write_all()
        return [model_mgr, treasuresetlist]
    

def main(request):
    return Handler.run(request)
