# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from defines import Defines
import settings
from platinumegg.lib.opensocial.util import OSAUtil


class Handler(AppHandler):
    """キャスト名鑑.
    表示するもの.
        カード詳細へのURL.
        サムネイルのURL.
    """
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def getAlbumPageNumMax(self, model_mgr, ctype, rare):
        nummax = BackendApi.get_album_content_nummax(model_mgr, ctype, rare, using=settings.DB_READONLY)
        page = max(1, int((nummax + Defines.ALBUM_PAGE_CONTENT_NUM - 1) / Defines.ALBUM_PAGE_CONTENT_NUM))
        return page
    
    def process(self):
        
        v_player = self.getViewerPlayer()
        
        client = OSAUtil.get_cache_client()
        
        ctype = Defines.CharacterType.ALL
        rare = Defines.Rarity.ALL
        page = 0
        if self.request.method == 'GET':
            namespacebase = 'albumlistargs:%s'
            ctype = client.get(v_player.id, namespace=namespacebase % 'ctype') or ctype
            rare = client.get(v_player.id, namespace=namespacebase % 'rare') or rare
            page = client.get(v_player.id, namespace=namespacebase % 'page') or page
        
        try:
            ctype = int(self.request.get(Defines.URLQUERY_CTYPE, ctype))
            rare = int(self.request.get(Defines.URLQUERY_RARE, rare))
            page = int(self.request.get(Defines.URLQUERY_PAGE, page))
        except:
            ctype = Defines.CharacterType.ALL
            rare = Defines.Rarity.ALL
            page = 0
        
        model_mgr = self.getModelMgr()
        
        # プレイヤー情報.
        v_player = self.getViewerPlayer()
        
        # アルバム情報取得.
        offset = page * Defines.ALBUM_PAGE_CONTENT_NUM
        limit = Defines.ALBUM_PAGE_CONTENT_NUM + 1
        albumlist = BackendApi.get_album_list(self, v_player.id, ctype, rare, offset, limit, using=settings.DB_READONLY)
        has_nextpage = Defines.ALBUM_PAGE_CONTENT_NUM < len(albumlist)
        albumlist = albumlist[:Defines.ALBUM_PAGE_CONTENT_NUM]
        
        # アルバムリスト.
        self.html_param['album_list'] = albumlist
        self.html_param['cur_page'] = page + 1
        self.html_param['page_max'] = self.getAlbumPageNumMax(model_mgr, ctype, rare)
        
        self.html_param['ctype'] = ctype
        self.html_param['rare'] = rare
        
        url_base = UrlMaker.album()
        self.html_param['url_post'] = self.makeAppLinkUrl(url_base)
        
        url_base = OSAUtil.addQuery(url_base, Defines.URLQUERY_CTYPE, ctype)
        url_base = OSAUtil.addQuery(url_base, Defines.URLQUERY_RARE, rare)
        if 0 < page:
            self.html_param['url_page_prev'] = self.makeAppLinkUrl(OSAUtil.addQuery(url_base, Defines.URLQUERY_PAGE, page-1))
        if has_nextpage:
            self.html_param['url_page_next'] = self.makeAppLinkUrl(OSAUtil.addQuery(url_base, Defines.URLQUERY_PAGE, page+1))
        
        namespacebase = 'albumlistargs:%s'
        client.set(v_player.id, ctype, namespace=namespacebase % 'ctype')
        client.set(v_player.id, rare, namespace=namespacebase % 'rare')
        client.set(v_player.id, page, namespace=namespacebase % 'page')
        
        self.writeAppHtml('album/album')

def main(request):
    return Handler.run(request)
