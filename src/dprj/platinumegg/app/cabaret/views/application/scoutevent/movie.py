# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings
from platinumegg.app.cabaret.views.application.scoutevent.base import ScoutHandler


class Handler(ScoutHandler):
    """スカウトイベント動画ページ.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        model_mgr = self.getModelMgr()
        
        # 引数.
        args = self.getUrlArgs('/sceventmovie/')
        stage = args.getInt(0)
        
        # イベントマスターID.
        eventmaster = self.getCurrentScoutEvent(do_check_schedule=True)
        eventid = eventmaster.id
        
        # 対象のステージ.
        eventstagemaster = None
        if stage:
            eventstagemaster = BackendApi.get_event_stage_by_stagenumber(model_mgr, eventid, stage, using=settings.DB_READONLY)
        
        # 動画の閲覧可否.
        eventmovieid = None
        if stage == 0 and eventmaster.movie_op:
            # オープニング用.
            eventmovieid = eventmaster.movie_op
        elif eventstagemaster and eventstagemaster.movie:
            # イベント進行状況.
            v_player = self.getViewerPlayer()
            uid = v_player.id
            playdata = BackendApi.get_event_playdata(model_mgr, eventid, uid, using=settings.DB_READONLY)
            if stage < playdata.stage:
                eventmovieid = eventstagemaster.movie
        
        eventmoviemaster = None
        if eventmovieid:
            eventmoviemaster = BackendApi.get_eventmovie_master(model_mgr, eventmovieid, using=settings.DB_READONLY)
        
        # イベント情報.
        config = BackendApi.get_current_scouteventconfig(model_mgr, using=settings.DB_READONLY)
        self.html_param['scoutevent'] = Objects.scouteventmaster(self, eventmaster, config)
        
        if eventmoviemaster:
            # 動画詳細.
            self.__procDetail(eventmaster, eventstagemaster, eventmoviemaster)
        else:
            # 動画一覧.
            self.__procList(eventmaster)
    
    def __procList(self, eventmaster):
        """動画一覧.
        """
        self.__putMovieList(eventmaster)
        
        # HTML出力.
        self.writeScoutEventHTML('ev_album', eventmaster)
    
    def __procDetail(self, eventmaster, eventstagemaster, eventmoviemaster):
        """動画詳細.
        """
        v_player = self.getViewerPlayer()
        
        uid = v_player.id
        eventmovieid = eventmoviemaster.id
        
        # HTML用オブジェクトを作成.
        htmlobj = BackendApi.make_eventmovie_htmlobj_dict(self, uid, [eventmovieid], [eventmovieid]).get(eventmovieid)
        self.html_param['eventmovie'] = htmlobj
        
        # 閲覧用のセッションを作成.
        BackendApi.save_eventmovie_sessiondata(self, uid, eventmovieid, 'scoutevent', self.is_pc)
        
        # 閲覧回数を加算.
        BackendApi.add_eventmovie_viewcount(uid, eventmovieid, self.is_pc)
        
        self.__putMovieList(eventmaster)
        # HTML出力.
        self.writeScoutEventHTML('ev_memories', eventmaster)
    
    def __putMovieList(self, eventmaster):
        """動画リストを埋め込み.
        """
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        
        uid = v_player.id
        eventid = eventmaster.id
        
        # イベント進行情報.
        playdata = BackendApi.get_event_playdata(model_mgr, eventid, uid, using=settings.DB_READONLY)
        
        # 動画設定のあるステージ.
        eventstagemasterlist = BackendApi.get_event_stage_by_stagenumber(model_mgr, eventid, using=settings.DB_READONLY)
        eventstagemasterlist.sort(key=lambda x:x.stage)
        
        movie_eventstagemasterlist = []
        opened_movie_idlist = []
        next_movie_stage = None
        newbie_stage = 0
        
        if eventmaster.movie_op:
            opened_movie_idlist.append(eventmaster.movie_op)
        
        for eventstagemaster in eventstagemasterlist:
            if eventstagemaster.movie < 1:
                # 動画設定がないステージ.
                continue
            elif playdata.stage <= eventstagemaster.stage:
                # 未クリアのステージ.
                if next_movie_stage:
                    # 次に開放される動画が設定されている.
                    break
                next_movie_stage = eventstagemaster
            else:
                opened_movie_idlist.append(eventstagemaster.movie)
                newbie_stage = eventstagemaster.stage
            movie_eventstagemasterlist.append(eventstagemaster)
        
        # HTML用オブジェクトを作成.
        htmlobj_dict = BackendApi.make_eventmovie_htmlobj_dict(self, uid, opened_movie_idlist + ([next_movie_stage.movie] if next_movie_stage else []), opened_movie_idlist)
        htmlobj_list = []
        def addObj(mid, stage):
            htmlobj = htmlobj_dict.get(mid)
            if htmlobj is None:
                return
            htmlobj = dict(htmlobj)
            htmlobj['stage'] = stage
            htmlobj['url'] = self.makeAppLinkUrl(UrlMaker.scoutevent_movie(stage))
            htmlobj_list.append(htmlobj)
        
        if eventmaster.movie_op:
            addObj(eventmaster.movie_op, 0)
        for eventstagemaster in movie_eventstagemasterlist:
            addObj(eventstagemaster.movie, eventstagemaster.stage)
        
        self.html_param['url_eventmovie_top'] = self.makeAppLinkUrl(UrlMaker.scoutevent_movie())
        self.html_param['url_eventmovie_detail'] = self.makeAppLinkUrl(UrlMaker.scoutevent_movie(newbie_stage))
        
        self.html_param['eventmovielist'] = htmlobj_list

def main(request):
    return Handler.run(request)
