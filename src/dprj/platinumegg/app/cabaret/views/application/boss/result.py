# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.views.application.boss.base import BossHandler
import settings_sub
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import urllib
import settings
from platinumegg.lib.opensocial.util import OSAUtil
from defines import Defines


class Handler(BossHandler):
    """ボス戦結果.
    表示するもの:
        ボス情報.
        デッキ情報.
        勝った時:
            次のエリアのURL
            報酬.
    引数:
        エリアID.
        キー.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        args = self.getUrlArgs('/bossresult/')
        try:
            # エリア.
            areaid = int(args.get(0, None))
            self.setAreaID(areaid)
            battlekey = urllib.unquote(args.get(1))[:32]
            if not battlekey:
                raise
        except:
            raise CabaretError(u'引数が想定外です', CabaretError.Code.ILLEGAL_ARGS)
        
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        uid = v_player.id
        
        using = settings.DB_READONLY
        
        # 結果.
        bossbattle = BackendApi.get_bossresult(model_mgr, uid, areaid, using=using)
        if bossbattle is None:
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'結果が見つかりませんでした', CabaretError.Code.ILLEGAL_ARGS)
            self.callFunctionByFromPage('redirectToScoutTop')
            return
        
        animdata = bossbattle.anim
        
        is_win = animdata.winFlag
        b_hp = animdata.bossHpPost
        
        # ボス情報.
        boss = self.getBossMaster()
        self.html_param['boss'] = self.makeBossObj(boss, b_hp)
        
        # デッキのカード.
        self.putDeckInfoParams()
        
        area = self.getAreaMaster()
        self.html_param['area'] = self.makeAreaObj(area, playdata=None)
        
        if is_win:
            # エリアクリア報酬情報.
            prizeidlist = self.callFunctionByFromPage('getAreaPrize')
            prizelist = BackendApi.get_prizelist(model_mgr, prizeidlist, using=using)
            self.html_param['prize'] = BackendApi.make_prizeinfo(self, prizelist, using=using)
            
            # 次のエリアの情報.
            self.callFunctionByFromPage('putNextAreaInfo')
            
            self.writeAppHtml('boss/bosswin')
        else:
            # イベントバナー.
            eventbanners = BackendApi.get_eventbanners(self, using=settings.DB_READONLY)
            if eventbanners:
                self.html_param['eventbanners'] = [Objects.eventbanner(self, banner) for banner in eventbanners]
            
            # 強化合成素材選択のページ.
            deck = self.getDeck()
            url = UrlMaker.compositionmaterial(deck.leader)
            self.html_param['url_composition_material'] = self.makeAppLinkUrl(url)
            
            self.writeAppHtml('boss/bosslose')
    
    def __putEventNextAreaInfo(self, eventmaster, event_next_stage_getter):
        model_mgr = self.getModelMgr()
        
        if eventmaster is not None:
            stagemaster = self.getAreaMaster()
            nextstagemaster = None
            if stagemaster:
                nextstagemaster = event_next_stage_getter()
                if nextstagemaster and nextstagemaster.id != stagemaster.id:
                    obj_next_area = self.makeAreaObj(nextstagemaster, playdata=None)
                    obj_next_area['name'] = u'%s%s' % (nextstagemaster.areaname, nextstagemaster.name)
                    self.html_param['next_area'] = obj_next_area
                
                eventplaydata = self.getAreaPlayData()
                if stagemaster.earlybonus and eventplaydata.result and eventplaydata.result.get('earlybonus'):
                    # 早期クリアボーナス.
                    prizelist = BackendApi.get_prizelist(model_mgr, stagemaster.earlybonus, using=settings.DB_READONLY)
                    self.html_param['earlybonus'] = BackendApi.make_prizeinfo(self, prizelist, using=settings.DB_READONLY)
    
    #==================================================
    # 通常スカウト.
    def getAreaPrize_SCOUT(self):
        area = self.getAreaMaster()
        return area.prizes
    
    def putNextAreaInfo_SCOUT(self):
        model_mgr = self.getModelMgr()
        area = self.getAreaMaster()
        
        next_areaid = BackendApi.get_next_areaid(model_mgr, area.id, using=settings.DB_READONLY)
        if next_areaid and area.id != next_areaid:
            # 次のエリア情報.
            next_area = BackendApi.get_area(model_mgr, next_areaid, using=settings.DB_READONLY)
            self.html_param['next_area'] = self.makeAreaObj(next_area, playdata=None)
        
        url = UrlMaker.scout()
        url = OSAUtil.addQuery(url, Defines.URLQUERY_AREA, next_areaid)
        self.html_param['url_scout'] = self.makeAppLinkUrl(url)
    
    #==================================================
    # スカウトイベント.
    def getAreaPrize_SCOUTEVENT(self):
        area = self.getAreaMaster()
        return area.bossprizes
    
    def putNextAreaInfo_SCOUTEVENT(self):
        model_mgr = self.getModelMgr()
        
        eventmaster = BackendApi.get_current_scouteventmaster(model_mgr, using=settings.DB_READONLY)
        stagemaster = self.getAreaMaster()
        event_next_stage_getter = lambda : BackendApi.get_event_next_stage(model_mgr, eventmaster.id, stagemaster, using=settings.DB_READONLY)
        self.__putEventNextAreaInfo(eventmaster, event_next_stage_getter)
        
        if eventmaster and stagemaster:
            if stagemaster.movie:
                # 開放された動画.
                dic = BackendApi.get_eventmovie_necessaryitems_dict(model_mgr, [stagemaster.movie], using=settings.DB_READONLY).get(stagemaster.movie)
                eventmoviemaster = dic['master']
                moviemaster = dic['pc'] if self.is_pc else dic['sp']
                self.html_param['eventmovie'] = Objects.eventmovie(self, eventmoviemaster, moviemaster, None, True)
                self.html_param['url_eventmovie_detail'] = self.makeAppLinkUrl(UrlMaker.scoutevent_movie(stagemaster.stage))
        
        self.html_param['url_scout'] = self.makeAppLinkUrl(UrlMaker.scoutevent())
        self.html_param['url_scoutevent_top'] = self.makeAppLinkUrl(UrlMaker.scoutevent_top())
    
    #==================================================
    # レイドイベント.
    def getAreaPrize_RAIDEVENTSCOUT(self):
        area = self.getAreaMaster()
        return area.bossprizes
    
    def putNextAreaInfo_RAIDEVENTSCOUT(self):
        model_mgr = self.getModelMgr()
        eventmaster = BackendApi.get_current_raideventmaster(model_mgr, using=settings.DB_READONLY)
        event_next_stage_getter = lambda : BackendApi.get_raidevent_next_stagemaster(model_mgr, eventmaster.id, self.getAreaMaster(), using=settings.DB_READONLY)
        self.__putEventNextAreaInfo(eventmaster, event_next_stage_getter)
        
        self.html_param['url_scout'] = self.makeAppLinkUrl(UrlMaker.raidevent_scouttop())
        self.html_param['url_raidevent_top'] = self.makeAppLinkUrl(UrlMaker.raidevent_top())

    # ==================================================
    # プロデュースイベント.
    def getAreaPrize_PRODUCEEVENT(self):
        return self.getAreaPrize_PRODUCEEVENTSCOUT()

    def getAreaPrize_PRODUCEEVENTSCOUT(self):
        area = self.getAreaMaster()
        return area.bossprizes

    def putNextAreaInfo_PRODUCEEVENT(self):
        return self.putNextAreaInfo_PRODUCEEVENTSCOUT()

    def putNextAreaInfo_PRODUCEEVENTSCOUT(self):
        model_mgr = self.getModelMgr()
        eventmaster = BackendApi.get_current_produce_event_master(model_mgr, using=settings.DB_READONLY)
        event_next_stage_getter = lambda : BackendApi.get_produceevent_next_stagemaster(model_mgr, eventmaster.id, self.getAreaMaster(), using=settings.DB_READONLY)
        self.__putEventNextAreaInfo(eventmaster, event_next_stage_getter)

        self.html_param['url_scout'] = self.makeAppLinkUrl(UrlMaker.produceevent_scouttop())
        self.html_param['url_produceevent_top'] = self.makeAppLinkUrl(UrlMaker.produceevent_top())


def main(request):
    return Handler.run(request)
