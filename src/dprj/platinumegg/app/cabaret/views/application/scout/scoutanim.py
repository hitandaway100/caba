# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.views.application.scout.base import ScoutHandler
import urllib
from platinumegg.app.cabaret.util.scout import ScoutEventNone
from defines import Defines
import settings_sub


class Handler(ScoutHandler):
    """スカウト実行演出.
    引数:
        実行したスカウトのID.
        確認キー.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        args = self.getUrlArgs('/scoutanim/')
        try:
            scoutid = int(args.get(0))
            scoutkey = urllib.unquote(args.get(1))
        except:
            raise CabaretError(u'引数が想定外です', CabaretError.Code.ILLEGAL_ARGS)
        
        v_player = self.getViewerPlayer()
        model_mgr = self.getModelMgr()
        uid = v_player.id
        
        using = settings.DB_READONLY
        
        # 進行情報.
        playdata = BackendApi.get_scoutprogress(model_mgr, uid, [scoutid], using=using).get(scoutid, None)
        if playdata and playdata.confirmkey == scoutkey:
            # DBからとり直すべき.
            playdata = BackendApi.get_scoutprogress(model_mgr, v_player.id, [scoutid], using=settings.DB_DEFAULT, reflesh=True).get(scoutid, None)
        
        if playdata is None or playdata.alreadykey != scoutkey:
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'キーが正しくありません %s vs %s' % (playdata.alreadykey if playdata else 'None', scoutkey))
            url = self.makeAppLinkUrlRedirect(UrlMaker.scout())
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
            backUrl = UrlMaker.scoutdo(scoutid, playdata.confirmkey)
        elif eventKind in (Defines.ScoutEventType.LEVELUP, Defines.ScoutEventType.COMPLETE, Defines.ScoutEventType.HAPPENING):
            # 結果表示へ.
            backUrl = UrlMaker.scoutresultanim(scoutid, scoutkey, 0)
        
        # 結果表示へ.
        backUrl = backUrl or UrlMaker.scoutresult(scoutid, scoutkey)
        
        # 演出のパラメータ.
        scoutmaster = BackendApi.get_scouts(model_mgr, [scoutid], using=using)[0]
        resultlist = playdata.result.get('result', [])
        params = BackendApi.make_scoutanim_params(self, scoutmaster, eventlist, resultlist)
        if params is None:
            # 演出不要.
            self.appRedirect(self.makeAppLinkUrlRedirect(backUrl))
            return
        
#        params['backUrl'] = self.makeAppLinkUrl(backUrl)
#        self.appRedirectToEffect('scout/effect.html', params)
        
        # 演出用パラメータ.
        dataUrl = self.makeAppLinkUrlEffectParamGet('scout/%d/%s' % (scoutid, urllib.quote(playdata.alreadykey, '')))
        self.appRedirectToEffect2('scout/effect2.html', dataUrl)

def main(request):
    return Handler.run(request)
