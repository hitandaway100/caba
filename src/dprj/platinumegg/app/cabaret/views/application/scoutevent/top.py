# -*- coding: utf-8 -*-
from defines import Defines
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.views.application.scoutevent.base import ScoutHandler
from platinumegg.app.cabaret.models.Player import PlayerScout, PlayerAp,\
    PlayerGold, PlayerExp, PlayerDeck, PlayerFriend


class Handler(ScoutHandler):
    """スカウトTopページ.
    引数:
        プレイヤー情報.
        エリア情報.
        エリアのスカウト情報.
        スカウトのドロップアイテムの取得状況.
        ボス情報.
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
        eventmaster = self.getCurrentScoutEvent()
        mid = eventmaster.id
        
        # イベントプレイ情報
        playdata = BackendApi.get_event_playdata(model_mgr, mid, uid, using)
        
        # 今いるステージ.
        stage = BackendApi.get_current_scouteventstage_master(model_mgr, eventmaster, playdata, using=settings.DB_READONLY)
        stageid = stage.stage
        
        cardget_event = BackendApi.find_scout_event(playdata, Defines.ScoutEventType.GET_CARD)
        if cardget_event and not cardget_event.is_received:
            # カード獲得で離脱した.
            url = UrlMaker.scouteventresult(stage.id, playdata.alreadykey)
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        
        # プレイ情報.
        self.__putParam('scout', Objects.scoutevent_stage(self, stage, playdata))
        
        # ボス出現.
        bossattack = False
        allcleared = BackendApi.check_event_boss_playable(playdata, stage)
        boss = None
        if 0 < stage.boss and allcleared:
            boss = BackendApi.get_boss(model_mgr, stage.boss, using=using)
            if boss is not None:
                bossattack = True
        
        # ステージ情報.
        obj_stage = self.makeStageObj(stage, playdata, stageid, bossattack)
        self.__putParam('stagelist', [obj_stage])
        
        # ボス
        if bossattack:
            # ボス戦へのURL.
            self.__putParam('boss', Objects.boss(self, boss))
            self.setFromPage(Defines.FromPages.SCOUTEVENT, stage.id)
            url = UrlMaker.bosspre(stage.id)
            self.html_param['url_bossbattle'] = self.makeAppLinkUrl(url)
        
        self.html_param['player'] = Objects.player(self, v_player, None)
        
        self.html_param['scoutevent'] = Objects.scouteventmaster(self, eventmaster, None)
        
        # フィーバー
        self.html_param['scouteventfever'] = Objects.scoutevent_fever(playdata)
        
        # 説明とランキングのリンク.
        self.putEventTopic(mid, 'top')
        
        # カードの上限チェック.
        if v_player.cardlimit <= BackendApi.get_cardnum(uid, arg_model_mgr=model_mgr, using=using):
            self.__putParam('overlimit_card', True)
        
        # 宝箱の上限チェック.
        overlimit_treasure_list = BackendApi.get_treasuretype_list_overlimit(model_mgr, uid, using=using)
        self.__putParam('overlimit_treasure', overlimit_treasure_list)
        
        self.__putParam('flag_skip', BackendApi.get_scoutskip_flag(uid))
        
        config = BackendApi.get_current_scouteventconfig(model_mgr, using=settings.DB_READONLY)
        max_stage = config.get_stage_max()
        is_all_open = max_stage is None
        self.__putParam('is_all_open', is_all_open)
        
        is_all_cleared = False
        if is_all_open:
            if allcleared and not bossattack:
                stagelist_all = BackendApi.get_event_stage_by_stagenumber(model_mgr, mid, using=settings.DB_READONLY)
                stagelist_all.sort(key=lambda x:x.stage, reverse=True)
                is_all_cleared = stagelist_all[0].stage <= playdata.cleared
        else:
            is_all_cleared = max_stage <= playdata.cleared
        self.__putParam('is_all_cleared', is_all_cleared)
        
        # 短冊情報.
        BackendApi.put_scoutevent_tanzakudata(self, uid)
        
        self.writeScoutEventHTML('scout', eventmaster)
    

def main(request):
    return Handler.run(request)
