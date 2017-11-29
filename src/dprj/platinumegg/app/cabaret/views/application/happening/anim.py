# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.views.application.happening.base import HappeningHandler
import settings_sub
from platinumegg.app.cabaret.util.url_maker import UrlMaker
import urllib
from platinumegg.app.cabaret.util.scout import ScoutEventNone
from defines import Defines
from platinumegg.app.cabaret.models.Player import PlayerHappening, PlayerRequest
from platinumegg.app.cabaret.util.api import BackendApi


class Handler(HappeningHandler):
    """ハプニング実行アニメ.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerHappening, PlayerRequest]
    
    def process(self):
        args = self.getUrlArgs('/happeninganim/')
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
        
        master = self.getHappeningMaster()
        resultlist = v_player.happening_result.get('result', [])
        eventlist = v_player.happening_result.get('event', [])
        
        if eventlist:
            # ここで必要なのははじめの１件.
            event = eventlist[0]
        else:
            # なにも起きなかった.
            event = ScoutEventNone.create()
        
        eventKind = event.get_type()
        backUrl = None
        
        # イベント毎の設定.
        if eventKind == Defines.ScoutEventType.NONE:
            # そのままもう一回.
            backUrl = UrlMaker.happeningdo()
        elif eventKind in (Defines.ScoutEventType.LEVELUP, Defines.ScoutEventType.COMPLETE):
            # 結果表示へ.
            backUrl = UrlMaker.happeningresultanim(key)
        
        # 結果表示へ.
        backUrl = backUrl or UrlMaker.happeningresult(key)
        
        params = BackendApi.make_scoutanim_params(self, master, eventlist, resultlist)
        if params is None:
            # 演出不要.
            self.appRedirect(self.makeAppLinkUrlRedirect(backUrl))
            return
        
        params['backUrl'] = self.makeAppLinkUrl(backUrl)
        self.appRedirectToEffect('scout/effect.html', params)

def main(request):
    return Handler.run(request)
