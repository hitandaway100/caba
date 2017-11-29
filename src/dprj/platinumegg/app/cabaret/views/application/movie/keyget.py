# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.util.api import BackendApi
import settings
from platinumegg.app.cabaret.util.redisdb import MemoriesSession
import binascii
from defines import Defines
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.kpi.operator import KpiOperator


class Handler(AppHandler):
    """動画の暗号化キーを取得.
    """
    
    @classmethod
    def get_default_status(cls):
        """デフォルトで返すHttpStatus.
        """
        return 500
    
    def processError(self, error_message):
        self.response.set_status(500)
        self.response.end()
    
    def __sendErrorResponse(self, status):
        self.response.set_status(status)
        self.response.end()
    
    def checkUser(self):
        pass
    
    def check_process_pre(self):
        flag = False
        if self.is_pc:
            flag = True
        elif not self.osa_util.useragent.is_smartphone():
            pass
        elif self.osa_util.useragent.is_ios():
            flag = True
        elif self.osa_util.useragent.is_android():
            flag = True
        else:
            flag = self.osa_util.is_dbg
        if not flag:
            self.__sendErrorResponse(400)
        return flag
    
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
            if memoriesmaster and memoriesmaster.contenttype == Defines.MemoryContentType.MOVIE and mid == int(memoriesmaster.contentdata):
                playlistmaster = BackendApi.get_movieplaylist_master(model_mgr, mid, using=settings.DB_READONLY)
                
                # 閲覧回数加算
                def tr_write(mid):
                    """書き込み.
                    """
                    model_mgr = ModelRequestMgr()
                    BackendApi.tr_add_movieviewdata(model_mgr, mid)
                    model_mgr.write_all()
                    return model_mgr
                
                def writeEnd():
                    kpi = KpiOperator()
                    kpi.set_incrment_movieview_count(memories_id)
                    kpi.save()
                
                model_mgr = db_util.run_in_transaction(tr_write, memories_id)
                model_mgr.add_write_end_method(writeEnd)
                model_mgr.write_end()
        
        if playlistmaster is None:
            eventmovie_session_data = BackendApi.get_eventmovie_sessiondata(self)
            playlistmaster = None
            if eventmovie_session_data and not eventmovie_session_data.get('is_pc'):
                eventmovie_id = eventmovie_session_data.get('mid')
                if eventmovie_id:
                    eventmoviemaster = BackendApi.get_eventmovie_master(model_mgr, eventmovie_id, using=settings.DB_READONLY)
                    if eventmoviemaster:
                        filename = eventmoviemaster.sp
                        playlistmaster = BackendApi.get_movieplaylist_dict_by_uniquename(model_mgr, [filename], using=settings.DB_READONLY).get(filename)
            
            if playlistmaster is None:
                self.osa_util.logger.error("Invalid session. %s" % self.osa_util.session)
                self.__sendErrorResponse(400)
                return
        
        # 鍵.
        data = binascii.a2b_hex(playlistmaster.data)
        
        self.response.set_header('Content-Type', 'plain/text')
        self.response.set_status(200)
        self.response.send(data)
    

def main(request):
    return Handler.run(request)
