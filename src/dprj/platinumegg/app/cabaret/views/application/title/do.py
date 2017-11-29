# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.application.cabaclub import CabaClubHandler
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.cabareterror import CabaretError

class Handler(CabaClubHandler):
    """称号交換書き込み.
    """
    def process(self):
        # 現在時刻.
        now = OSAUtil.get_now()
        # ModelRequestMgr.
        model_mgr = self.getModelMgr()
        # 交換する称号.
        args = self.getUrlArgs('/titledo/')
        mid = args.getInt(0)
        master = BackendApi.get_title_master(model_mgr, mid, using=settings.DB_READONLY) if mid else None
        if master is None:
            self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.titletop()))
            return
        # ユーザ情報.
        v_player = self.getViewerPlayer()
        uid = v_player.id
        # 書き込み.
        try:
            db_util.run_in_transaction(self.tr_write, uid, master, now)
        except CabaretError, err:
            if err.code == CabaretError.Code.ALREADY_RECEIVED:
                pass
            elif err.code == CabaretError.Code.ILLEGAL_ARGS:
                self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.titletop()))
                return
            else:
                raise
        # 書き込み結果のURL.
        url = UrlMaker.titleend(mid)
        self.appRedirect(self.makeAppLinkUrlRedirect(url))
    
    def tr_write(self, uid, titlemaster, now):
        model_mgr = ModelRequestMgr()
        BackendApi.tr_title_get(model_mgr, uid, titlemaster, now)
        model_mgr.write_all()
        model_mgr.write_end()

def main(request):
    return Handler.run(request)
