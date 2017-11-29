# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.api import BackendApi, Objects
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.models.Player import PlayerScout, PlayerAp, \
    PlayerGold, PlayerExp, PlayerDeck, PlayerFriend
from platinumegg.app.cabaret.views.application.produce_event.base import ProduceEventBaseHandler
from defines import Defines
import settings

class Handler(ProduceEventBaseHandler):
    """プロデュースイベントスカウトTopページ.
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
        eventmaster = self.getCurrentProduceEvent()
        mid = eventmaster.id

        # イベントスカウトのプレイ情報
        playdata = BackendApi.get_produceeventstage_playdata(model_mgr, mid, uid, using=using)

        # 今いるステージ.
        stagemaster = BackendApi.get_current_produceeventstage_master(model_mgr, eventmaster, playdata, using=using)

        bossattack = False
        # 発生中のレイド情報.
        happeningraidset = self.getHappeningRaidSet()
        happeningset = None
        if happeningraidset:
            happeningset = happeningraidset.happening
        if happeningset:
            # レイドがある.
            if not happeningset.happening.is_end():
                bossattack = True

        # エリアボス出現
        areaboss_attack = False
        allcleared = BackendApi.check_event_boss_playable(playdata, stagemaster)
        boss = None
        if 0 < stagemaster.boss and allcleared:
            boss = BackendApi.get_boss(model_mgr, stagemaster.boss, using=settings.DB_READONLY)
            if boss is not None:
                areaboss_attack = True

        # エリアボス情報
        if areaboss_attack:
            # エリアボス戦へのURL
            self.html_param['areaboss'] = Objects.boss(self, boss)
            self.setFromPage(Defines.FromPages.PRODUCEEVENT, stagemaster.id)
            url = UrlMaker.bosspre(stagemaster.id)
            self.html_param['url_bossbattle'] = self.makeAppLinkUrl(url)

        # 現在のステージ情報
        obj_scout = self.makeStageObj(stagemaster, playdata, stagemaster.stage, bossattack=bossattack, areaboss_attack=areaboss_attack)
        self.__putParam('scout', obj_scout)

        # プレーヤーの情報
        self.html_param['player'] = Objects.player(self, v_player, None)

        # 宝箱の上限チェック.
        overlimit_treasure_list = BackendApi.get_treasuretype_list_overlimit(model_mgr, uid, using=using)
        self.__putParam('overlimit_treasure', overlimit_treasure_list)

        # スキップフラグ
        self.__putParam('flag_skip', BackendApi.get_scoutskip_flag(uid))
        # 全力探索フラグ
        self.__putParam('flag_search', BackendApi.get_scoutsearch_flag(uid))

        # 説明とランキングのリンク.
        self.putEventTopic(mid)

        self.writeHtml(eventmaster, 'scout/scout')


def main(request):
    return Handler.run(request)
