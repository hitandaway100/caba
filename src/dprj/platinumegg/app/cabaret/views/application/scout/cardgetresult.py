# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.views.application.scout.base import ScoutHandler
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
        args = self.getUrlArgs('/scoutcardgetresult/')
        try:
            scoutid = int(args.get(0))
        except:
            raise CabaretError(u'引数が想定外です', CabaretError.Code.ILLEGAL_ARGS)
        
        v_player = self.getViewerPlayer()
        model_mgr = self.getModelMgr()
        
        using = settings.DB_READONLY
        
        # 進行情報.
        playdata = BackendApi.get_scoutprogress(model_mgr, v_player.id, [scoutid], using=using).get(scoutid, None)
        target_event = BackendApi.find_scout_event(playdata, Defines.ScoutEventType.GET_CARD)
        
        if target_event is None:
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'女の子を発見していません')
            url = self.makeAppLinkUrlRedirect(UrlMaker.scout())
            self.appRedirect(url)
            return
        elif not target_event.is_received:
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'まだ女の子をスカウトしていません')
            url = self.makeAppLinkUrlRedirect(UrlMaker.scoutresult(scoutid, playdata.alreadykey))
            self.appRedirect(url)
            return
        
        # プレイヤー.
        self.html_param['player'] = Objects.player(self, v_player)
        
        # 獲得したカード.
        cardmaster = BackendApi.get_cardmasters([target_event.card], arg_model_mgr=model_mgr, using=using).get(target_event.card)
        card = BackendApi.create_card_by_master(cardmaster)
        cardset = CardSet(card, cardmaster)
        self.html_param['card'] = Objects.card(self, cardset, is_new=target_event.is_new)
        
        # スカウト.
        arr = BackendApi.get_scouts(model_mgr, [scoutid], using=using)
        scoutmaster = arr[0] if arr else None
        self.html_param['scout'] = self.makeScoutObj(scoutmaster, playdata)
        
        # スカウト結果.
        resultlist = playdata.result.get('result', [])
        self.html_param['scoutresultinfo'] = BackendApi.make_scoutresult_info(resultlist)
        
        # レイドイベント.
        BackendApi.put_raidevent_champagnedata(self, v_player.id)
        
        if target_event.is_success:
            if target_event.autosell:
                # 自動退店.
                self.html_param['autosell'] = target_event.autosell
                self.html_param['_gold_add'] = target_event.sellprice
                self.html_param['_ckt'] = getattr(target_event, 'sellprice_treasure', 0)
            
            self.writeAppHtml('scout/cardgetresult_success')
        else:
            self.writeAppHtml('scout/cardgetresult_failed')
    

def main(request):
    return Handler.run(request)
