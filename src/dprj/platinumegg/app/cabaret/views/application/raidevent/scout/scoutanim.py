# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.views.application.raidevent.base import RaidEventBaseHandler
import urllib
from platinumegg.app.cabaret.util.scout import ScoutEventNone
from defines import Defines
import settings_sub


class Handler(RaidEventBaseHandler):
    """スカウト実行演出.
    引数:
        実行したスカウトのID.
        確認キー.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        args = self.getUrlArgs('/raideventscoutanim/')
        try:
            stageid = int(args.get(0))
            scoutkey = urllib.unquote(args.get(1))
        except:
            raise CabaretError(u'引数が想定外です', CabaretError.Code.ILLEGAL_ARGS)
        
        v_player = self.getViewerPlayer()
        uid = v_player.id
        
        model_mgr = self.getModelMgr()
        
        using = settings.DB_READONLY
        
        eventmaster = BackendApi.get_current_raideventmaster(model_mgr, using=using)
        if eventmaster is None:
            raise CabaretError(u'Event Closed.', CabaretError.Code.EVENT_CLOSED)
        mid = eventmaster.id
        
        # 進行情報.
        playdata = BackendApi.get_raideventstage_playdata(model_mgr, mid, uid, using=using)
        if playdata and playdata.confirmkey == scoutkey:
            # DBからとり直すべき.
            playdata = BackendApi.get_raideventstage_playdata(model_mgr, mid, uid, using=settings.DB_DEFAULT, reflesh=True)
        
        if playdata is None or playdata.alreadykey != scoutkey:
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'キーが正しくありません %s vs %s' % (playdata.alreadykey if playdata else 'None', scoutkey))
            url = self.makeAppLinkUrlRedirect(UrlMaker.raidevent_top())
            self.appRedirect(url)
            return
        
        eventlist = playdata.result.get('event', [])
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
            backUrl = UrlMaker.raidevent_scoutdo(stageid, playdata.confirmkey)
        elif eventKind in (Defines.ScoutEventType.LEVELUP, Defines.ScoutEventType.COMPLETE, Defines.ScoutEventType.HAPPENING):
            # 結果表示へ.
            backUrl = UrlMaker.raidevent_scoutresultanim(stageid, scoutkey, 0)
        
        # 結果表示へ.
        backUrl = backUrl or UrlMaker.raidevent_scoutresult(stageid, scoutkey)
        
        # 演出のパラメータ.
        stagemaster = BackendApi.get_raidevent_stagemaster(model_mgr, stageid, using=using)
        resultlist = playdata.result.get('result', [])
        params = BackendApi.make_scoutanim_params(self, stagemaster, eventlist, resultlist)
        if params is None:
            # 演出不要.
            self.appRedirect(self.makeAppLinkUrlRedirect(backUrl))
            return
        
        # 演出用パラメータ.
        dataUrl = self.makeAppLinkUrlEffectParamGet('raideventscout/%d/%s' % (stageid, urllib.quote(playdata.alreadykey, '')))
        self.appRedirectToEffect2('scoutevent/scout/effect2.html', dataUrl)

def main(request):
    return Handler.run(request)
