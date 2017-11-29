# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.util.api import BackendApi, Objects
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.views.application.produce_happening.base import HappeningHandler
from platinumegg.lib.opensocial.util import OSAUtil
from defines import Defines
import settings
import settings_sub

class ProduceEventBaseHandler(HappeningHandler):
    """プロデュースイベントのベースハンドラ
    """

    CONTENT_NUM_MAX_PER_PAGE = 10

    def preprocess(self):
        HappeningHandler.preprocess(self)
        self.__current_event = None
        self.__current_event_flagrecord = None
        self.html_param['url_produceevent_top'] = self.makeAppLinkUrl(UrlMaker.produceevent_top())
        self.html_param['url_sp_gacha'] = self.makeAppLinkUrl('/gacha?_gtype=stepup')

    def processAppError(self, err):
        if err.code == CabaretError.Code.EVENT_CLOSED:
            url = UrlMaker.mypage()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        AppHandler.processAppError(self, err)

    def getCurrentProduceEvent(self, quiet=False, check_schedule=True):
        """現在発生中のプロデュースイベント.
        """
        if self.__current_event is None:
            model_mgr = self.getModelMgr()
            self.__current_event = BackendApi.get_current_produce_event_master(model_mgr, using=settings.DB_READONLY, check_schedule=check_schedule)
            if self.__current_event is None and not quiet:
                raise CabaretError(u'Event Closed.', CabaretError.Code.EVENT_CLOSED)
        return self.__current_event

    def putEventTopic(self, mid, cur_topic='top'):
        """eventbase.htmlのトピック用のパラメータを埋め込む.
        """
        self.html_param['cur_topic'] = cur_topic

        # イベント説明のURL.
        url = UrlMaker.produceevent_explain(mid, ope='detail')
        self.html_param['url_produceevent_explain_detail'] = self.makeAppLinkUrl(url)

        # イベント報酬一覧のURL.
        url = UrlMaker.produceevent_explain(mid, ope='prizes')
        self.html_param['url_produceevent_explain_prizes'] = self.makeAppLinkUrl(url)

        # ランキングのURL.
        url = UrlMaker.produceevent_explain(mid, ope='ranking')
        self.html_param['url_produceevent_explain_ranking'] = self.makeAppLinkUrl(url)

        # 特効キャスト一覧のURL.
        url = UrlMaker.produceevent_explain(mid, ope='nominatecast')
        self.html_param['url_produceevent_explain_nominatecast'] = self.makeAppLinkUrl(url)

    def writeHtml(self, eventmaster, name):
        self.writeAppHtml('produce_event/%s' % name)

    def makeStageObj(self, stagemaster, playdata, cur_stagenumber, bossattack=False, areaboss_attack=False):
        """ステージ情報作成.
        """
        v_player = self.getViewerPlayer()
        if playdata.stage > stagemaster.stage:
            progress = stagemaster.execution
        else:
            progress = playdata.progress
        obj_stage = Objects.produceevent_stage(self, v_player, cur_stagenumber, stagemaster, progress, playdata.confirmkey,
                                               bossattack=bossattack, areaboss_attack=areaboss_attack)
        return obj_stage

    def getCurrentProduceFlagRecord(self):
        """現在発生中のイベントのフラグレコードを取得.
        """
        if self.__current_event_flagrecord is None:
            model_mgr = self.getModelMgr()
            v_player = self.getViewerPlayer()
            current_event = self.getCurrentProduceEvent()
            self.__current_event_flagrecord = BackendApi.get_produceevent_flagrecord(model_mgr, current_event.id, v_player.id, using=settings.DB_READONLY)
        return self.__current_event_flagrecord
