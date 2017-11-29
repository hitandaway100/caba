# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.cabareterror import CabaretError
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.views.application.boss.base import BossHandler
import settings_sub
from platinumegg.app.cabaret.util.api import BackendApi
import urllib
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.models.Player import PlayerAp, PlayerFriend, PlayerExp


class Handler(BossHandler):
    """ボス戦書き込み.
    やること:
        戦えるかを確認.
        戦闘計算.
        結果書き込み.
    引数:
        エリアID.
        キー.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        try:
            args = self.getUrlArgs('/bossbattle/')
            # エリア.
            areaid = int(args.get(0, None))
            scoutkey = urllib.unquote(args.get(1))[:32]
            self.setAreaID(areaid)
            if not scoutkey:
                raise CabaretError()
        except:
            raise CabaretError(u'引数が想定外です', CabaretError.Code.ILLEGAL_ARGS)
        
        model_mgr = self.getModelMgr()
        
        using = settings.DB_READONLY
        
        # ボス情報.
        boss = self.getBossMaster()

        if boss is None or not self.checkBossBattleAble(model_mgr, using=using):
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'まだこの街の太客には接客できません', CabaretError.Code.ILLEGAL_ARGS)
            self.callFunctionByFromPage('redirectToScoutTop')
            return
        
        # デッキのカード.
        cardlist = self.getDeckCardList()
        
        # 戦闘計算.
        _, animdata = BackendApi.bossbattle(cardlist, boss)
        
        # 書き込み.
        try:
            self.callFunctionByFromPage('write', animdata, scoutkey).write_end()
        except CabaretError, e:
            if e.code == CabaretError.Code.ALREADY_RECEIVED:
                pass
            else:
                raise
        
        # 結果へ.
        url = UrlMaker.bossbattleanim(areaid, scoutkey)
        self.appRedirect(self.makeAppLinkUrlRedirect(url))
    
    #==================================================
    # 通常スカウト.
    def tr_write(self, uid, area, boss, animdata, key):
        """書き込み.
        """
        model_mgr = ModelRequestMgr()
        
        # 結果書き込み.
        BackendApi.tr_save_bossresult(model_mgr, uid, area, boss, animdata, key)
        
        player = BackendApi.get_players(self, [uid], [PlayerAp, PlayerFriend, PlayerExp], model_mgr=model_mgr)[0]
        if animdata.winFlag:
            BackendApi.tr_area_clear(model_mgr, player, area)
        
        # 消費体力書き込み.
        if 0 < boss.apcost:
            BackendApi.tr_add_ap(model_mgr, player, -boss.apcost)
        
        model_mgr.write_all()
        return model_mgr
    
    def write_SCOUT(self, animdata, scoutkey):
        """書き込み
        """
        v_player = self.getViewerPlayer()
        area = self.getAreaMaster()
        boss = self.getBossMaster()
        return db_util.run_in_transaction(self.tr_write, v_player.id, area, boss, animdata, scoutkey)
    
    #==================================================
    # スカウトイベント.
    def write_SCOUTEVENT(self, animdata, scoutkey):
        """書き込み
        """
        model_mgr = self.getModelMgr()
        eventmaster = BackendApi.get_current_scouteventmaster(model_mgr, using=settings.DB_READONLY)
        if eventmaster is None:
            raise CabaretError(u'Event Closed.', CabaretError.Code.EVENT_CLOSED)
        v_player = self.getViewerPlayer()
        area = self.getAreaMaster()
        boss = self.getBossMaster()
        
        return db_util.run_in_transaction(self.tr_event_write, eventmaster, v_player.id, area, boss, animdata, scoutkey, BackendApi.tr_scoutevent_stage_clear)
    
    #==================================================
    # レイドイベント.
    def write_RAIDEVENTSCOUT(self, animdata, scoutkey):
        """書き込み
        """
        model_mgr = self.getModelMgr()
        eventmaster = BackendApi.get_current_raideventmaster(model_mgr, using=settings.DB_READONLY)
        if eventmaster is None:
            raise CabaretError(u'Event Closed.', CabaretError.Code.EVENT_CLOSED)
        v_player = self.getViewerPlayer()
        area = self.getAreaMaster()
        boss = self.getBossMaster()
        
        return db_util.run_in_transaction(self.tr_event_write, eventmaster, v_player.id, area, boss, animdata, scoutkey, BackendApi.tr_raidevent_stage_clear)

    #==================================================
    # プロデュースイベント
    def write_PRODUCEEVENT(self, animdata, scoutkey):
        return self.write_PRODUCEEVENTSCOUT(animdata, scoutkey)

    def write_PRODUCEEVENTSCOUT(self, animdata, scoutkey):
        """書き込み
        """
        model_mgr = self.getModelMgr()
        eventmaster = BackendApi.get_current_produce_event_master(model_mgr, using=settings.DB_READONLY)
        if eventmaster is None:
            raise CabaretError(u'Event Closed.', CabaretError.Code.EVENT_CLOSED)
        v_player = self.getViewerPlayer()
        area = self.getAreaMaster()
        boss = self.getBossMaster()

        return db_util.run_in_transaction(self.tr_event_write, eventmaster, v_player.id, area, boss, animdata, scoutkey, BackendApi.tr_produceevent_stage_clear)

    #==================================================
    def tr_event_write(self, eventmaster, uid, stage, boss, animdata, key, write_win):
        """イベント書き込み.
        """
        model_mgr = ModelRequestMgr()
        
        # 結果書き込み.
        BackendApi.tr_save_bossresult(model_mgr, uid, stage, boss, animdata, key)
        
        player = BackendApi.get_players(self, [uid], [PlayerAp, PlayerFriend, PlayerExp], model_mgr=model_mgr)[0]
        if animdata.winFlag:
            write_win(model_mgr, eventmaster, player, stage)
        
        # 消費体力書き込み.
        if 0 < boss.apcost:
            BackendApi.tr_add_ap(model_mgr, player, -boss.apcost)
        
        model_mgr.write_all()
        return model_mgr

def main(request):
    return Handler.run(request)
