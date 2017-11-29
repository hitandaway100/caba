# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.views.application.battleevent.base import BattleEventBaseHandler
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from defines import Defines

class Handler(BattleEventBaseHandler):
    """バトルイベントログインボーナス演出.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        
        args = self.getUrlArgs('/battleeventloginbonusanim/')
        eventid = args.getInt(0)
#        fame = args.getInt(1)
#        fame_next = args.getInt(2)
        rank = args.getInt(3)
        rank_next = args.getInt(4)
        grouprank = args.getInt(5)
        
        model_mgr = self.getModelMgr()
        
        eventmaster = None
        if eventid and rank and rank_next:
            eventmaster = BackendApi.get_battleevent_master(model_mgr, eventid, using=settings.DB_READONLY)
        if eventmaster is None or eventmaster.is_goukon:
            url = self.makeAppLinkUrlRedirect(UrlMaker.mypage())
            self.appRedirect(url)
            return
        
        # 最大ランクのマスター.
        max_rankmaster = BackendApi.get_battleevent_maxrankmaster(model_mgr, eventid, using=settings.DB_READONLY)
        
        # ランクマスターデータ.
        master_dict = BackendApi.get_battleevent_rankmaster_dict(model_mgr, eventid, list(set([rank, rank_next])), using=settings.DB_READONLY)
        if master_dict.get(rank) is None or master_dict.get(rank_next) is None:
            url = self.makeAppLinkUrlRedirect(UrlMaker.mypage())
            self.appRedirect(url)
            return
        
        if rank < rank_next:
            # ランクアップ.
            effectText0 = Defines.EffectTextFormat.BATTLEEVENT_LOGINBONUS_UP % (master_dict[rank].name, grouprank, master_dict[rank_next].name)
        elif rank == rank_next:
            # ランクステイ.
            effectText0 = Defines.EffectTextFormat.BATTLEEVENT_LOGINBONUS_STAY % (master_dict[rank].name, grouprank, master_dict[rank_next].name)
        else:
            # ランクダウン.
            effectText0 = Defines.EffectTextFormat.BATTLEEVENT_LOGINBONUS_DOWN % (master_dict[rank].name, grouprank, master_dict[rank_next].name)
        
        if max_rankmaster and max_rankmaster.rank == rank_next:
            effectText1 = Defines.EffectTextFormat.BATTLEEVENT_LOGINBONUS_2_RANKMAX
        else:
            effectText1 = Defines.EffectTextFormat.BATTLEEVENT_LOGINBONUS_2
        
        params = {
            'effectText0' : effectText0,
            'effectText1' : effectText1,
            'backUrl' : self.makeAppLinkUrl(UrlMaker.mypage()),
            'pre' : self.url_static_img + 'event/btevent/%s/' % eventmaster.codename,
            'logo_img' : 'scenario/event_logo.png',
            'logo_w_img' : 'scenario/event_logo_w.png',
        }
        self.appRedirectToEffect('btevent/event_result/effect.html', params)

def main(request):
    return Handler.run(request)
