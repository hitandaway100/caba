# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.models.Player import PlayerAp, PlayerGold,\
    PlayerExp, PlayerFriend, PlayerHappening
from platinumegg.app.cabaret.views.application.happening.base import HappeningHandler
import settings_sub
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.api import BackendApi, Objects
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.happening import HappeningUtil


class Handler(HappeningHandler):
    """ハプニング諦める.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerAp, PlayerGold, PlayerExp, PlayerFriend, PlayerHappening]
    
    def process(self):
        
        happeningset = self.getHappening()
        if happeningset is None:
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'ハプニングが見つかりません')
            url = UrlMaker.happening()
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        elif happeningset.happening.is_end() or happeningset.happening.is_cleared():
            # 終了済み.
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'終了済みです')
            url = UrlMaker.happeningend(happeningset.happening.id)
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        
        args = self.getUrlArgs('/happeningcancel/')
        procname = args.get(0)
        table = {
            'yesno' : self.procYesno,
            'do' : self.procDo,
        }
        func = table.get(procname)
        if func:
            func()
        else:
            raise CabaretError(u'不正なアクセスです', CabaretError.Code.ILLEGAL_ARGS)
    
    def procYesno(self):
        """諦める確認.
        """
        # プレイヤー情報.
        v_player = self.getViewerPlayer()
        self.html_param['player'] = Objects.player(self, v_player)
        
        # ハプニング情報.
        self.putHappeningInfo()
        
        self.html_param['url_happening'] = self.makeAppLinkUrl(UrlMaker.happening())
        self.html_param['url_raidevent_battlepre'] = self.makeAppLinkUrl(UrlMaker.raidevent_battlepre())
        
        # 書き込みへのURL.
        url = UrlMaker.happeningcancel_do()
        self.html_param['url_happeningcancel_do'] = self.makeAppLinkUrl(url)
        
        happeningset = self.getHappening()
        eventid = HappeningUtil.get_raideventid(happeningset.happening.event)
        self.writeHtmlSwitchEvent('cancelyesno', eventid)
    
    def procDo(self):
        """書き込み.
        """
        # プレイヤー.
        v_player = self.getViewerPlayer()
        
        # マスターデータ.
        master = self.getHappeningMaster()
        
        # 書き込み.
        try:
            model_mgr = db_util.run_in_transaction(self.tr_write, v_player.id, master)
            model_mgr.write_end()
        except CabaretError, e:
            if e.code == CabaretError.Code.ALREADY_RECEIVED:
                pass
            else:
                raise
        # 結果へ.
        happeningset = self.getHappening()
        url = UrlMaker.happeningend(happeningset.id)
        self.appRedirect(self.makeAppLinkUrlRedirect(url))
    
    def tr_write(self, uid, happeningmaster):
        """書き込み.
        """
        model_mgr = ModelRequestMgr()
        player = BackendApi.get_players(self, [uid], [PlayerExp], model_mgr=model_mgr)[0]
        BackendApi.tr_happening_cancel(model_mgr, player, happeningmaster)
        model_mgr.write_all()
        return model_mgr

def main(request):
    return Handler.run(request)
