# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.application.gacha.base import GachaHandler
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from defines import Defines
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.models.Gacha import GachaBoxResetPlayerData
import urllib

class Handler(GachaHandler):
    """引抜BOXリセット.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        # ガチャのトピック.
        
        # チェックの確認.
        flag = self.request.get(Defines.URLQUERY_ACCEPT) == '1'
        if not flag:
            # ユーザーが承認していない.
            pass
        else:
            model_mgr = self.getModelMgr()
            v_player = self.getViewerPlayer()
            uid = v_player.id

            req_args = self.getUrlArgs('/gachaboxreset/')
            confirmkey = urllib.unquote(req_args.get(0))
            
            # BoxID.
            box_id = str(self.request.get(Defines.URLQUERY_ID) or '')
            box_playdata = None
            if box_id and box_id.isdigit():
                box_id = int(box_id)
                box_playdata = BackendApi.get_gachaplaydata(model_mgr, uid, [box_id]).get(box_id)
            
            if box_playdata is None or not box_playdata.counts:
                # リセット済み.
                pass
            else:
                # 書き込み.
                Handler.write(uid, box_id, confirmkey)
        topic = self.request.get(Defines.URLQUERY_CTYPE) or Defines.GachaConsumeType.GachaTopTopic.PAYMENT
        url = OSAUtil.addQuery(UrlMaker.gacha(), Defines.URLQUERY_CTYPE, topic)
        url = OSAUtil.addQuery(url, Defines.URLQUERY_GTYPE, self.request.get(Defines.URLQUERY_GTYPE))
        url = OSAUtil.addQuery(url, Defines.URLQUERY_GTAB, self.request.get(Defines.URLQUERY_GTAB))
        self.appRedirect(self.makeAppLinkUrlRedirect(url))
    
    @staticmethod
    def write(uid, box_id, confirmkey):
        model_mgr = db_util.run_in_transaction(Handler.tr_write, uid, box_id, confirmkey)
        model_mgr.write_end()
    
    @staticmethod
    def tr_write(uid, box_id, confirmkey):
        """ボックスの中身をリセット.
        """
        model_mgr = ModelRequestMgr()
        BackendApi.tr_reset_gachaboxplaydata(model_mgr, uid, box_id, confirmkey)
        model_mgr.write_all()
        return model_mgr
    

def main(request):
    return Handler.run(request)
