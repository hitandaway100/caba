# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.views.application.scoutevent.base import ScoutHandler
from defines import Defines
from platinumegg.app.cabaret.util.card import CardSet
import settings_sub
from platinumegg.app.cabaret.models.Player import PlayerExp, PlayerDeck


class Handler(ScoutHandler):
    """スカウトカード獲得結果.
    引数:
        実行したスカウトのID.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerExp, PlayerDeck]
    
    def process(self):
        args = self.getUrlArgs('/sceventcardgetresult/')
        try:
            stageid = int(args.get(0))
        except:
            raise CabaretError(u'引数が想定外です', CabaretError.Code.ILLEGAL_ARGS)
        
        v_player = self.getViewerPlayer()
        model_mgr = self.getModelMgr()
        
        using = settings.DB_READONLY
        
        eventmaster = BackendApi.get_current_scouteventmaster(model_mgr, using=using)
        if eventmaster is None:
            raise CabaretError(u'Event Closed.', CabaretError.Code.EVENT_CLOSED)
        mid = eventmaster.id
        
        # 進行情報.
        playdata = BackendApi.get_event_playdata(model_mgr, mid, v_player.id, using)
        target_event = BackendApi.find_scout_event(playdata, Defines.ScoutEventType.GET_CARD)
        
        if target_event is None:
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'女の子を発見していません')
            url = self.makeAppLinkUrlRedirect(UrlMaker.scoutevent())
            self.appRedirect(url)
            return
        elif not target_event.is_received:
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'まだ女の子をスカウトしていません')
            url = self.makeAppLinkUrlRedirect(UrlMaker.scouteventresult(stageid, playdata.alreadykey))
            self.appRedirect(url)
            return
        
        # プレイヤー.
        self.html_param['player'] = Objects.player(self, v_player)
        
        # 獲得したカード.
        cardmaster = BackendApi.get_cardmasters([target_event.card], arg_model_mgr=model_mgr, using=using).get(target_event.card)
        card = BackendApi.create_card_by_master(cardmaster)
        cardset = CardSet(card, cardmaster)
        self.html_param['card'] = Objects.card(self, cardset, is_new=target_event.is_new)
        
        # ステージ.
        arr = BackendApi.get_event_stages(model_mgr, [stageid], using=using)
        stagemaster = arr[0] if arr else None
        self.html_param['scout'] = self.makeStageObj(stagemaster, playdata, stagemaster.stage)
        
        # フィーバー
        self.html_param['scouteventfever'] = Objects.scoutevent_fever(playdata)
        
        # スカウト結果.
        resultlist = playdata.result.get('result', [])
        self.html_param['scoutresultinfo'] = BackendApi.make_scoutresult_info(resultlist)
        
        # イベントポイント
        self.putEventPoint(mid, v_player.id, playdata)
        
        config = BackendApi.get_current_scouteventconfig(model_mgr, using=settings.DB_READONLY)
        obj_scouteventmaster = Objects.scouteventmaster(self, eventmaster, config)
        self.html_param['scoutevent'] = obj_scouteventmaster
        
        if target_event.is_success:
            if target_event.autosell:
                # 自動退店.
                self.html_param['autosell'] = target_event.autosell
                self.html_param['_gold_add'] = target_event.sellprice
                self.html_param['_ckt'] = getattr(target_event, 'sellprice_treasure', 0)
            
            self.writeScoutEventHTML('cardgetresult_success', eventmaster)
        else:
            self.writeScoutEventHTML('cardgetresult_failed', eventmaster)
    

def main(request):
    return Handler.run(request)