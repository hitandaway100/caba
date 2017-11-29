# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.models.Player import PlayerAp, PlayerGold,\
    PlayerExp, PlayerFriend, PlayerTreasure, PlayerHappening, PlayerRequest
from platinumegg.app.cabaret.views.application.happening.base import HappeningHandler
from platinumegg.app.cabaret.util.api import Objects, BackendApi
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.lib.opensocial.util import OSAUtil
from defines import Defines
from platinumegg.app.cabaret.util.cabareterror import CabaretError
import settings
from platinumegg.app.cabaret.util.happening import HappeningUtil


class Handler(HappeningHandler):
    """ハプニングTopページ.
    表示するもの:
        プレイヤー情報.
        ハプニング情報.
        実行URL.
        諦めるURL.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerAp, PlayerGold, PlayerExp, PlayerFriend, PlayerTreasure, PlayerHappening, PlayerRequest]
    
    def process(self):
        
        # プレイヤー情報.
        v_player = self.getViewerPlayer()
        self.html_param['player'] = Objects.player(self, v_player)
        
        # ハプニング情報.
        self.putHappeningInfo()
        
        self.setFromPage(Defines.FromPages.HAPPENING)
        
        model_mgr = self.getModelMgr()
        cur_eventmaster = BackendApi.get_current_raideventmaster(model_mgr, using=settings.DB_READONLY)
        
        # 実行Url.
        happeningset = self.getHappening()
        eventid = HappeningUtil.get_raideventid(happeningset.happening.event) if happeningset else 0
        if happeningset and happeningset.happening.is_missed() and happeningset.happening.state != Defines.HappeningState.MISS:
            # 失敗した.
            if cur_eventmaster and cur_eventmaster.id == eventid:
                url = UrlMaker.raidresultanim(happeningset.id)
            else:
                self.writeHappeningMissed(happeningset.id)
                url = UrlMaker.happening()
            self.appRedirect(self.makeAppLinkUrl(url))
            return
        elif happeningset and not happeningset.happening.is_end():
            
            if happeningset.happening.is_cleared():
                # クリア済み.
                if cur_eventmaster and cur_eventmaster.id == eventid:
                    # イベントレイド.
                    url = UrlMaker.raidresultanim(happeningset.id)
                else:
                    url = UrlMaker.raidend(happeningset.id)
                self.appRedirect(self.makeAppLinkUrl(url, add_frompage=False))
                return
            elif eventid:
                if cur_eventmaster.id == eventid:
                    url = UrlMaker.raidevent_battlepre()
                    self.appRedirect(self.makeAppLinkUrl(url, add_frompage=False))
                    return
                else:
                    # これはデバッグ中だけ起きる想定. ステータスは...メンテでいいかなぁ.
                    raise CabaretError(u'イベントの終了処理が終わっていません', CabaretError.Code.MAINTENANCE)
            else:
                # 救援要請.
                func_raidhelp_callback = self.putRaidHelpList(do_execute=False)
                
                raidboss = self.getRaidBoss()
                if raidboss:
                    # ダメージ履歴.
                    func_put_attacklog = self.putRaidAttackLog(raidboss)
                    # お助け.
                    func_put_playerlist = self.putHelpFriend(raidboss)
                    
                    if func_raidhelp_callback or func_put_attacklog or func_put_playerlist:
                        self.execute_api()
                        if func_raidhelp_callback:
                            func_raidhelp_callback()
                        if func_put_attacklog:
                            func_put_attacklog()
                        if func_put_playerlist:
                            func_put_playerlist()
                    
                    BackendApi.put_bprecover_uselead_info(self)
                    
                    deckcardlist = self.getDeckCardList()
                    self.putDeckParams(deckcardlist)
                    
                    url = UrlMaker.raiddo(raidboss.id, v_player.req_confirmkey)
                    htmlname = 'happening/bossappear'
                    
                    self.html_param['url_exec_strong'] = self.makeAppLinkUrl(OSAUtil.addQuery(url, Defines.URLQUERY_STRONG, 1))
                    
                    self.html_param['url_deck_raid'] = self.makeAppLinkUrl(UrlMaker.deck_raid())
                    
                else:
                    if func_raidhelp_callback:
                        self.execute_api()
                        func_raidhelp_callback()
                    url = UrlMaker.happeningdo(v_player.req_confirmkey)
                    htmlname = 'happening/happening'
                self.html_param['url_exec'] = self.makeAppLinkUrl(url)
                self.html_param['url_happeningcancel_yesno'] = self.makeAppLinkUrl(UrlMaker.happeningcancel_yesno())
        else:
            if cur_eventmaster is not None:
                # イベント.
                eventbanners = BackendApi.get_eventbanners(self, using=settings.DB_READONLY)
                self.html_param['eventbanners'] = [Objects.eventbanner(self, banner) for banner in eventbanners]
            
            # 救援要請.
            self.putRaidHelpList()
            htmlname = 'happening/happening_none'
        
        self.html_param['url_trade'] = self.makeAppLinkUrl(UrlMaker.trade(), add_frompage=True)
        
        self.html_param['is_event_open'] = cur_eventmaster is not None
        
        self.writeAppHtml(htmlname)

def main(request):
    return Handler.run(request)
