# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.views.application.produce_event.base import ProduceEventBaseHandler
import urllib
from platinumegg.app.cabaret.models.Player import PlayerAp, PlayerExp, \
    PlayerGold, PlayerDeck, PlayerFriend
from defines import Defines
from platinumegg.app.cabaret.util.card import CardSet
import settings_sub
from platinumegg.app.cabaret.util.happening import HappeningRaidSet


class Handler(ProduceEventBaseHandler):
    """スカウト結果.
    引数:
        実行したスカウトのID.
        確認キー.
    共通で埋め込むもの:
        スカウト情報.
        プレイヤー情報.
        スカウトを続けるURL.
    結果のパターン:
        レベルアップ.
            スカウト達成があるかも.
        スカウト達成.
        アイテム獲得.
        トロフィ獲得.
        カード獲得.
        行動力が足りない.
        なにも起きなかった.
            scoutdoへリダイレクト.
    """

    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerAp, PlayerFriend, PlayerExp, PlayerGold, PlayerDeck]

    def process(self):
        args = self.getUrlArgs('/produceeventscoutresult/')
        try:
            stageid = int(args.get(0))
            scoutkey = urllib.unquote(args.get(1))
        except:
            raise CabaretError(u'引数が想定外です', CabaretError.Code.ILLEGAL_ARGS)

        v_player = self.getViewerPlayer()
        uid = v_player.id

        model_mgr = self.getModelMgr()

        using = settings.DB_READONLY

        eventmaster = BackendApi.get_current_produce_event_master(model_mgr, using=using)
        if eventmaster is None:
            raise CabaretError(u'Event Closed.', CabaretError.Code.EVENT_CLOSED)
        mid = eventmaster.id
        self.eventmaster = eventmaster

        # 進行情報.
        playdata = BackendApi.get_produceeventstage_playdata(model_mgr, mid, uid, using=using)
        if playdata and playdata.confirmkey == scoutkey:
            # DBからとり直すべき.
            playdata = BackendApi.get_produceeventstage_playdata(model_mgr, mid, uid, using=using, reflesh=True)

        if playdata is None or playdata.alreadykey != scoutkey:
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'キーが正しくありません %s vs %s' % (playdata.alreadykey if playdata else 'None', scoutkey))
            url = self.makeAppLinkUrlRedirect(UrlMaker.produceevent_top())
            self.appRedirect(url)
            return

        # プレイヤー.
        self.html_param['player'] = Objects.player(self, v_player)

        # ステージ.
        stagemaster = BackendApi.get_produceevent_stagemaster(model_mgr, stageid, using=using)
        if stagemaster is None:
            url = self.makeAppLinkUrlRedirect(UrlMaker.produceevent_top())
            self.appRedirect(url)
            return
        obj_scout = self.makeStageObj(stagemaster, playdata, stagemaster.stage)
        self.html_param['scout'] = obj_scout

        self.putEventTopic(mid)

        eventlist = playdata.result.get('event', [])
        if not eventlist:
            raise CabaretError(u'スカウト実行の実装に問題があります')

        table = (
            (Defines.ScoutEventType.LEVELUP, self.procLevelup),
            (Defines.ScoutEventType.GET_CARD, self.procGetCard),
            (Defines.ScoutEventType.GET_TREASURE, self.procGetTreasure),
            (Defines.ScoutEventType.COMPLETE, self.procComplete),
            (Defines.ScoutEventType.HAPPENING, self.procHappening),
            (Defines.ScoutEventType.AP_NONE, self.procApNone),
            (Defines.ScoutEventType.NONE, self.procNone),
        )

        eventdict = {}
        for event in eventlist:
            eventdict[event.get_type()] = event
        self.__eventdict = eventdict

        # スカウト結果
        resultlist = playdata.result.get('result', [])
        self.html_param['scoutresultinfo'] = BackendApi.make_scoutresult_info(resultlist)

        for eventtype, func in table:
            event = eventdict.get(eventtype)
            if event:
                func(mid, stagemaster, playdata, event)
                return
        raise CabaretError(u'実行可能なスカウト内イベントがありません')

    def __putCompleteData(self, model_mgr, playdata, stagemaster):

        if 0 < stagemaster.boss and BackendApi.check_event_boss_playable(playdata, stagemaster):
            # ボス出現.
            boss = BackendApi.get_boss(model_mgr, stagemaster.boss, using=settings.DB_READONLY)
            self.html_param['boss'] = Objects.boss(self, boss)

            self.setFromPage(Defines.FromPages.PRODUCEEVENTSCOUT, stagemaster.id)
            url = UrlMaker.bosspre(stagemaster.id)
            self.html_param['url_bossbattle'] = self.makeAppLinkUrl(url)
        else:
            nextstagemaster = BackendApi.get_produceevent_next_stagemaster(model_mgr, playdata.mid, stagemaster,
                                                                        using=settings.DB_READONLY)
            if nextstagemaster and nextstagemaster.stage != stagemaster.stage:
                if nextstagemaster.area == stagemaster.area:
                    self.html_param['next_stage'] = nextstagemaster.name
                else:
                    self.html_param['next_area'] = nextstagemaster.areaname
                url = UrlMaker.produceevent_scoutdo(nextstagemaster.id, playdata.confirmkey)
            else:
                url = UrlMaker.produceevent_scoutdo(stagemaster.id, playdata.confirmkey)
            self.html_param['url_next'] = self.makeAppLinkUrl(url)

    def procComplete(self, mid, stagemaster, playdata, event):
        """スカウト完了.
        """
        model_mgr = self.getModelMgr()

        self.__putCompleteData(model_mgr, playdata, stagemaster)

        self.writeHtml(self.eventmaster, 'scout/complete')

    def procLevelup(self, mid, stagemaster, playdata, event):
        """レベルアップ.
        """
        model_mgr = self.getModelMgr()

        v_player = self.getViewerPlayer()
        if event.level != v_player.level:
            url = UrlMaker.produceevent_scoutdo(stagemaster.id, playdata.confirmkey)
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        
        self.html_param['levelup_info'] = BackendApi.make_playerlevelup_info(model_mgr, v_player, using=settings.DB_READONLY)
        
        if self.__eventdict.has_key(Defines.ScoutEventType.COMPLETE):
            self.__putCompleteData(model_mgr, playdata, stagemaster)

        self.writeHtml(self.eventmaster, 'scout/levelup')

    def procGetCard(self, mid, stagemaster, playdata, event):
        """カード獲得.
        """
        if event.is_received:
            # 終了済み.
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'判定済みです', CabaretError.Code.ALREADY_RECEIVED)
            self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.produceevent_scoutcardgetresult(stagemaster.id)))
            return

        model_mgr = self.getModelMgr()

        # 獲得したカード.
        cardid = event.card
        cardmaster = BackendApi.get_cardmasters([cardid], model_mgr, using=settings.DB_READONLY).get(cardid)
        if cardmaster is None:
            raise CabaretError(u'一度公開されたキャストが非公開にされました.危険です.', CabaretError.Code.INVALID_MASTERDATA)
        card = BackendApi.create_card_by_master(cardmaster)
        self.html_param['card'] = Objects.card(self, CardSet(card, cardmaster), is_new=event.is_new)

        # 獲得判定へ飛ぶ.
        url = UrlMaker.produceevent_scoutcardget(stagemaster.id)
        self.html_param['url_exec'] = self.makeAppLinkUrl(url)

        # アイテム.
        BackendApi.put_scoutcard_uselead_info(self, UrlMaker.produceevent_scoutcardget(stagemaster.id))

        self.html_param['num_key'] = Defines.URLQUERY_NUMBER

        self.writeHtml(self.eventmaster, 'scout/cardget')

    def procGetTreasure(self, mid, stagemaster, playdata, event):
        """宝箱発見.
        """
        self.html_param['treasure_view'] = Objects.treasure_view(self, event.treasuretype)

        self.writeHtml(self.eventmaster, 'scout/treasureget')

    def procHappening(self, mid, stagemaster, playdata, event):
        """ハプニング発生.
        """
        model_mgr = self.getModelMgr()
        happeningid = BackendApi.get_current_producehappeningid(model_mgr, playdata.uid, using=playdata.current_db, reflesh=True)
        happeningset = BackendApi.get_producehappening(model_mgr, happeningid, using=playdata.current_db)
        if happeningset is None:
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'ハプニングが発生していません')
            url = UrlMaker.produceevent_top()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return

        happeningraidset = HappeningRaidSet(happeningset)
        self.html_param['happening'] = Objects.producehappening(self, happeningraidset)

        # レイドボス
        raidmaster = BackendApi.get_raid_master(model_mgr, happeningset.master.boss, using=settings.DB_READONLY)
        self.html_param['boss'] = Objects.raidmaster(self, raidmaster, is_produceevent=True)

        self.setFromPage(Defines.FromPages.PRODUCEEVENTSCOUT, (stagemaster.id, urllib.quote(playdata.confirmkey, '')))
        url = UrlMaker.producehappening()

        self.html_param['url_happening'] = self.makeAppLinkUrl(url)

        self.writeHtml(self.eventmaster, 'scout/happening')

    def procApNone(self, mid, stagemaster, playdata, event):
        """行動力が足りない.
        """
        v_player = self.getViewerPlayer()

        is_full = BackendApi.get_scoutsearch_flag(v_player.id)
        apcost = BackendApi.get_event_apcost(stagemaster, v_player, is_full)
        if apcost <= v_player.get_ap():
            # 行動力が回復している.
            url = UrlMaker.produceevent_scoutdo(stagemaster.id, playdata.confirmkey)
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return

        self.setFromPage(Defines.FromPages.PRODUCEEVENTSCOUT, (stagemaster.id, urllib.quote(playdata.confirmkey, '')))

        # 回復アイテム.
        BackendApi.put_aprecover_uselead_info(self)

        self.writeHtml(self.eventmaster, 'scout/apnone')

    def procNone(self, mid, stagemaster, playdata, event):
        """なにも起きなかった.
        """
        flag_skip = BackendApi.get_scoutskip_flag(playdata.uid)
        if flag_skip:
            self.writeHtml(self.eventmaster, 'scout/none')
        else:
            url = UrlMaker.produceevent_scoutdo(stagemaster.id, playdata.confirmkey)
            self.appRedirect(self.makeAppLinkUrlRedirect(url))


def main(request):
    return Handler.run(request)
