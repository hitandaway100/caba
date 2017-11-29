# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.models.Player import PlayerAp, PlayerGold,\
    PlayerExp, PlayerFriend
from platinumegg.app.cabaret.views.application.happening.base import HappeningHandler
import settings_sub
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from defines import Defines
from platinumegg.app.cabaret.util.happening import HappeningUtil


class Handler(HappeningHandler):
    """ハプニング終わり.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerAp, PlayerGold, PlayerExp, PlayerFriend]
    
    def process(self):
        
        args = self.getUrlArgs('/happeningend/')
        
        model_mgr = self.getModelMgr()
        
        happeningid = str(args.get(0, ''))
        happeningraid = None
        if happeningid.isdigit():
            happeningraid = BackendApi.get_happeningraidset(model_mgr, int(happeningid), using=settings.DB_READONLY)
        if happeningraid is None:
            raise CabaretError(u'ハプニングが見つかりません', CabaretError.Code.ILLEGAL_ARGS)
        
        # プレイヤー情報.
        v_player = self.getViewerPlayer()
        
        happeningset = happeningraid.happening
        raideventid = HappeningUtil.get_raideventid(happeningset.happening.event)
        if happeningset.happening.is_end() and not happeningset.happening.is_missed_and_not_end():
            pass
        else:
            if happeningset.happening.is_cleared():
                if v_player.id == happeningset.happening.oid:
                    # 終了書き込みをさせる.
                    if settings_sub.IS_LOCAL:
                        raise CabaretError(u'まだ終わっていません')
                    url = UrlMaker.raidend(happeningset.happening.id)
                    self.appRedirect(self.makeAppLinkUrlRedirect(url))
                    return
                else:
                    pass
            elif happeningset.happening.is_missed_and_not_end():
                if v_player.id == happeningset.happening.oid:
                    # 終了書き込みをさせる.
                    if settings_sub.IS_LOCAL and not self.request.get('_test'):
                        raise CabaretError(u'終了処理を行っていません')
                    elif raideventid:
                        self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.happening()))
                        return
                    else:
                        self.writeHappeningMissed(happeningset.id)
                else:
                    pass
            else:
                if settings_sub.IS_LOCAL:
                    raise CabaretError(u'まだ終わっていません')
                url = UrlMaker.happening()
                self.appRedirect(self.makeAppLinkUrlRedirect(url))
                return
        
        eventmaster = None
        if raideventid:
            eventmaster = BackendApi.get_raideventmaster(model_mgr, raideventid, using=settings.DB_READONLY)
        
        if eventmaster:
            # イベント開催中.
            self.html_param['url_raidevent_top'] = self.makeAppLinkUrl(UrlMaker.raidevent_top(eventmaster.id))
            self.html_param['prize'] = None
            
            if eventmaster.flag_dedicated_stage:
                self.html_param['url_raidevent_scouttop'] = self.makeAppLinkUrl(UrlMaker.raidevent_scouttop())
            
            if happeningset.happening.is_canceled():
                # キャンセル.
                self.html_param['cancel'] = True
                self.writeAppHtml('raidevent/failed')
            elif happeningset.happening.is_missed():
                # 失敗.
                self.html_param['cancel'] = False
                self.writeAppHtml('raidevent/failed')
            else:
                # 成功.
                url = UrlMaker.raidend(happeningset.happening.id)
                self.appRedirect(self.makeAppLinkUrlRedirect(url))
                return
        else:
            model_mgr = self.getModelMgr()
            
            # スカウトイベント.
            scouteventmaster = BackendApi.get_current_scouteventmaster(model_mgr, using=settings.DB_READONLY)
            if scouteventmaster:
                scouteventconfig = BackendApi.get_current_scouteventconfig(model_mgr, using=settings.DB_READONLY)
                self.html_param['scoutevent'] = Objects.scouteventmaster(self, scouteventmaster, scouteventconfig)
                self.html_param['url_scoutevent_scouttop'] = self.makeAppLinkUrl(UrlMaker.scoutevent())
            
            # ハプニングの報酬.
            prizeinfo = None
            if v_player.id == happeningset.happening.oid:
                prizelist = self.getPooledPrizeList(happeningset.happening.is_canceled())
                if prizelist:
                    prizeinfo = BackendApi.make_prizeinfo(self, prizelist, using=settings.DB_READONLY)
            
            # 成否.
            if happeningset.happening.state in (Defines.HappeningState.END, Defines.HappeningState.CLEAR):
                
                # ハプニング情報.
                self.html_param['happening'] = Objects.happening(self, happeningraid, prizeinfo)
                
                # レイドの報酬.
                self.html_param['raidprize'] = Objects.raidprize(self, v_player, happeningraid.raidboss, happeningset.happening.items.get('dropitems', []))
                
                self.writeAppHtml('happening/prizeget')
            else:
                self.html_param['prize'] = prizeinfo
                self.html_param['cancel'] = happeningset.happening.is_canceled()
                self.writeAppHtml('happening/failed')

def main(request):
    return Handler.run(request)
