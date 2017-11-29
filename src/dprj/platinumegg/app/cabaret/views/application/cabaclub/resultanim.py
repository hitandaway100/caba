# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.application.cabaclub import CabaClubHandler
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.url_maker import UrlMaker
import datetime
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.models.CabaretClub import CabaClubScorePlayerDataWeekly
from platinumegg.app.cabaret.util import db_util
from defines import Defines
from random import randint

class Handler(CabaClubHandler):
    """キャバクラ経営結果演出.
    """
    def process(self):
        # 現在時刻.
        now = OSAUtil.get_now()
        # 各店舗の更新.
        self.updateStore(now)
        # ModelRequestMgr.
        model_mgr = self.getModelMgr()
        # ユーザ情報.
        v_player = self.getViewerPlayer()
        uid = v_player.id
        # 経営情報.
        scoredata_weekly = BackendApi.get_cabaretclub_scoreplayerdata_weekly(model_mgr, uid, now - datetime.timedelta(days=7))
        if scoredata_weekly is None:
            self.appRedirect(self.makeAppLinkUrl(UrlMaker.mypage()))
            return
        elif not scoredata_weekly.view_result:
            # 閲覧フラグの更新.
            db_util.run_in_transaction(self.tr_write, uid, scoredata_weekly.id)
        # 演出用パラメータ.
        if self.getFromPageName() == Defines.FromPages.CABACLUB_STORE:
            url = UrlMaker.cabaclubtop()
        else:
            url = UrlMaker.mypage()
        params = dict(
            backUrl = self.makeAppLinkUrl(url),
            proceeds = scoredata_weekly.proceeds,
            customer = scoredata_weekly.customer,
            cast = randint(0, 2),
        )
        self.appRedirectToEffect('cb_system/result/effect.html', params)
    
    def tr_write(self, uid, scoredata_weekly_id):
        """閲覧フラグの更新.
        """
        model_mgr = ModelRequestMgr()
        ins = model_mgr.get_model_forupdate(CabaClubScorePlayerDataWeekly, scoredata_weekly_id)
        ins.view_result = True
        model_mgr.set_save(ins, ['view_result'])
        model_mgr.write_all()
        model_mgr.write_end()
        return ins

def main(request):
    return Handler.run(request)
