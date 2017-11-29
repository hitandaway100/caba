# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.application.raidevent.base import RaidEventBaseHandler
from platinumegg.app.cabaret.views.application.produce_event.base import ProduceEventBaseHandler
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from platinumegg.app.cabaret.models.Player import PlayerRequest, PlayerAp, \
    PlayerExp, PlayerFriend, PlayerTreasure
from platinumegg.lib.opensocial.util import OSAUtil
from defines import Defines
from platinumegg.app.cabaret.util.happening import HappeningUtil
from platinumegg.app.cabaret.models.produce_event.ProduceEvent import ProduceEventScore
from platinumegg.app.cabaret.util.redisdb import ProduceEventRanking

class Handler(ProduceEventBaseHandler):
    """レイドイベントレイド挑戦.
    自分のレイドだけ.
    救援はproducehelpdetailへ.
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
        cur_eventmaster = self.getCurrentProduceEvent()
        mid = cur_eventmaster.id

        # 現在発生中のレイド.
        happeningraidset = self.getHappeningRaidSet()
        if happeningraidset is None or happeningraidset.raidboss is None:
            self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.mypage()))
            return

        # イベントのレイド判定.
        happeningset = happeningraidset.happening
        raidboss = happeningraidset.raidboss
        eventid = HappeningUtil.get_produceeventid(happeningset.happening.event)
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
            self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.produceraidend(happeningset.happening.id)))
            return

        produceeventraidmaster = BackendApi.get_produceevent_raidmaster(model_mgr, cur_eventmaster.id, raidboss.master.id, using=settings.DB_READONLY)

        # キャストを借りる.
        func_put_playerlist = self.putHelpFriend(raidboss)

        # ダメージ履歴.
        func_put_attacklog = self.putRaidAttackLog(raidboss)

        # イベント情報.
        config = BackendApi.get_current_produce_event_config(model_mgr, using=settings.DB_READONLY)
        self.html_param['produceevent'] = Objects.produceevent(self, cur_eventmaster, config)

        # レイド情報.
        obj_happening = Objects.producehappening(self, happeningraidset)
        self.html_param['happening'] = obj_happening

        # 実行リンク 等倍と3倍.
        url = UrlMaker.produceraiddo(raidboss.id, v_player.req_confirmkey)
        self.html_param['url_exec'] = self.makeAppLinkUrl(url)
        self.html_param['url_exec_strong'] = self.makeAppLinkUrl(OSAUtil.addQuery(url, Defines.URLQUERY_STRONG, 1))

        # イベントデータ.
        scorerecord = BackendApi.get_produceevent_scorerecord(model_mgr, mid, uid, using=settings.DB_READONLY)
        self.html_param['produceeventscore'] = Objects.produceevent_score(cur_eventmaster, scorerecord, None)

        # 特攻カード.
        #BackendApi.put_raidevent_specialcard_info(self, uid, produceeventraidmaster, using=settings.DB_READONLY)

        # このページに戻ってくるリンク.
        self.setFromPage(Defines.FromPages.HAPPENING, happeningset.id)
        BackendApi.put_bprecover_uselead_info(self)
        self.html_param['url_deck_raid'] = self.makeAppLinkUrl(UrlMaker.deck_raid())

        # デッキ情報.
        deckcardlist = self.getDeckCardList()
        self.putDeckParams(deckcardlist)

        self.execute_api()
        # if func_put_attacklog:
        #     func_put_attacklog()
        # if func_put_playerlist:
        #     func_put_playerlist()

        self.html_param['player'] = Objects.player(self, v_player)

        event_item_master = BackendApi.get_itemmaster(model_mgr, cur_eventmaster.useitem, using=settings.DB_READONLY)
        has_event_item_nums = BackendApi.get_item_nums(model_mgr, uid, [event_item_master.id], using=settings.DB_READONLY)
        if not has_event_item_nums:
            num = 0
        else:
            num = has_event_item_nums[event_item_master.id]
        self.html_param['event_item'] = {
            'name': event_item_master.name,
            'num': num
        }
        self.html_param['shop_url'] = self.makeAppLinkUrl(UrlMaker.shop())
        produce_score = ProduceEventScore.get_instance(model_mgr, uid, mid, using=settings.DB_READONLY)
        self.html_param['produce_eventscore'] = produce_score.to_dict()
        self.html_param['produce_rank'] = BackendApi.get_ranking_rank(ProduceEventRanking, mid, uid)

        self.writeHtml(cur_eventmaster, 'bossappear')


def main(request):
    return Handler.run(request)
