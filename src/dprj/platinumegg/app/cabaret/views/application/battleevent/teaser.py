# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from defines import Defines
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr

class Handler(AppHandler):
    """ティザーページ.
    合コンイベントのみ.
    """
    
    def process(self):
        args = self.getUrlArgs('/battleeventteaser/')
        mid = args.getInt(0)
        
        def redirectToMypage():
            self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.mypage()))
        
        model_mgr = self.getModelMgr()
        now = OSAUtil.get_now()
        config = BackendApi.get_current_battleeventconfig(model_mgr, using=settings.DB_READONLY)
        mid = mid or config.mid
        
        eventmaster = BackendApi.get_battleevent_master(model_mgr, config.mid, using=settings.DB_READONLY)
        if eventmaster is None or not eventmaster.is_goukon:
            # 合コンイベントじゃない.
            redirectToMypage()
            return
        
        # ティザー期間判定.
        is_teaser_open = config.mid == mid and now < config.starttime
        self.html_param['is_teaser_open'] = is_teaser_open
        
        # イベント情報.
        self.html_param['battleevent'] = Objects.battleevent(self, eventmaster, now)
        
        if is_teaser_open:
            # ティザー期間中.
            v_player = self.getViewerPlayer()
            rankrecord = BackendApi.get_battleevent_rankrecord(model_mgr, eventmaster.id, v_player.id, using=settings.DB_READONLY)
            if rankrecord:
                # 登録済み.
                self.__procRegistered(config, eventmaster, rankrecord)
            else:
                self.__procNotRegistered(config, eventmaster)
            if self.response.isEnd:
                return
        
        self.writeAppHtml('gcevent/teaser_info')
    
    def __procNotRegistered(self, config, eventmaster):
        """未登録状態.
        """
        model_mgr = self.getModelMgr()
        # 公開中のランク.
        rankmaster_list = BackendApi.get_battleevent_rankmaster_by_eventid(model_mgr, eventmaster.id, using=settings.DB_READONLY)
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
                    db_util.run_in_transaction(self.tr_write, eventmaster, uid, rank).write_end()
                except:
                    pass
                
                # 書き込み後はリダイレクト.
                url = UrlMaker.battleevent_teaser(eventmaster.id)
                self.appRedirect(self.makeAppLinkUrlRedirect(url))
                return
        
        # 各ランクの情報.
        obj_rank_list = []
        rankmaster_list.sort(key=lambda x:x.rank, reverse=True)
        for rankmaster in rankmaster_list:
            obj_rank = BackendApi.make_battleevent_rank_selectobj(self, rankmaster)
            obj_rank_list.append(obj_rank)
        self.html_param['battleevent_rank_select'] = obj_rank_list
        
        # 書き込み実行URL.
        url = UrlMaker.battleevent_teaser()
        self.html_param['url_do'] = self.makeAppLinkUrl(url)
    
    def __procRegistered(self, config, eventmaster, rankrecord):
        """登録済.
        """
        model_mgr = self.getModelMgr()
        # 選択したランクの情報.
        rankmaster = BackendApi.get_battleevent_rankmaster(model_mgr, eventmaster.id, rankrecord.rank, using=settings.DB_READONLY)
        self.html_param['battleevent_rank_selectobj'] = BackendApi.make_battleevent_rank_selectobj(self, rankmaster)
    
    def tr_write(self, eventmaster, uid, rank):
        """書き込み.
        """
        model_mgr = ModelRequestMgr()
        BackendApi.tr_battleevent_regist_from_teaser(model_mgr, eventmaster, uid, rank)
        model_mgr.write_all()
        return model_mgr

def main(request):
    return Handler.run(request)
