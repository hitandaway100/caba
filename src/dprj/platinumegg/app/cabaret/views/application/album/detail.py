# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.util.api import BackendApi, Objects
from platinumegg.app.cabaret.util.cabareterror import CabaretError
import settings
import settings_sub
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from defines import Defines
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.models.Player import PlayerRequest, PlayerDeck
from platinumegg.app.cabaret.util.card import CardUtil


class Handler(AppHandler):
    """カード詳細.
    表示するもの.
        カード詳細情報.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerRequest, PlayerDeck]
    
    def process(self):
        args = self.getUrlArgs('/albumdetail/')
        try:
            albumid = int(args.get(0, None))
            hklevel = int(self.request.get(Defines.URLQUERY_HKEVEL) or 1)
        except:
            raise CabaretError(u'リクエストが正しくありません', CabaretError.Code.ILLEGAL_ARGS)
        
        model_mgr = self.getModelMgr()
        
        # プレイヤー情報.
        v_player = self.getViewerPlayer()
        if not BackendApi.check_album_viewable(model_mgr, v_player.id, albumid, using=settings.DB_READONLY):
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'閲覧できません')
            self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.album()))
            return
        
        # カード詳細情報取得.
        cardmasteridlist = BackendApi.get_albumcardmasteridlist(model_mgr, albumid, using=settings.DB_READONLY)
        if not cardmasteridlist:
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'閲覧できません')
            self.appRedirect(self.makeAppLinkUrlRedirect(UrlMaker.album()))
            return
        cardmaster_dict = BackendApi.get_cardmasters(cardmasteridlist, model_mgr, using=settings.DB_READONLY)
        cardmasteridlist.sort()
        
        obj_card_list = []
        obj_card = None
        cur_cardmaster = None
        if 1 < len(cardmasteridlist):
            urlbase = UrlMaker.albumdetail(albumid)
            
            cardacquisitions = BackendApi.get_cardacquisitions(model_mgr, v_player.id, cardmasteridlist, using=settings.DB_READONLY)
            for cardmasterid in cardmasteridlist:
                if not cardacquisitions.get(cardmasterid):
                    continue
                cardmaster = cardmaster_dict[cardmasterid]
                obj = Objects.cardmaster(self, cardmaster)
                obj['url'] = self.makeAppLinkUrl(OSAUtil.addQuery(urlbase, Defines.URLQUERY_HKEVEL, cardmaster.hklevel))
                if obj_card is None or cardmaster.hklevel == hklevel:
                    obj_card = obj
                    cur_cardmaster = cardmaster
                obj_card_list.append(obj)
        self.html_param['cardmasterlist'] = obj_card_list
        self.html_param['cardmaster'] = obj_card
        
        first_cardmaster = cardmaster_dict[cardmasteridlist[0]]
        
        if cur_cardmaster is None:
            cardmasterid = first_cardmaster.id
            cur_cardmaster = first_cardmaster
        self.html_param['card'] = BackendApi.make_album_detail(self, v_player.id, cur_cardmaster, using=settings.DB_READONLY)
        
        # 思い出アルバムリストを取得.
        memories_list = []
        movie_list = []
        pcmovie_list = []
        voice_list = []
        for obj_memories in BackendApi.get_album_memories_list(self, v_player.id, albumid, using=settings.DB_READONLY):
            if obj_memories['contenttype'] == Defines.MemoryContentType.MOVIE:
                movie_list.append(obj_memories)
            elif obj_memories['contenttype'] == Defines.MemoryContentType.MOVIE_PC:
                pcmovie_list.append(obj_memories)
            elif obj_memories['contenttype'] == Defines.MemoryContentType.VOICE:
                voice_list.append(obj_memories)
            else:
                memories_list.append(obj_memories)
        
        # 異動数.
        if first_cardmaster and CardUtil.checkStockableMaster(first_cardmaster, raise_on_error=False):
            stocknum_model = BackendApi.get_cardstock(model_mgr, v_player.id, first_cardmaster.album, using=settings.DB_READONLY)
            stocknum = stocknum_model.num if stocknum_model else 0
            self.html_param['stocknum'] = stocknum
            url = UrlMaker.transferreturn(first_cardmaster.id, v_player.req_confirmkey)
            self.html_param['url_transferreturn'] = self.makeAppLinkUrl(url)
            cardnum = BackendApi.get_cardnum(v_player.id, model_mgr, using=settings.DB_READONLY)
            self.html_param['cardnum'] = cardnum
            self.html_param['cardlimit'] = v_player.cardlimit
        
        self.html_param['memories_list'] = memories_list
        self.html_param['movie_list'] = movie_list
        self.html_param['pcmovie_list'] = pcmovie_list
        self.html_param['voice_list'] = voice_list
        
        # カード詳細情報.
        self.writeAppHtml('album/detail')

def main(request):
    return Handler.run(request)
