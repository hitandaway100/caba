# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.util import db_util
from platinumegg.app.cabaret.util.api import BackendApi, Objects
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.app.cabaret.util.cabareterror import CabaretError
import settings
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.redisdb import MemoriesSession
from defines import Defines
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.mission import PanelMissionConditionExecuter


class Handler(AppHandler):
    """思い出アルバム閲覧.
    表示するもの.
        思い出アルバム情報.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        args = self.getUrlArgs('/albummemories/')
        try:
            mid = int(args.get(0, None))
        except:
            raise CabaretError(u'リクエストが正しくありません', CabaretError.Code.ILLEGAL_ARGS)
        
        model_mgr = self.getModelMgr()
        
        # プレイヤー情報.
        v_player = self.getViewerPlayer()
        
        cardmaster = None
        memoriesmaster = BackendApi.get_memoriesmasters([mid], model_mgr, using=settings.DB_READONLY).get(mid)
        if memoriesmaster is not None:
            cardmaster = BackendApi.get_cardmasters([memoriesmaster.cardid], model_mgr, using=settings.DB_READONLY).get(memoriesmaster.cardid)
            card_acquisition = BackendApi.get_cardacquisitions(model_mgr, v_player.id, [cardmaster.id], using=settings.DB_READONLY).get(cardmaster.id)
        if cardmaster is None:
            raise CabaretError(u'閲覧できない思い出です', CabaretError.Code.ILLEGAL_ARGS)
        
        # 閲覧時間.
        now = OSAUtil.get_now()
        vtime = BackendApi.get_memories_vtime(model_mgr, v_player.id, [mid], using=settings.DB_READONLY).get(mid, None)
        
        obj_album = Objects.memoriesmaster(self, memoriesmaster, card_acquisition, now)
        if not obj_album['acquisition']:
            raise CabaretError(u'閲覧できない思い出です', CabaretError.Code.ILLEGAL_ARGS)
        
        # 思い出アルバム取得.
        self.html_param['cardmaster'] = Objects.cardmaster(self, cardmaster)
        self.html_param['album'] = obj_album
        
        # 思い出アルバムリストを取得.
        memories_list = []
        movie_list = []
        pcmovie_list = []
        voice_list = []
        for obj_memories in BackendApi.get_album_memories_list(self, v_player.id, cardmaster.album, using=settings.DB_READONLY):
            if obj_memories['contenttype'] == Defines.MemoryContentType.MOVIE:
                movie_list.append(obj_memories)
            elif obj_memories['contenttype'] == Defines.MemoryContentType.MOVIE_PC:
                pcmovie_list.append(obj_memories)
            elif obj_memories['contenttype'] == Defines.MemoryContentType.VOICE:
                voice_list.append(obj_memories)
            else:
                memories_list.append(obj_memories)
        self.html_param['memories_list'] = memories_list
        self.html_param['movie_list'] = movie_list
        self.html_param['pcmovie_list'] = pcmovie_list
        self.html_param['voice_list'] = voice_list
        
        # カード詳細URL.
        self.html_param['url_detail'] = self.makeAppLinkUrl(UrlMaker.albumdetail(cardmaster.album))
        
        # newフラグ更新.
        if vtime is None or now < vtime:
            model_mgr = db_util.run_in_transaction(BackendApi.tr_set_memories_vtime, v_player.id, memoriesmaster)
            model_mgr.write_end()
        else:
            # ミッション.
            mission_executer = PanelMissionConditionExecuter()
            if memoriesmaster.contenttype == Defines.MemoryContentType.IMAGE:
                mission_executer.addTargetViewMemoriesImage()
            elif memoriesmaster.contenttype in (Defines.MemoryContentType.MOVIE, Defines.MemoryContentType.MOVIE_PC):
                mission_executer.addTargetViewMemoriesMovie()
            try:
                model_mgr = db_util.run_in_transaction(Handler.tr_write_mission, v_player.id, mission_executer)
                model_mgr.write_end()
            except:
                pass
        
        # 動画閲覧用のキーを保存.
        remote_addr = self.request.remote_addr
        key = None
        if remote_addr:
            key = '%s##%s' % (remote_addr, self.osa_util.useragent.browser)
            MemoriesSession.create(v_player.id, mid, key).save()
        
        self.writeAppHtml('album/memories')
    
    @staticmethod
    def tr_write_mission(uid, mission_executer):
        """ミッションの書き込み.
        """
        model_mgr = ModelRequestMgr()
        # ミッション.
        is_update = BackendApi.tr_complete_panelmission(model_mgr, uid, mission_executer)
        if not is_update:
            # 更新なし.
            raise CabaretError(u'更新なし')
        model_mgr.write_all()
        return model_mgr
    

def main(request):
    return Handler.run(request)
