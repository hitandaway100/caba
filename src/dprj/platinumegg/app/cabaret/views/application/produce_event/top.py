# -*- coding: utf-8 -*-

from platinumegg.app.cabaret.views.application.produce_event.base import ProduceEventBaseHandler
from platinumegg.app.cabaret.util.api import BackendApi, Objects
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.models.View import CardMasterView
from platinumegg.app.cabaret.util.card import CardUtil
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from defines import Defines
import settings
from platinumegg.app.cabaret.models.produce_event.ProduceEvent import ProduceEventScore
from platinumegg.app.cabaret.util.redisdb import ProduceEventRanking

class Handler(ProduceEventBaseHandler):
    """プロデュースイベントTOP
    """

    def process(self):
        model_mgr = self.getModelMgr()

        event_config = BackendApi.get_current_produce_event_config(model_mgr, using=settings.DB_READONLY)

        args = self.getUrlArgs('/produceeventtop/')
        mid = args.getInt(0)
        eventmaster = None

        if not mid and event_config:
            mid = event_config.mid

        if mid:
            eventmaster = BackendApi.get_produce_event_master(model_mgr, mid, using=settings.DB_READONLY)

        if not eventmaster:
            raise CabaretError(u'Event Closed.', CabaretError.Code.EVENT_CLOSED)

        cur_eventmaster = self.getCurrentProduceEvent(quiet=True)
        is_open = cur_eventmaster and cur_eventmaster.id == mid
        v_player = self.getViewerPlayer()
        uid = v_player.id

        if is_open:
            # 発生中のレイド情報.
            happeningraidset = self.getHappeningRaidSet()
            happeningset = None
            if happeningraidset:
                happeningset = happeningraidset.happening
            if happeningset:
                # レイドがある.
                if (happeningset.happening.is_cleared()):
                    # 未確認の結果がある.
                    url = UrlMaker.raidresultanim(happeningset.id)
                    self.appRedirect(self.makeAppLinkUrlRedirect(url))
                    return
                elif not happeningset.happening.is_end():
                    obj_happening = Objects.producehappening(self, happeningraidset)
                    obj_happening['url_battlepre'] = self.makeAppLinkUrl(UrlMaker.produceevent_battlepre())
                    self.html_param['producehappening'] = obj_happening

            # デッキ編成へのリンクを上書き.
            self.setFromPage(Defines.FromPages.PRODUCEEVENT)
            self.html_param['url_deck_raid'] = self.makeAppLinkUrl(UrlMaker.deck_raid())
        # イベント情報.
        self.html_param['produceevent'] = Objects.produceevent(self, eventmaster, event_config)

        # ルール、説明とランキングのリンク.
        self.putEventTopic(mid, 'top')
        
        self.html_param['produce_card'] = BackendApi.create_produce_cardinfo(self, model_mgr, uid, eventmaster.id)
        
        # イベント専用スカウトのTOPページへのリンク.
        self.html_param['url_produceevent_scouttop'] = self.makeAppLinkUrl(UrlMaker.produceevent_scouttop())
        
        produce_score = ProduceEventScore.get_instance(model_mgr, uid, eventmaster.id, using=settings.DB_READONLY)
        self.html_param['produce_eventscore'] = produce_score.to_dict()

        self.html_param['produce_rank'] = BackendApi.get_ranking_rank(ProduceEventRanking, eventmaster.id, uid)
        
        self.html_param['shop_url'] = self.makeAppLinkUrl(UrlMaker.shop())
        
        # HTML 作成
        self.writeAppHtml('produce_event/top')

def main(request):
    return Handler.run(request)
