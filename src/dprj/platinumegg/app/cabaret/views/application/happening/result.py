# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.views.application.happening.base import HappeningHandler
import settings_sub
from platinumegg.app.cabaret.util.url_maker import UrlMaker
import urllib
from defines import Defines
import settings
from platinumegg.app.cabaret.util.api import BackendApi, Objects
from platinumegg.app.cabaret.models.Player import PlayerAp, PlayerFriend,\
    PlayerExp, PlayerGold, PlayerDeck, PlayerHappening, PlayerTreasure,\
    PlayerRequest


class Handler(HappeningHandler):
    """ハプニング結果.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerAp, PlayerFriend, PlayerExp, PlayerGold, PlayerDeck, PlayerHappening, PlayerTreasure, PlayerRequest]
    
    def process(self):
        args = self.getUrlArgs('/happeningresult/')
        try:
            key = urllib.unquote(args.get(0))
        except:
            raise CabaretError(u'引数が想定外です', CabaretError.Code.ILLEGAL_ARGS)
        
        v_player = self.getViewerPlayer()
        
        # 進行情報.
        if v_player.req_alreadykey != key:
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'キーが正しくありません %s vs %s' % (v_player.req_alreadykey, key))
            url = self.makeAppLinkUrlRedirect(UrlMaker.happening())
            self.appRedirect(url)
            return
        
        self.html_param['player'] = Objects.player(self, v_player)
        
        # ハプニング.
        self.putHappeningInfo()
        
        # 続ける.
        url = UrlMaker.happeningdo(v_player.req_confirmkey)
        self.html_param['url_exec'] = self.makeAppLinkUrl(url)
        
        # 諦める.
        url = UrlMaker.happeningcancel_yesno()
        self.html_param['url_happeningcancel_yesno'] = self.makeAppLinkUrl(url)
        
        # レイド.
        self.putRaidHelpList()
        
        eventlist = v_player.happening_result.get('event', [])
        if not eventlist:
            raise CabaretError(u'ハプニング実行の実装に問題があります')
        
        table = (
            (Defines.ScoutEventType.AP_NONE, self.procApNone),
            (Defines.ScoutEventType.GET_ITEM, self.procGetItem),
        )
        
        eventdict = {}
        for event in eventlist:
            eventdict[event.get_type()] = event
        self.__eventdict = eventdict
        
        for eventtype, func in table:
            event = eventdict.get(eventtype)
            if event:
                func(event)
                return
        raise CabaretError(u'実行可能なハプニング内イベントがありません')
    
    def procGetItem(self, event):
        """アイテム獲得.
        """
        model_mgr = self.getModelMgr()
        
        # 獲得したアイテム.
        itemmaster = BackendApi.get_itemmaster(model_mgr, event.item, using=settings.DB_READONLY)
        if itemmaster is None:
            raise CabaretError(u'一度公開されたアイテムが非公開にされました.危険です.', CabaretError.Code.INVALID_MASTERDATA)
        self.html_param['item'] = Objects.itemmaster(self, itemmaster)
        
        self.writeAppHtml('happening/itemget')
    
    def procApNone(self, event):
        """行動力が足りない.
        """
        v_player = self.getViewerPlayer()
        
        master = self.getHappeningMaster()
        apcost = BackendApi.get_apcost(master, v_player)
        if apcost <= v_player.get_ap():
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'行動力が回復している')
            # 行動力が回復している.
            url = UrlMaker.happeningdo()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        
        self.setFromPage(Defines.FromPages.HAPPENING)
        
        # 回復アイテム.
        BackendApi.put_aprecover_uselead_info(self)
        
        self.writeAppHtml('happening/apnone')

def main(request):
    return Handler.run(request)
