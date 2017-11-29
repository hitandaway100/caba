# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.util.api import BackendApi, Objects
import settings


class Handler(AppHandler):
    """動画再生用のプレイリストを返す.
    """
    
    @classmethod
    def get_default_status(cls):
        """デフォルトで返すHttpStatus.
        """
        return 500
    
    def processError(self, error_message):
        self.response.set_status(500)
        self.response.end()
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def __sendErrorResponse(self):
        self.response.set_status(404)
        self.response.end()
    
    def process(self):
        args = self.getUrlArgs('/albummovie/')
        try:
            mid = int(args.get(0, None))
        except:
            self.__sendErrorResponse()
            return
        
        model_mgr = self.getModelMgr()
        
        # プレイヤー情報.
        v_player = self.getViewerPlayer()
        
        cardmaster = None
        memoriesmaster = BackendApi.get_memoriesmasters([mid], model_mgr, using=settings.DB_READONLY).get(mid)
        if memoriesmaster is not None:
            cardmaster = BackendApi.get_cardmasters([memoriesmaster.cardid], model_mgr, using=settings.DB_READONLY).get(memoriesmaster.cardid)
            card_acquisition = BackendApi.get_cardacquisitions(model_mgr, v_player.id, [cardmaster.id], using=settings.DB_READONLY).get(cardmaster.id)
        if cardmaster is None:
            self.__sendErrorResponse()
            return
        
        # 閲覧時間.
        obj_album = Objects.memoriesmaster(self, memoriesmaster, card_acquisition)
        if not obj_album['acquisition']:
            self.__sendErrorResponse()
            return
        
        # プレイリスト.
        playlistmaster = BackendApi.get_movieplaylist_master(model_mgr, int(memoriesmaster.contentdata), using=settings.DB_READONLY)
        playlist_data = playlistmaster.data.replace('{{url_media__}}', self.url_media)
        
        self.response.set_header('Content-Type', 'application/x-mpegURL')
        self.response.set_status(200)
        self.response.send(playlist_data)

def main(request):
    return Handler.run(request)
