# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from defines import Defines
from platinumegg.app.cabaret.util.card import CardSet
import settings_sub
from platinumegg.app.cabaret.models.Player import PlayerExp, PlayerDeck
from platinumegg.app.cabaret.views.application.produce_event.base import ProduceEventBaseHandler


class Handler(ProduceEventBaseHandler):
    """スカウトカード獲得結果.
    引数:
        実行したスカウトのID.
    """

    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerExp, PlayerDeck]

    def process(self):
        args = self.getUrlArgs('/produceeventscoutcardgetresult/')
        try:
            stageid = int(args.get(0))
        except:
            raise CabaretError(u'引数が想定外です', CabaretError.Code.ILLEGAL_ARGS)

        v_player = self.getViewerPlayer()
        model_mgr = self.getModelMgr()

        using = settings.DB_READONLY

        eventmaster = BackendApi.get_current_produce_event_master(model_mgr, using=using)
        if eventmaster is None:
            raise CabaretError(u'Event Closed.', CabaretError.Code.EVENT_CLOSED)
        mid = eventmaster.id

        # 進行情報.
        playdata = BackendApi.get_produceeventstage_playdata(model_mgr, mid, v_player.id, using)
        target_event = BackendApi.find_scout_event(playdata, Defines.ScoutEventType.GET_CARD)

        if target_event is None:
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'女の子を発見していません')
            url = self.makeAppLinkUrlRedirect(UrlMaker.produceevent_scouttop())
            self.appRedirect(url)
            return
        elif not target_event.is_received:
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'まだ女の子をスカウトしていません')
            url = self.makeAppLinkUrlRedirect(UrlMaker.produceevent_scoutresult(stageid, playdata.alreadykey))
            self.appRedirect(url)
            return

        # プレイヤー.
        self.html_param['player'] = Objects.player(self, v_player)

        # 獲得したカード.
        cardmaster = BackendApi.get_cardmasters([target_event.card], arg_model_mgr=model_mgr, using=using).get(
            target_event.card)
        card = BackendApi.create_card_by_master(cardmaster)
        cardset = CardSet(card, cardmaster)
        self.html_param['card'] = Objects.card(self, cardset, is_new=target_event.is_new)

        # ステージ.
        arr = BackendApi.get_produceevent_stagemaster_list(model_mgr, [stageid], using=using)
        stagemaster = arr[0] if arr else None
        self.html_param['scout'] = self.makeStageObj(stagemaster, playdata, stagemaster.stage)

        # スカウト結果.
        resultlist = playdata.result.get('result', [])
        self.html_param['scoutresultinfo'] = BackendApi.make_scoutresult_info(resultlist)

        # イベントTopのURL.
        url = UrlMaker.produceevent_top(mid)
        self.html_param['url_produceevent_top'] = self.makeAppLinkUrl(url)

        if target_event.is_success:
            if target_event.autosell:
                # 自動退店.
                self.html_param['autosell'] = target_event.autosell
                self.html_param['_gold_add'] = target_event.sellprice
                self.html_param['_ckt'] = getattr(target_event, 'sellprice_treasure', 0)

            self.writeHtml(eventmaster, 'scout/cardgetresult_success')
        else:
            self.writeHtml(eventmaster, 'scout/cardgetresult_failed')


def main(request):
    return Handler.run(request)
