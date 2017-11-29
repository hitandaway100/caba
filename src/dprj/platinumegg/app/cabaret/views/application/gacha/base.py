# -*- coding: utf-8 -*-
import settings
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.util.api import BackendApi, Objects
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.models.Player import PlayerGachaPt, PlayerDeck
from platinumegg.lib.opensocial.util import OSAUtil
from defines import Defines


class GachaHandler(AppHandler):
    """ガチャのハンドラ.
    """
    
    def preprocess(self):
        AppHandler.preprocess(self)
        self.__gachamaster_id = None
        self.__playdata = None
        self.__playcount = None
        self.__gachamaster = None
        self.__gachamasterstep = None
        self.__gachaseatmodels = None
        self.html_param['omake'] = {}
    
    def set_masterid(self, mid):
        self.__gachamaster_id = mid
        self.__playdata = None
        self.__gachamaster = None
    
    @property
    def gachamaster_id(self):
        return self.__gachamaster_id
        
    def getGachaMaster(self):
        """マスターデータ.
        """
        if self.__gachamaster is None:
            model_mgr = self.getModelMgr()
            self.__gachamaster = BackendApi.get_gachamaster(model_mgr, self.gachamaster_id, using=settings.DB_READONLY)
            if self.__gachamaster is None:
                raise CabaretError(u'存在しないガチャです', CabaretError.Code.INVALID_MASTERDATA)
            
        return self.__gachamaster
    
    def getGachaMasterStep(self):
        """マスターデータ.
        """
        if self.__gachamasterstep is None:
            model_mgr = self.getModelMgr()
            master = self.getGachaMaster()
            if master.stepsid > 0:
                if master.stepsid != master.id:
                    self.__gachamasterstep = BackendApi.get_gachamaster(model_mgr, master.stepsid, using=settings.DB_READONLY)
                    if self.__gachamasterstep is None:
                        raise CabaretError(u'存在しないガチャです', CabaretError.Code.INVALID_MASTERDATA)
                else:
                    self.__gachamasterstep = master
            
        return self.__gachamasterstep
    
    def checkSchedule(self, master):
        """マスターデータのスケジュールを確認.
        """
        model_mgr = self.getModelMgr()
        BackendApi.check_schedule(model_mgr, master.schedule, using=settings.DB_READONLY)
    
    def getGachaPlayData(self):
        """プレイ情報.
        """
        if self.__playdata is None:
            v_player = self.getViewerPlayer()
            master = self.getGachaMaster()
            model_mgr = self.getModelMgr()
            self.__playdata = BackendApi.get_gachaplaydata(model_mgr, v_player.id, [master.boxid], using=settings.DB_READONLY, get_instance=True).get(master.boxid)
        return self.__playdata
    
    def getGachaPlayCount(self):
        """プレイ回数.
        """
        if self.__playcount is None:
            v_player = self.getViewerPlayer()
            master = self.getGachaMaster()
            model_mgr = self.getModelMgr()
            if master.stepsid <= 0:
                self.__playcount = BackendApi.get_gachaplaycount(model_mgr, v_player.id, [master.id], using=settings.DB_READONLY, get_instance=True).get(master.id)
            else:
                master = self.getGachaMasterStep()
                self.__playcount = BackendApi.get_gachaplaycount(model_mgr, v_player.id, [master.id], using=settings.DB_READONLY, get_instance=True).get(master.id)
        return self.__playcount
    
    def getSeatModels(self, do_get_result=False):
        if self.__gachaseatmodels is None:
            v_player = self.getViewerPlayer()
            master = self.getGachaMasterStep() or self.getGachaMaster()
            model_mgr = self.getModelMgr()
            self.__gachaseatmodels = BackendApi.get_gachaseatmodels_by_gachamaster(model_mgr, v_player.id, master, do_get_result=do_get_result, using=settings.DB_READONLY)
        return self.__gachaseatmodels
    
    def getSeatMaster(self):
        return self.getSeatModels().get('seatmaster')
    
    def getSeatPlayData(self):
        return self.getSeatModels().get('playdata')
    
    def getSeatPlayCount(self):
        return self.getSeatModels().get('playcount')
    
    def makeGachaObj(self):
        """ガチャ情報作成.
        """
        v_player = self.getViewerPlayer()
        
        master = self.getGachaMaster()
        playcount = self.getGachaPlayCount()
        
        return Objects.gacha(self, master, v_player, playcount)
    
    def makeOmakeInfo(self, gachamaster):
        """ガチャおまけ情報作成.
        """
        if not gachamaster.bonus or isinstance(gachamaster.bonus[0], dict):    # TODO: ランダムおまけ用の情報.
            return None
        
        model_mgr = self.getModelMgr()
        
        prizelist = BackendApi.get_prizelist(model_mgr, gachamaster.bonus, using=settings.DB_READONLY)
        prizeinfo = BackendApi.make_prizeinfo(self, prizelist, using=settings.DB_READONLY)
        
        return prizeinfo
    
    def putOpenGachaList(self, topic=None, result_gachamaster=None):
        model_mgr = self.getModelMgr()
        
        # 開催中のガチャ情報.
        gachamasterlist = BackendApi.get_playablegacha_list(model_mgr, using=settings.DB_READONLY)
        
        # ガチャ情報埋め込み.
        BackendApi.put_gachahtmldata(self, gachamasterlist, topic=topic, result_gachamaster=result_gachamaster, do_put_rare_log=True)
    
    def writePlayGacha(self, now, continuity=None):
        """ガチャプレイ書き込み.
        """
        result_code = CabaretError.Code.UNKNOWN
        v_player = self.getViewerPlayer()
        uid = v_player.id
        master = self.getGachaMaster()
        playcount = self.getGachaPlayCount()
        
        seatplaydata = self.getSeatPlayData()
        is_first = 0 < BackendApi.get_gacha_firstplay_restnum(master, playcount, now, seatplaydata=seatplaydata)
        continuity = continuity or BackendApi.get_gacha_continuity_num(self.getModelMgr(), master, v_player, is_first)
        playerconfigdata = BackendApi.get_playerconfigdata(uid)
        
        try:
            model_mgr = db_util.run_in_transaction(self.__tr_write_playgacha_free, uid, master, v_player.req_confirmkey, continuity, now, playerconfigdata.autosell_rarity)
            model_mgr.write_end()
            result_code = CabaretError.Code.OK
        except CabaretError, err:
            if self.osa_util.is_dbg_user:
                raise
            result_code = err.code
        return result_code
    
    def __tr_write_playgacha_free(self, uid, gachamaster, key, continuity, now, autosell_rarity):
        model_mgr = ModelRequestMgr()
        player = BackendApi.get_players(self, [uid], [PlayerGachaPt, PlayerDeck], model_mgr=model_mgr)[0]
        BackendApi.tr_play_gacha_free(model_mgr, player, gachamaster, key, continuity, now, autosell_rarity)
        model_mgr.write_all()
        return model_mgr
    
    def makeRankingGachaRanking(self, gachamaster, view_myrank, page_content_num=10, offset=0, do_execute_api=True, single=True):
        """ランキングガチャランキングデータ.
        """
        return BackendApi.make_rankinggacha_ranking(self, gachamaster, view_myrank, page_content_num, offset, do_execute_api, single)
    
    def checkStep(self, master, playcount):
        """ステップの確認.
        """
        if master.consumetype not in (Defines.GachaConsumeType.STEPUP, Defines.GachaConsumeType.STEPUP2):
            return True
        
        model_mgr = self.getModelMgr()
        if playcount:
            BackendApi.stepup_reset(model_mgr, master, playcount,OSAUtil.get_now())
            step = playcount.step + 1
        else:
            step = 1
        
        if step != master.step:
            # ステップが不正.
            return False
        
        return True
    
    def getRankingGachaLinkDataList(self, gachamaster, rankinggachamaster, url_maker):
        """ランキングガチャページのタブ切り替え用のリンクを埋め込む.
        """
        model_mgr = self.getModelMgr()
        
        # 同じグループのランキングガチャ.
        rankinggachamasterlist_by_samegroup = BackendApi.get_rankinggacha_master_by_group(model_mgr, rankinggachamaster.group, using=settings.DB_READONLY)
        rankinggachamasterlist_by_samegroup.sort(key=lambda x:x.id)
        linklist = []
        
        for master in rankinggachamasterlist_by_samegroup:
            if rankinggachamaster.id == master.id:
                # 現在のページ.
                gm = gachamaster
            else:
                gachamaster_list = BackendApi.get_gachamaster_list_by_boxid(model_mgr, master.id, using=settings.DB_READONLY)
                if gachamaster_list:
                    gm = gachamaster_list[0]
                    for tmp_gm in gachamaster_list:
                        if tmp_gm.consumetype == Defines.GachaConsumeType.RANKING:
                            gm = tmp_gm
                            if BackendApi.check_schedule(model_mgr, tmp_gm.schedule, using=settings.DB_READONLY):
                                break
                else:
                    continue
            linklist.append({
                'boxid' : master.id,
                'name' : master.name,
                'url' : self.makeAppLinkUrl(url_maker(gm.id))
            })
        return linklist
