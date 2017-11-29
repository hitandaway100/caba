# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.application.cabaclub import CabaClubHandler
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.url_maker import UrlMaker
import settings
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from defines import Defines
from platinumegg.app.cabaret.models.Player import PlayerExp
from platinumegg.lib.opensocial.util import OSAUtil
import settings_sub


class CabaClubEventBaseHandler(CabaClubHandler):
    """経営イベントのハンドラ
    """

    def preprocess(self):
        CabaClubHandler.preprocess(self)
        self.__current_event = None

    def processAppError(self, err):
        if err.code == CabaretError.Code.EVENT_CLOSED:
            url = UrlMaker.mypage()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        CabaClubHandler.processAppError(self, err)

    def getCurrentCabaClubEvent(self):
        """現在発生中の経営のイベント
        """
        if self.__current_event is None:
            model_mgr = self.getModelMgr()
            self.__current_event = BackendApi.get_current_cabaclubrankeventmaster(model_mgr, using=settings.DB_READONLY)
            if self.__current_event is None:
                raise CabaretError(u'Event is closed', CabaretError.Code.EVENT_CLOSED)
        return self.__current_event
