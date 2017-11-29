# -*- coding: utf-8 -*-
from defines import Defines
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.models.Player import PlayerScout, PlayerAp,\
    PlayerGold, PlayerExp, PlayerDeck, PlayerFriend
from platinumegg.app.cabaret.views.application.raidevent.base import RaidEventBaseHandler


class Handler(RaidEventBaseHandler):
    """レイドイベントスカウトTopページ.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerScout, PlayerAp, PlayerGold, PlayerExp, PlayerDeck, PlayerFriend]
    
    def __putParam(self, key, value):
        self.html_param[key] = value
    
    def process(self):
        
        v_player = self.getViewerPlayer()
        uid = v_player.id
        
        model_mgr = self.getModelMgr()
        
        using = settings.DB_READONLY
        
        # イベントマスター.
        eventmaster = self.getCurrentRaidEvent()
        mid = eventmaster.id
        
        # イベントスカウトのプレイ情報
        playdata = BackendApi.get_raideventstage_playdata(model_mgr, mid, uid, using=using)
        
        # 今いるステージ.
        stagemaster = BackendApi.get_current_raideventstage_master(model_mgr, eventmaster, playdata, using=using)
        
        cardget_event = BackendApi.find_scout_event(playdata, Defines.ScoutEventType.GET_CARD)
        if cardget_event and not cardget_event.is_received:
            # カード獲得で離脱した.
            url = UrlMaker.raidevent_scoutresult(stagemaster.id, playdata.alreadykey)
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        
        # ボス出現.
        bossattack = False
        allcleared = BackendApi.check_event_boss_playable(playdata, stagemaster)
        boss = None
        if 0 < stagemaster.boss and allcleared:
            boss = BackendApi.get_boss(model_mgr, stagemaster.boss, using=using)
            if boss is not None:
                bossattack = True
        
        # 現在のステージ情報.
        obj_scout = self.makeStageObj(stagemaster, playdata, stagemaster.stage, bossattack=bossattack)
        self.__putParam('scout', obj_scout)
        
        # ボス
        if bossattack:
            # ボス戦へのURL.
            self.__putParam('boss', Objects.boss(self, boss))
            self.setFromPage(Defines.FromPages.RAIDEVENTSCOUT, stagemaster.id)
            url = UrlMaker.bosspre(stagemaster.id)
            self.html_param['url_bossbattle'] = self.makeAppLinkUrl(url)
        
        self.html_param['player'] = Objects.player(self, v_player, None)
        
        # 説明とランキングのリンク.
        self.putEventTopic(mid)
        
        # カードの上限チェック.
        if v_player.cardlimit <= BackendApi.get_cardnum(uid, arg_model_mgr=model_mgr, using=using):
            self.__putParam('overlimit_card', True)
        
        # 宝箱の上限チェック.
        overlimit_treasure_list = BackendApi.get_treasuretype_list_overlimit(model_mgr, uid, using=using)
        self.__putParam('overlimit_treasure', overlimit_treasure_list)
        
        self.__putParam('flag_skip', BackendApi.get_scoutskip_flag(uid))
        
        config = BackendApi.get_current_raideventconfig(model_mgr, using=settings.DB_READONLY)
        max_stage = config.get_stage_max()
        is_all_open = max_stage is None
        self.__putParam('is_all_open', is_all_open)
        
        is_all_cleared = False
        if is_all_open:
            if allcleared and not bossattack:
                stagelist_all = BackendApi.get_raidevent_stagemaster_by_stagenumber(model_mgr, mid, using=settings.DB_READONLY)
                stagelist_all.sort(key=lambda x:x.stage, reverse=True)
                is_all_cleared = stagelist_all[0].stage <= playdata.cleared
        else:
            is_all_cleared = max_stage <= playdata.cleared
        self.__putParam('is_all_cleared', is_all_cleared)
        
        # レイドイベント.
        self.putChampagneData()
        
        self.writeHtml(eventmaster, 'scout/scout')
    

def main(request):
    return Handler.run(request)
