# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.util.api import BackendApi
import settings
import settings_sub
from platinumegg.app.cabaret.util.redisdb import MemoriesSession
from defines import Defines
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.kpi.operator import KpiOperator
from platinumegg.lib.opensocial.util import OSAUtil


class Handler(AppHandler):
    """セッションチェックしてRTMPのパスを返す
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def __sendErrorResponse(self, status):
        self.response.set_status(status)
        self.response.end()
    
    def process(self):
        args = self.getUrlArgs('/movie/keyget/')
        try:
            mid = int(args.get(0, None))
        except:
            self.__sendErrorResponse(404)
            return
        
        model_mgr = self.getModelMgr()
        
        # プレイヤー確認.
        remote_addr = self.request.remote_addr
        
        if remote_addr and remote_addr.find('10.116.41.') == 0:
            # rewriteで転送された.
            remote_addr = self.request.django_request.META.get('HTTP_X_FORWARDED_FOR')
        
        keys = None
        if remote_addr:
            keys = [
                '%s##%s' % (remote_addr, self.osa_util.useragent.browser),
                '%s##%s##%s' % (remote_addr, self.osa_util.useragent.browser, self.osa_util.useragent.version),
            ]
        memories_session_data = None
        if keys:
            for key in keys:
                memories_session_data = MemoriesSession.get(key)
                if memories_session_data:
                    break
        
        playlistmaster = None
        if memories_session_data:
            memories_id = memories_session_data.mid
            memoriesmaster = BackendApi.get_memoriesmasters([memories_id], model_mgr, using=settings.DB_READONLY).get(memories_id)
            if memoriesmaster and memoriesmaster.contenttype == Defines.MemoryContentType.MOVIE_PC and mid == int(memoriesmaster.contentdata):
                # ファイル名.
                playlistmaster = BackendApi.get_pcmovieplaylist_master(model_mgr, mid, using=settings.DB_READONLY)
                
                # 閲覧回数加算
                def tr_write(mid):
                    """書き込み.
                    """
                    model_mgr = ModelRequestMgr()
                    BackendApi.tr_add_pcmovieviewdata(model_mgr, mid)
                    model_mgr.write_all()
                    return model_mgr
                
                def writeEnd():
                    kpi = KpiOperator()
                    kpi.set_incrment_pcmovieview_count(memories_id)
                    kpi.save()
                
                model_mgr = db_util.run_in_transaction(tr_write, memories_id)
                model_mgr.add_write_end_method(writeEnd)
                model_mgr.write_end()
        
        if playlistmaster is None:
            eventmovie_session_data = BackendApi.get_eventmovie_sessiondata(self)
            playlistmaster = None
            if eventmovie_session_data and eventmovie_session_data.get('is_pc'):
                eventmovie_id = eventmovie_session_data.get('mid')
                if eventmovie_id:
                    eventmoviemaster = BackendApi.get_eventmovie_master(model_mgr, eventmovie_id, using=settings.DB_READONLY)
                    if eventmoviemaster:
                        filename = eventmoviemaster.pc
                        playlistmaster = BackendApi.get_pcmovieplaylist_dict_by_uniquename(model_mgr, [filename], using=settings.DB_READONLY).get(filename)
            
            if playlistmaster is None:
                self.osa_util.logger.error("Invalid session. %s" % self.osa_util.session)
                self.__sendErrorResponse(400)
                return
        
        self.response.set_header('Content-Type', 'plain/text')
        self.response.set_status(200)
        self.response.send(self.makeAppLinkRtmpUrl(playlistmaster.filename))
    
    def makeAppLinkRtmpUrl(self, filename):
        #url = 'rtmp://%s:%s/cabaret_quest/mp4:%s.mp4' % (settings_sub.WOWZA_HOST, settings_sub.WOWZA_PORT, filename)
        wowza_host = settings_sub.WOWZA_HOST
        if wowza_host.find('127.0.0.1') != -1:
            protocol = 'rtmp'
        else:
            protocol = 'rtmps'
        url = '%s://%s:%s/cabaret_quest/mp4:%s.mp4' % (protocol, wowza_host, settings_sub.WOWZA_PORT, filename)
        return OSAUtil.addQuery(url, OSAUtil.KEY_APP_ID, self.osa_util.appparam.app_id)
    
def main(request):
    return Handler.run(request)
