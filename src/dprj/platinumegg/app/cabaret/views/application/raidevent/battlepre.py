# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.application.raidevent.base import RaidEventBaseHandler
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from platinumegg.app.cabaret.models.Player import PlayerRequest, PlayerAp,\
    PlayerExp, PlayerFriend, PlayerTreasure
from platinumegg.lib.opensocial.util import OSAUtil
from defines import Defines
from platinumegg.app.cabaret.util.happening import HappeningUtil


class Handler(RaidEventBaseHandler):
    """レイドイベントレイド挑戦.
    自分のレイドだけ.
    救援はraidhelpdetailへ.
    イベント情報.
    ハプニング情報.
    実行リンク 等倍と3倍.
    キャストを借りる.
    ダメージ履歴.
    特攻カード.
    諦めるリンク.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerAp, PlayerExp, PlayerFriend, PlayerTreasure, PlayerRequest]
    
    def process(self):
        
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        uid = v_player.id
        
        # 開催中判定.
        cur_eventmaster = self.getCurrentRaidEvent()
        mid = cur_eventmaster.id
        
        # 現在発生中のレイド.
        happeningraidset = self.getHappeningRaidSet()
        if happeningraidset is None or happeningraidset.raidboss is None:
            self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.mypage()))
            return
        
        # イベントのレイド判定.
        happeningset = happeningraidset.happening
        raidboss = happeningraidset.raidboss
        eventid = HappeningUtil.get_raideventid(happeningset.happening.event)
        if happeningset.happening.oid != uid:
            # 自分のじゃないのは救援詳細へ.
            self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.raidhelpdetail(happeningset.id)))
            return
        elif eventid != mid:
            # イベントじゃないレイド.
            self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.happening()))
            return
        elif not happeningset.happening.is_active():
            # 終了済み.
            self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.raidend(happeningset.happening.id)))
            return
        
        raideventraidmaster = BackendApi.get_raidevent_raidmaster(model_mgr, cur_eventmaster.id, raidboss.master.id, using=settings.DB_READONLY)
        
        # キャストを借りる.
        func_put_playerlist = self.putHelpFriend(raidboss)
        
        # ダメージ履歴.
        func_put_attacklog = self.putRaidAttackLog(raidboss)
        
        # イベント情報.
        config = BackendApi.get_current_raideventconfig(model_mgr, using=settings.DB_READONLY)
        self.html_param['raidevent'] = Objects.raidevent(self, cur_eventmaster, config)
        
        # レイド情報.
        obj_happening = Objects.happening(self, happeningraidset)
        self.html_param['happening'] = obj_happening
        
        # 実行リンク 等倍と3倍.
        url = UrlMaker.raiddo(raidboss.id, v_player.req_confirmkey)
        self.html_param['url_exec'] = self.makeAppLinkUrl(url)
        self.html_param['url_exec_strong'] = self.makeAppLinkUrl(OSAUtil.addQuery(url, Defines.URLQUERY_STRONG, 1))
        
        # 諦める.
        self.html_param['url_happeningcancel_yesno'] = self.makeAppLinkUrl(UrlMaker.happeningcancel_yesno())
        
        # 初心者フラグ.
        is_beginer = BackendApi.check_raidevent_beginer(model_mgr, uid, cur_eventmaster, config, using=settings.DB_READONLY)
        self.html_param['is_beginer'] = is_beginer
        
        # イベントデータ.
        scorerecord = BackendApi.get_raidevent_scorerecord(model_mgr, mid, uid, using=settings.DB_READONLY)
        rank = BackendApi.get_raidevent_rank(cur_eventmaster.id, uid)
        rank_beginer = BackendApi.get_raidevent_rank(cur_eventmaster.id, uid, is_beginer=True)
        self.html_param['raideventscore'] = Objects.raidevent_score(cur_eventmaster, scorerecord, rank, rank_beginer)
        
        # 特攻カード.
        BackendApi.put_raidevent_specialcard_info(self, uid, raideventraidmaster, using=settings.DB_READONLY)
        
        # このページに戻ってくるリンク.
        self.setFromPage(Defines.FromPages.HAPPENING, happeningset.id)
        BackendApi.put_bprecover_uselead_info(self)
        self.html_param['url_deck_raid'] = self.makeAppLinkUrl(UrlMaker.deck_raid())
        
        # デッキ情報.
        deckcardlist = self.getDeckCardList()
        self.putDeckParams(deckcardlist)
        
        self.execute_api()
        if func_put_attacklog:
            func_put_attacklog()
        if func_put_playerlist:
            func_put_playerlist()
        
        # 説明とランキングのリンク.
        url = UrlMaker.raidevent_top(mid)
        self.html_param['url_raidevent_top'] = self.makeAppLinkUrl(url)
        
        self.html_param['player'] = Objects.player(self, v_player)
        
        self.writeHtml(cur_eventmaster, 'bossappear')
    

def main(request):
    return Handler.run(request)
