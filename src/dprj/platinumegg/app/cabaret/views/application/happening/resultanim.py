# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.views.application.happening.base import HappeningHandler
import settings_sub
from platinumegg.app.cabaret.util.url_maker import UrlMaker
import urllib
from defines import Defines
import settings
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.models.Player import PlayerHappening, PlayerRequest


class Handler(HappeningHandler):
    """ハプニング結果アニメ.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerHappening, PlayerRequest]
    
    def process(self):
        self.__swf_params = {}
        
        args = self.getUrlArgs('/happeningresultanim/')
        try:
            key = urllib.unquote(args.get(0))
            index = int(args.get(1) or 0)
        except:
            raise CabaretError(u'引数が不正です', CabaretError.Code.ILLEGAL_ARGS)
        
        v_player = self.getViewerPlayer()
        
        # 進行情報.
        if v_player.req_alreadykey != key:
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'キーが正しくありません %s vs %s' % (v_player.req_alreadykey, key))
            url = self.makeAppLinkUrlRedirect(UrlMaker.happening())
            self.appRedirect(url)
            return
        
        eventlist = v_player.happening_result.get('event', [])[index:]
        if not eventlist:
            raise CabaretError(u'引数が不正です', CabaretError.Code.ILLEGAL_ARGS)
        
        event = eventlist[0]
        next_event = eventlist[1] if 1 < len(eventlist) else None
        
        eventtype = event.get_type()
        table = {
            Defines.ScoutEventType.LEVELUP : self.procLevelup,
            Defines.ScoutEventType.COMPLETE : self.procComplete,
            Defines.ScoutEventType.GET_ITEM : self.procGetItem,
        }
        if next_event and table.has_key(next_event.get_type()):
            url = UrlMaker.happeningresultanim(key, index+1)
        else:
            if eventtype == Defines.ScoutEventType.GET_ITEM:
                # 結果画面がある.
                url = UrlMaker.happeningresult(key)
            elif eventtype == Defines.ScoutEventType.COMPLETE:
                # ボス戦へ.
                url = UrlMaker.happening()
            else:
                url = UrlMaker.happeningdo(v_player.req_confirmkey)
        
        self.__swf_params['backUrl'] = self.makeAppLinkUrl(url)
        
        proc = table.get(eventtype, None)
        if not proc:
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'アニメーション表示をしないイベント')
            url = UrlMaker.happeningresult(key)
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        proc(event)
    
    def procGetItem(self, event):
        """アイテム獲得演出.
        """
        model_mgr = self.getModelMgr()
        master = BackendApi.get_itemmaster(model_mgr, event.item, using=settings.DB_READONLY)
        if master is None:
            raise CabaretError(u'存在しないアイテムです.id=%d' % event.item, CabaretError.Code.INVALID_MASTERDATA)
        
        # TODO: Flushができてからー.
        resulttexts = [u'アイテム:%sを発見しました' % master.name]
        
        self.html_param['resulttexts'] = resulttexts
        self.html_param.update(**self.__swf_params)
        self.writeAppHtml('scout/dummyresult')
    
    def procComplete(self, event):
        """ハプニングボス出現演出.
        """
        self.appRedirectToEffect('bossencount/effect.html', self.__swf_params)
    
    def procLevelup(self, event):
        """レベルアップ演出.
        """
        resulttexts = []
        
        # レベル情報.
        resulttexts.append(Defines.EffectTextFormat.LEVELUP_STATUSTEXT % event.level)
        
        self.__swf_params['statusText'] = u'\n'.join(resulttexts)
        
        self.appRedirectToEffect('levelup/effect.html', self.__swf_params)

def main(request):
    return Handler.run(request)
