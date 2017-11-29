# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.application.raidevent.base import RaidEventBaseHandler
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from platinumegg.app.cabaret.models.Player import PlayerRequest
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util import db_util
import settings_sub


class Handler(RaidEventBaseHandler):
    """イベントレイド討伐報酬受け取り.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerRequest]
    
    def process(self):
        
        args = self.getUrlArgs('/raideventprizereceive/')
        ope = args.get(0)
        mid = str(args.get(1))
        
        table = {
            'do' : self.__proc_do,
            'anim' : self.__proc_anim,
            'complete' : self.__proc_complete,
        }
        f = table.get(ope)
        if f:
            model_mgr = self.getModelMgr()
            eventmaster = None
            if mid.isdigit():
                mid = int(mid)
                eventmaster = BackendApi.get_raideventmaster(model_mgr, mid, using=settings.DB_READONLY)
            if eventmaster is None:
                raise CabaretError(u'受け取れない報酬です', CabaretError.Code.ILLEGAL_ARGS)
            
            f(args, eventmaster)
        else:
            self.response.set_status(404)
            self.response.end()
    
    def __proc_do(self, args, eventmaster):
        model_mgr = self.getModelMgr()
        confirmkey = args.get(2)
        
        v_player = self.getViewerPlayer()
        if v_player.req_confirmkey != confirmkey:
            if v_player.req_alreadykey == confirmkey:
                # 受取済み.
                pass
            else:
                raise CabaretError(u'ブラウザバックでは受け取れません', CabaretError.Code.ILLEGAL_ARGS)
        else:
            try:
                model_mgr = db_util.run_in_transaction(Handler.tr_write, v_player.id, eventmaster, confirmkey)
                model_mgr.write_end()
            except CabaretError, err:
                if settings_sub.IS_LOCAL:
                    raise
                elif err.code == CabaretError.Code.ALREADY_RECEIVED:
                    pass
                else:
                    raise
        
#        url = UrlMaker.raidevent_prizereceive_anim(eventmaster.id)
        url = UrlMaker.raidevent_prizereceive_complete(eventmaster.id)
        self.appRedirect(self.makeAppLinkUrlRedirect(url))
    
    def __proc_anim(self, args, eventmaster):
        """演出.
        """
        # 演出のパラメータ.
#        effectpath = '%s/prizereceive/effect.html' % eventmaster.effectname
        effectpath = 'levelup/effect.html'
        params = {
            'backUrl' : self.makeAppLinkUrl(UrlMaker.raidevent_prizereceive_complete(eventmaster.id)),
        }
        self.appRedirectToEffect(effectpath, params)
    
    def __proc_complete(self, args, eventmaster):
        """受け取り結果.
        """
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        
        flagrecord = BackendApi.get_raidevent_flagrecord(model_mgr, eventmaster.id, v_player.id, using=settings.DB_READONLY)
        prizeidlist = flagrecord.destroyprize_received
        prizelist = BackendApi.get_prizelist(model_mgr, prizeidlist, using=settings.DB_READONLY)
        self.html_param['prize'] = BackendApi.make_prizeinfo(self, prizelist, using=settings.DB_READONLY)
        
        # イベントTopのURL.
        url = UrlMaker.raidevent_top(eventmaster.id)
        self.html_param['url_raidevent_top'] = self.makeAppLinkUrl(url)
        
        if eventmaster and eventmaster.flag_dedicated_stage:
            url_scout_top = UrlMaker.raidevent_scouttop()
        else:
            url_scout_top = UrlMaker.scout()
        self.html_param['url_scout_top'] = self.makeAppLinkUrl(url_scout_top)
        
        self.writeHtml(eventmaster, 'bonusget')
    
    @staticmethod
    def tr_write(uid, master, confirmkey):
        """書き込み.
        """
        model_mgr = ModelRequestMgr()
        BackendApi.tr_receive_raidevent_destroyprize(model_mgr, uid, master, confirmkey)
        model_mgr.write_all()
        return model_mgr
    

def main(request):
    return Handler.run(request)
