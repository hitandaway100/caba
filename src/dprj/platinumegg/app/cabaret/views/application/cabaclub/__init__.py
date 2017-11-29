# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from platinumegg.lib.opensocial.util import OSAUtil
from defines import Defines
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.redisdb import CabaClubLastViewedStore
from platinumegg.app.cabaret.util.redisdb import RedisModel, CabaClubRanking
from platinumegg.app.cabaret.models.CabaretClubEvent import CabaClubEventRankMaster, CabaClubRankEventMaster
from platinumegg.app.cabaret.util.url_maker import UrlMaker


class CabaClubHandler(AppHandler):
    """キャバクラ経営のハンドラ.
    """

    def preprocess(self):
        AppHandler.preprocess(self)
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()

        # プレーヤーの本日の総売上を取得
        eventmaster = BackendApi.get_current_cabaclubrankeventmaster(model_mgr, using=settings.DB_READONLY)
        if eventmaster:
            rankingid = CabaClubRankEventMaster.makeID(v_player.id, eventmaster.id)
            rankmaster = BackendApi.get_model(model_mgr, CabaClubEventRankMaster, rankingid, using=settings.DB_READONLY)
            self.html_param['today_proceeds'] = rankmaster.today_proceeds if rankmaster else 0
        else:
            self.html_param['today_proceeds'] = 0
        self.html_param['url_cabaclub_top'] = self.makeAppLinkUrl(UrlMaker.cabaclubtop())

    def updateStore(self, now, master=None):
        """店舗の更新.
        """
        model_mgr = self.getModelMgr()
        # ユーザID取得.
        v_player = self.getViewerPlayer()
        BackendApi.update_cabaretclubstore(model_mgr, v_player.id, now, master)
    
    def getLastViewedStoreMaster(self):
        """最後に閲覧した店舗を取得.
        """
        # ユーザID取得.
        v_player = self.getViewerPlayer()
        uid = v_player.id
        # マスターIDを取得.
        model = CabaClubLastViewedStore.get(uid)
        if model is None:
            return None
        # マスターデータを取得.
        return BackendApi.get_cabaretclub_store_master(self.getModelMgr(), model.mid, using=settings.DB_READONLY)
    
    def saveLastViewedStore(self, cabaclubstoremaster):
        """最後に閲覧した店舗を記録.
        """
        # ユーザID取得.
        v_player = self.getViewerPlayer()
        uid = v_player.id
        # 保存.
        CabaClubLastViewedStore.create(uid, cabaclubstoremaster.id).save()
    
    def getStoreCastList(self, mid):
        """店舗に配置されているキャスト.
        """
        model_mgr = self.getModelMgr()
        # ユーザID取得.
        v_player = self.getViewerPlayer()
        uid = v_player.id
        # キャストのIDを取得.
        castdata = BackendApi.get_cabaretclub_castdata(model_mgr, uid, mid, using=settings.DB_READONLY)
        if castdata:
            return BackendApi.get_cards(castdata.cast, model_mgr, using=settings.DB_READONLY)
        else:
            return []

    def get_cabaclub_management_info(self, model_mgr, uid, now, using=settings.DB_READONLY):
        scoredata = BackendApi.get_cabaretclub_scoreplayerdata(model_mgr, uid, using=using)
        scoredata_weekly = BackendApi.get_cabaretclub_scoreplayerdata_weekly(model_mgr, uid, now, using=using)
        obj_cabaclub_management_info = Objects.cabaclub_management_info(self, scoredata, scoredata_weekly)
        return obj_cabaclub_management_info

    def set_event_period(self, model_mgr, htmlparam, event_config):
        if BackendApi.get_current_cabaclubrankeventmaster(model_mgr):
            htmlparam['event_start_time'] = event_config.starttime
            htmlparam['event_end_time'] = event_config.endtime
            htmlparam['is_event_open'] = True
        else:
            htmlparam['event_start_time'] = event_config.next_starttime
            htmlparam['event_end_time'] = event_config.next_endtime
            htmlparam['is_event_open'] = False
