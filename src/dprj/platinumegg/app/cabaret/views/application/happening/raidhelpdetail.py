# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.models.Player import PlayerAp,\
    PlayerExp, PlayerFriend, PlayerTreasure, PlayerRequest
from platinumegg.app.cabaret.views.application.happening.base import HappeningHandler
from platinumegg.app.cabaret.util.api import Objects, BackendApi
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.lib.opensocial.util import OSAUtil
from defines import Defines
from platinumegg.app.cabaret.util.cabareterror import CabaretError
import settings_sub
import settings
from platinumegg.app.cabaret.util.happening import HappeningRaidSet,\
    HappeningUtil
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr


class Handler(HappeningHandler):
    """救援詳細.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerAp, PlayerExp, PlayerFriend, PlayerTreasure, PlayerRequest]
    
    def __redirectWithError(self, url, msg):
        self.osa_util.logger.error('raidhelpdetail\n%s\n%s\nredirect:%s' % (self.request.uri, msg, url))
        self.appRedirect(url)
    
    def process(self):
        
        args = self.getUrlArgs('/raidhelpdetail/')
        raidid = str(args.get(0, ''))
        
        if not raidid.isdigit():
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'レイドIDの指定がおかしい')
            self.__redirectWithError(self.makeAppLinkUrlRedirect(UrlMaker.happening()), u'Illegal ID.')
            return
        raidid = int(raidid)
        
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        uid = v_player.id
        
        # レイド情報.
        raidboss = BackendApi.get_raid(model_mgr, raidid, using=settings.DB_READONLY)
        if raidboss is None:
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'存在しないレイド')
            raidlog = BackendApi.get_raidlog_by_raidid(model_mgr, uid, raidid, using=settings.DB_READONLY)
            if raidlog:
                self.__redirectWithError(self.makeAppLinkUrlRedirect(UrlMaker.raidlogdetail(raidlog.id)), u'Raid not Found.')
            else:
                self.__redirectWithError(self.makeAppLinkUrlRedirect(UrlMaker.happening()), u'Raid not Found and Log not Found.')
            return
        elif raidboss.raid.oid == uid:
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'自分のレイド')
            self.__redirectWithError(self.makeAppLinkUrlRedirect(UrlMaker.happening()), u'Mine.')
            return
        
        happeningset = BackendApi.get_happening(model_mgr, raidid, using=settings.DB_READONLY)
        is_end = False
        if happeningset.happening.is_active():
            # 参加可能かを確認.
            if not BackendApi.check_raid_joinable(model_mgr, raidboss, uid, using=settings.DB_READONLY):
                # もう一度開催確認.
                happeningset = BackendApi.get_happening(ModelRequestMgr(), raidid, using=settings.DB_DEFAULT)
                if happeningset.happening.is_active():
                    if settings_sub.IS_LOCAL:
                        raise CabaretError(u'参加できないレイド')
                    self.__redirectWithError(self.makeAppLinkUrlRedirect(UrlMaker.happening()), u'Cannot Join.')
                    return
                else:
                    # チェック中に終了した.
                    is_end = True
        else:
            is_end = True
        
        BackendApi.reset_raidboss_eventraidmaster(model_mgr, raidboss, happeningset.happening.event, using=settings.DB_READONLY)
        
        # プレイヤー情報.
        self.html_param['player'] = Objects.player(self, v_player)
        
        # ダメージ履歴.
        func_put_attacklog = self.putRaidAttackLog(raidboss)
        # お助け.
        func_put_playerlist = self.putHelpFriend(raidboss)
        
        # ハプニング情報.
        o_players = BackendApi.get_players(self, [happeningset.happening.oid], [], using=settings.DB_READONLY)
        dmmid = ''
        if o_players:
            o_player = o_players[0]
            dmmid = o_player.dmmid
            persons = BackendApi.get_dmmplayers(self, o_players, using=settings.DB_READONLY, do_execute=False)
        else:
            persons = {}
        
        if not is_end:
            # デッキ情報.
            deckcardlist = self.getDeckCardList()
            self.putDeckParams(deckcardlist)
        
        self.execute_api()
        
        obj_happening = Objects.happening(self, HappeningRaidSet(happeningset, raidboss), o_person=persons.get(dmmid))
        self.html_param['happening'] = obj_happening
        
        if func_put_attacklog or func_put_playerlist:
            if func_put_attacklog:
                func_put_attacklog()
            if func_put_playerlist:
                func_put_playerlist()
        
        self.setFromPage(Defines.FromPages.RAID, raidid)
        BackendApi.put_bprecover_uselead_info(self)
        
        self.html_param['url_deck_raid'] = self.makeAppLinkUrl(UrlMaker.deck_raid())
        
        # 実行Url.
        url = UrlMaker.raiddo(raidboss.id, v_player.req_confirmkey)
        self.html_param['url_exec_strong'] = self.makeAppLinkUrl(OSAUtil.addQuery(url, Defines.URLQUERY_STRONG, 1))
        self.html_param['url_exec'] = self.makeAppLinkUrl(url)
        self.html_param['url_trade'] = self.makeAppLinkUrl(UrlMaker.trade(), add_frompage=True)
        
        cur_eventmaster = BackendApi.get_current_raideventmaster(model_mgr, using=settings.DB_READONLY)
        eventid = HappeningUtil.get_raideventid(happeningset.happening.event)
        if cur_eventmaster and cur_eventmaster.id == eventid:
            # イベント情報.
            config = BackendApi.get_current_raideventconfig(model_mgr, using=settings.DB_READONLY)
            self.html_param['raidevent'] = Objects.raidevent(self, cur_eventmaster, config)
            
            # イベントデータ.
            scorerecord = BackendApi.get_raidevent_scorerecord(model_mgr, cur_eventmaster.id, uid, using=settings.DB_READONLY)
            rank = BackendApi.get_raidevent_rank(cur_eventmaster.id, uid)
            self.html_param['raideventscore'] = Objects.raidevent_score(cur_eventmaster, scorerecord, rank)
            
            # 特攻カード.
            raideventraidmaster = BackendApi.get_raidevent_raidmaster(model_mgr, cur_eventmaster.id, raidboss.master.id, using=settings.DB_READONLY)
            BackendApi.put_raidevent_specialcard_info(self, uid, raideventraidmaster, using=settings.DB_READONLY)
            
            self.html_param['url_raidevent_top'] = self.makeAppLinkUrl(UrlMaker.raidevent_top(cur_eventmaster.id))
            
            self.html_param['is_end'] = is_end
            
            self.writeAppHtml('raidevent/bossappear')
        elif is_end:
            self.writeAppHtml('raid/helpend')
        else:
            self.writeAppHtml('raid/helpdetail')
    

def main(request):
    return Handler.run(request)
