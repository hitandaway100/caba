# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.views.application.scoutevent.base import ScoutHandler
import urllib
from defines import Defines
import settings_sub


class Handler(ScoutHandler):
    """スカウト結果.
    引数:
        実行したスカウトのID.
        確認キー.
        結果のindex.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        self.__swf_params = {}
        
        args = self.getUrlArgs('/sceventresultanim/')
        try:
            stageid = int(args.get(0))
            scoutkey = urllib.unquote(args.get(1))
            index = int(args.get(2) or 0)
        except:
            raise CabaretError(u'引数が不正です', CabaretError.Code.ILLEGAL_ARGS)
        
        v_player = self.getViewerPlayer()
        model_mgr = self.getModelMgr()
        
        using = settings.DB_READONLY
        
        flag_skip = BackendApi.get_scoutskip_flag(v_player.id)
        
        eventmaster = BackendApi.get_current_scouteventmaster(model_mgr, using=using)
        if eventmaster is None:
            raise CabaretError(u'Event Closed.', CabaretError.Code.EVENT_CLOSED)
        mid = eventmaster.id
        
        # 進行情報.
        playdata = BackendApi.get_event_playdata(model_mgr, mid, v_player.id, using)
        if playdata and playdata.confirmkey == scoutkey:
            # DBからとり直すべき.
            playdata = BackendApi.get_event_playdata(model_mgr, mid, v_player.id, using=settings.DB_DEFAULT, reflesh=True)
        
        if playdata is None or playdata.alreadykey != scoutkey:
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'キーが正しくありません %s vs %s' % (playdata.alreadykey if playdata else 'None', scoutkey))
            url = self.makeAppLinkUrlRedirect(UrlMaker.scoutevent())
            self.appRedirect(url)
            return
        
        eventlist = playdata.result.get('event', [])[index:]
        if not eventlist:
            raise CabaretError(u'引数が不正です', CabaretError.Code.ILLEGAL_ARGS)
        
        table = {
            Defines.ScoutEventType.COMPLETE : (self.procComplete, False),
            Defines.ScoutEventType.LEVELUP : (self.procLevelup, True),
            Defines.ScoutEventType.HAPPENING : (self.procHappening, True),
        }
        
        proc = None
        next_event = None
        for idx, event in enumerate(eventlist):
            next_event = eventlist[idx+1] if (idx + 1) < len(eventlist) else None
            tmp = table.get(event.get_type(), None)
            if tmp is None:
                index += idx
                break
            tmp_proc, is_skipok = tmp
            if flag_skip and is_skipok:
                continue
            index += idx
            proc = tmp_proc
            break
        
        if not proc:
            url = UrlMaker.scouteventresult(stageid, scoutkey)
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        
        if next_event and table.has_key(next_event.get_type()):
            url = UrlMaker.scouteventresultanim(stageid, scoutkey, index+1)
        else:
            url = UrlMaker.scouteventresult(stageid, scoutkey)
        
        self.__swf_params['backUrl'] = self.makeAppLinkUrl(url)
        
        self.__playdata = playdata
        proc(event)
    
    def procComplete(self, event):
        """スカウト完了演出.
        """
        self.__swf_params['text'] = Defines.EffectTextFormat.SCOUTRESULT_COMPLETE_TEXT
        self.appRedirectToEffect('scoutclear/effect.html', self.__swf_params)
    
    def procLevelup(self, event):
        """レベルアップ演出.
        """
        resulttexts = []
        
        # レベル情報.
        resulttexts.append(Defines.EffectTextFormat.LEVELUP_STATUSTEXT % event.level)
        
        self.__swf_params['statusText'] = u'\n'.join(resulttexts)
        
        self.appRedirectToEffect('levelup/effect.html', self.__swf_params)
    
    def procHappening(self, event):
        """ハプニング発生演出.
        """
        self.appRedirectToEffect('chohutokyaku/effect.html', self.__swf_params)

def main(request):
    return Handler.run(request)