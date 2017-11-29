# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.views.application.battleevent.base import BattleEventBaseHandler
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util import db_util
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.cabareterror import CabaretError
import settings_sub
import datetime
from platinumegg.app.cabaret.util.datetime_util import DateTimeUtil
import settings
from defines import Defines

class Handler(BattleEventBaseHandler):
    """バトルイベントログインボーナス受け取り.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        
        eventmaster = self.getCurrentBattleEvent()
        if not self.checkBattleEventUser(do_check_battle_open=False, do_check_loginbonus=False):
            return
        
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        uid = v_player.id
        
        # ランクレコード取得.
        rankrecord = self.getCurrentBattleRankRecord()
        
        # 更新確認.
        config = BackendApi.get_current_battleeventconfig(self.getModelMgr(), using=settings.DB_READONLY)
        now = OSAUtil.get_now()
        received_data = None
        if rankrecord.isNeedUpdate(config, now=now):
            # 書き込み.
            try:
                model_mgr, received_data = db_util.run_in_transaction(Handler.tr_write, eventmaster, uid, now)
                model_mgr.write_end()
            except CabaretError, err:
                if settings_sub.IS_LOCAL:
                    raise err
                else:
                    url = self.makeAppLinkUrlRedirect(UrlMaker.battleevent_top(eventmaster.id))
                    self.appRedirect(url)
                    return
        elif 1 < len(rankrecord.groupidlist):
            # 前日の結果を取得.
            groupid_yesterday = rankrecord.groupidlist[-2]
            group_yesterday = BackendApi.get_battleevent_grouplog(model_mgr, groupid_yesterday, using=settings.DB_READONLY)
            if group_yesterday:
                rankmaster = BackendApi.get_battleevent_rankmaster_byId(model_mgr, group_yesterday.rankid, using=settings.DB_READONLY)
                if rankmaster:
                    fame = 0
                    for data in group_yesterday.userdata:
                        if data.uid == uid:
                            fame = data.fame
                            break
                    
                    received_data = {
                        'fame' : rankrecord.fame - fame,
                        'fame_next' : rankrecord.fame,
                        'rank' : rankmaster.rank,
                        'rank_next' : rankrecord.rank,
                    }
        
        basetime = DateTimeUtil.toLoginTime(OSAUtil.get_now())
        yesterday = datetime.date(basetime.year, basetime.month, basetime.day) - datetime.timedelta(days=1)
        target_grouplog = None
        for grouplog in BackendApi.get_battleevent_grouplog_dict(model_mgr, rankrecord.groups, using=settings.DB_READONLY).values():
            if grouplog.cdate == yesterday:
                target_grouplog = grouplog
                break
        if target_grouplog is None:
            url = self.makeAppLinkUrlRedirect(UrlMaker.battleevent_top(eventmaster.id))
            self.appRedirect(url)
            return
        elif eventmaster.is_goukon:
            # 合コンでは演出はない.
            if self.getFromPageName() == Defines.FromPages.BATTLEEVENT:
                args = self.getFromPageArgs()
                mid = int(args[0]) if args and str(args[0]).isdigit() else None
                url = self.makeAppLinkUrlRedirect(UrlMaker.battleevent_top(mid))
            else:
                url = self.makeAppLinkUrlRedirect(UrlMaker.mypage())
            self.appRedirect(url)
            return
        elif received_data is None:
            url = self.makeAppLinkUrlRedirect(UrlMaker.battleevent_top(eventmaster.id))
            self.appRedirect(url)
            return
        
        # 演出へ飛ばす.
        fame = received_data['fame']
        fame_next = received_data['fame_next']
        rank = received_data['rank']
        rank_next = received_data['rank_next']
        grouprank = BackendApi.get_battleevent_grouprank(model_mgr, target_grouplog, uid, using=settings.DB_READONLY)
        url = UrlMaker.battleevent_loginbonusanim(eventmaster.id, fame, fame_next, rank, rank_next, grouprank)
        self.appRedirect(self.makeAppLinkUrlRedirect(url))
    
    @staticmethod
    def tr_write(eventmaster, uid, now):
        model_mgr = ModelRequestMgr()
        received_data = BackendApi.tr_battleevent_receive_loginbonus(model_mgr, eventmaster, uid, now)
        model_mgr.write_all()
        return model_mgr, received_data

def main(request):
    return Handler.run(request)
