# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from platinumegg.app.cabaret.views.application.battleevent.base import BattleEventBaseHandler
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.models.Player import PlayerExp
from platinumegg.app.cabaret.util.datetime_util import DateTimeUtil
from platinumegg.lib.opensocial.util import OSAUtil
import datetime
from defines import Defines
import settings_sub


class Handler(BattleEventBaseHandler):
    """バトルイベント参加.
    バトル公開中だけ受け付ける.
    バトル公開中にグループに所属していないユーザーが対象.
    合コンイベントの時は登録ページ.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerExp]
    
    def process(self):
        
        eventmaster = self.getCurrentBattleEvent()
        if not self.checkBattleEventUser(do_check_regist=False, do_check_loginbonus=False):
            return
        
        if eventmaster.is_goukon:
            self.__procGoukon(eventmaster)
        else:
            self.__procNormal(eventmaster)
    
    def __procGoukon(self, eventmaster):
        """合コンバトルイベント.
        """
        model_mgr = self.getModelMgr()
        eventid = eventmaster.id
        
        basetime = DateTimeUtil.toLoginTime(OSAUtil.get_now())
        cdate = datetime.date(basetime.year, basetime.month, basetime.day)
        cur_group = self.getCurrentBattleGroup(do_search_log=False)
        
        # 設定済みの場合はイベントTOPへリダイレクト.
        if cur_group and cur_group.cdate == cdate:
            url = UrlMaker.battleevent_top(eventmaster.id)
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        
        # 最大ランク.
        config = BackendApi.get_current_battleeventconfig(model_mgr, using=settings.DB_READONLY)
        
        # 公開中のランク.
        rankmaster_list = BackendApi.get_battleevent_rankmaster_by_eventid(model_mgr, eventid, using=settings.DB_READONLY)
        rankmaster_list.sort(key=lambda x:x.rank)
        
        # 未設定で引数がある場合は書き込み.
        rank = str(self.request.get(Defines.URLQUERY_ID))
        if rank.isdigit():
            rank = int(rank)
            # ランクの公開確認.
            target_rankmaster = None
            for rankmaster in rankmaster_list:
                if rankmaster.rank == rank:
                    target_rankmaster = rankmaster
                    break
            if target_rankmaster:
                # 登録書き込み.
                v_player = self.getViewerPlayer()
                uid = v_player.id
                try:
                    db_util.run_in_transaction(self.tr_write, config, eventmaster, uid, v_player.level, rankmaster_list, rank).write_end()
                except CabaretError, err:
                    if err.code == CabaretError.Code.ALREADY_RECEIVED:
                        pass
                    elif settings_sub.IS_DEV:
                        raise
                    else:
                        url = UrlMaker.mypage()
                        self.appRedirect(self.makeAppLinkUrlRedirect(url))
                        return
                
                # 書き込み後はイベントTOPへ.
                url = UrlMaker.battleevent_top(eventmaster.id)
                self.appRedirect(self.makeAppLinkUrlRedirect(url))
                return
        
        # 未設定で引数がない場合は選択ページ.
        # イベント情報.
        self.html_param['battleevent'] = Objects.battleevent(self, eventmaster)
        
        # 各ランクの情報.
        obj_rank_list = []
        rankmaster_list.sort(key=lambda x:x.rank, reverse=True)
        for rankmaster in rankmaster_list:
            obj_rank = BackendApi.make_battleevent_rank_selectobj(self, rankmaster)
            obj_rank_list.append(obj_rank)
        self.html_param['battleevent_rank_select'] = obj_rank_list
        
        # 書き込み実行URL.
        url = UrlMaker.battleevent_regist()
        self.html_param['url_do'] = self.makeAppLinkUrl(url)
        
        self.putEventTopic(eventmaster.id)
        
        self.writeAppHtml('gcevent/start')
    
    def __procNormal(self, eventmaster):
        """通常のバトルイベント.
        """
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        uid = v_player.id
        eventid = eventmaster.id
        
        # 最大ランク.
        config = BackendApi.get_current_battleeventconfig(model_mgr, using=settings.DB_READONLY)
        
        # 公開中のランク.
        rankmaster_list = BackendApi.get_battleevent_rankmaster_by_eventid(model_mgr, eventid, using=settings.DB_READONLY)
        rankmaster_list.sort(key=lambda x:x.rank)
        
        try:
            db_util.run_in_transaction(self.tr_write, config, eventmaster, uid, v_player.level, rankmaster_list).write_end()
        except CabaretError, err:
            if err.code == CabaretError.Code.ALREADY_RECEIVED:
                pass
            else:
                url = UrlMaker.mypage()
                self.appRedirect(self.makeAppLinkUrlRedirect(url))
                return
        
        url = UrlMaker.battleevent_top()
        self.appRedirect(self.makeAppLinkUrlRedirect(url))
    
    def tr_write(self, config, eventmaster, uid, level, rankmaster_list, target_rank=None):
        """書き込み.
        """
        model_mgr = ModelRequestMgr()
        BackendApi.tr_battleevent_regist_group_for_user(model_mgr, config, eventmaster, uid, level, rankmaster_list, target_rank=target_rank)
        model_mgr.write_all()
        return model_mgr
    
    

def main(request):
    return Handler.run(request)
