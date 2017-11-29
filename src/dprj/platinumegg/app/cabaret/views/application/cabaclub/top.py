# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.application.cabaclub import CabaClubHandler
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from defines import Defines
from platinumegg.app.cabaret.models.CabaretClubEvent import CabaClubRankEventMaster

class Handler(CabaClubHandler):
    """キャバクラ経営Top.
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
        if BackendApi.check_cabaclub_lead_resultanim(model_mgr, uid, now, using=settings.DB_READONLY):
            # 結果演出へ.
            self.setFromPage(Defines.FromPages.CABACLUB_STORE)
            self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.cabaclubresultanim()))
            return
        # 経営情報.
        scoredata = BackendApi.get_cabaretclub_scoreplayerdata(model_mgr, uid, using=settings.DB_READONLY)
        scoredata_weekly = BackendApi.get_cabaretclub_scoreplayerdata_weekly(model_mgr, uid, now, using=settings.DB_READONLY)
        obj_cabaclub_management_info = Objects.cabaclub_management_info(self, scoredata, scoredata_weekly)
        # 店舗のイベント発生情報.
        BackendApi.put_cabaretclub_eventinfo(self, uid, now, using=settings.DB_READONLY)
        # 次の集計時間.
        section_endtime = BackendApi.to_cabaretclub_section_endtime(now)

        # 開催中または最新の開催したイベントの開催情報
        event_config = BackendApi.get_current_cabaclubrankeventconfig(model_mgr, using=settings.DB_READONLY)
        if BackendApi.is_cabaclubrankevent_open(model_mgr):
            # 経営イベントのランキングURL
            cabaclub_event_ranking_url = UrlMaker.cabaclubrank(event_config.mid)
        else:
            cabaclub_event_ranking_url = UrlMaker.cabaclubrank(event_config.previous_mid)

        
        self.set_event_period(model_mgr, self.html_param, event_config)
        if self.html_param['is_event_open']:
            self.html_param['eventmaster'] = BackendApi.get_cabaclubrankeventmaster(model_mgr, event_config.mid, using=settings.DB_READONLY)

        # HTML書き込み.
        self.html_param.update(
            cabaclub_management_info = obj_cabaclub_management_info,
            url_store = self.makeAppLinkUrl(UrlMaker.cabaclubstore()),
            url_title = self.makeAppLinkUrl(UrlMaker.titletop()),
            url_current_week_rank = self.makeAppLinkUrl(cabaclub_event_ranking_url),
            section_timelimit = Objects.timelimit(section_endtime, now),
        )
        self.writeAppHtml('cabaclub/top')

def main(request):
    return Handler.run(request)
