# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.adminhandler import AdminHandler
from platinumegg.app.cabaret.models.View import CardMasterView
import settings
from platinumegg.lib.opensocial.util import OSAUtil
from platinumegg.app.cabaret.util.card import CardUtil
from platinumegg.app.cabaret.util.url_maker import UrlMaker
import settings_sub
from defines import Defines
import urllib
from platinumegg.app.cabaret.models.Memories import MemoriesMaster,\
    PcMoviePlayList, MoviePlayList
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.media import Media

class Handler(AdminHandler):
    """画像確認.
    """
    def process(self):
        
        target = self.request.get("_target")
        str_filterlist = self.request.get("_filter")
        page = int(self.request.get("_page") or 0)
        
        try:
            if self.request.method != "POST":
                str_filterlist = urllib.unquote(str_filterlist)
            arr = str_filterlist.split(',')
            filter_json = {}
            for s in arr:
                k,v = s.split('=')
                if v.isdigit():
                    v = int(v)
                filter_json[k] = v
        except:
            filter_json = None
        
        self.html_param['_target'] = target
        self.html_param['_filter'] = str_filterlist
        
        f = getattr(self, "proc%s" % target, None)
        if f:
            f(filter_json, page)
        if self.response.isEnd:
            return
        
        self.html_param['url_appimage_prefix'] = self.makeAppImgUrl('')
        
        self.writeAppHtml("view_images")
    
    def putData(self, titles, datalist):
        """データ設定設定.
        """
        self.html_param['titles'] = titles
        self.html_param['datalist'] = datalist
    
    def putPagenationData(self, urlbase, page, pagemax):
        """ページング設定.
        """
        def __makePage(index):
            return {
                'num':index + 1,
                'url':self.makeAppLinkUrlAdmin(OSAUtil.addQuery(urlbase, '_page', index)),
            }
        pagination_data = {
            'page_list':[__makePage(p) for p in xrange(0, pagemax)],
            'now_page':__makePage(page),
            'has_next':False,
            'has_prev':False,
        }
        if (page+1) < pagemax:
            pagination_data['next_page'] = __makePage(page + 1)
            pagination_data['has_next'] = True
        if 0 < page:
            pagination_data['prev_page'] = __makePage(page - 1)
            pagination_data['has_prev'] = True
        self.html_param['pagination'] = pagination_data
    
    def procCard(self, filter_json, page):
        """カード画像確認.
        """
        PAGE_CONTENT_NUM = 50
        offset = page * PAGE_CONTENT_NUM
        
        nummax = CardMasterView.count(filters=filter_json, using=settings.DB_READONLY)
        pagemax = int((nummax + PAGE_CONTENT_NUM - 1) / PAGE_CONTENT_NUM)
        
        titles = (
            u'ID',
            u'キャスト',
            u'thumbの値',
            u'Card_thumb_52_52.png',
            u'Card_thumb_60_75.png',
            u'Card_thumb_110_138.png',
            u'Card_thumb_320_400.png',
            u'Card_thumb_320_314.png',
            u'Card_thumb_70_88.png',
        )
        
        cardmasterlist = CardMasterView.fetchValues(filters=filter_json, order_by='id', limit=PAGE_CONTENT_NUM, offset=offset, using=settings.DB_READONLY)
        
        datalist = []
        for cardmaster in cardmasterlist:
            row = [
                cardmaster.id,
                cardmaster.name,
                cardmaster.thumb,
                (self.makeAppImgUrl(CardUtil.makeThumbnailUrlIcon(cardmaster)), 52, 52),
                (self.makeAppImgUrl(CardUtil.makeThumbnailUrlSmall(cardmaster)), 60, 75),
                (self.makeAppImgUrl(CardUtil.makeThumbnailUrlMiddle(cardmaster)), 110, 138),
                (self.makeAppImgUrl(CardUtil.makeThumbnailUrlLarge(cardmaster)), 320, 400),
                (self.makeAppImgUrl(CardUtil.makeThumbnailUrlBustup(cardmaster)), 320, 314),
            ]
            if cardmaster.rare in Defines.Rarity.EVOLUTION_ABLES:
                row.append((self.makeAppImgUrl(CardUtil.makeThumbnailUrlMemory(cardmaster)), 70, 88))
            else:
                row.append('')
            datalist.append(row)
        self.putData(titles, datalist)
        
        url = OSAUtil.addQuery(UrlMaker.view_images(), '_target', 'Card')
        url = OSAUtil.addQuery(url, '_filter', urllib.quote(self.html_param['_filter'], ''))
        self.putPagenationData(url, page, pagemax)
    
    def procMemories(self, filter_json, page):
        """思い出画像確認.
        """
        PAGE_CONTENT_NUM = 50
        offset = page * PAGE_CONTENT_NUM
        
        cardmasterlist = CardMasterView.fetchValues(filters=filter_json, order_by='id', limit=PAGE_CONTENT_NUM, offset=offset, using=settings.DB_READONLY)
        cardidlist = [cardmaster.id for cardmaster in cardmasterlist]
        
        filters = {
            'cardid__in' : cardidlist,
        }
        nummax = MemoriesMaster.count(filters, using=settings.DB_READONLY)
        pagemax = int((nummax + PAGE_CONTENT_NUM - 1) / PAGE_CONTENT_NUM)
        
        titles = (
            u'ID',
            u'名前',
            u'サムネイル',
            u'コンテンツ',
        )
        memoriesmasterlist = MemoriesMaster.fetchValues(filters=filters, order_by='id', limit=PAGE_CONTENT_NUM, offset=offset, using=settings.DB_READONLY)
        
        datalist = []
        for memoriesmaster in memoriesmasterlist:
            thumb = ''
            content = ''
            if memoriesmaster.contenttype == Defines.MemoryContentType.IMAGE:
                thumb = (self.makeAppImgUrl(memoriesmaster.thumb), 78, 88)
                content = (self.makeAppImgUrl(memoriesmaster.contentdata), 320, 400)
            elif memoriesmaster.contenttype == Defines.MemoryContentType.MOVIE:
                moviemaster = BackendApi.get_movieplaylist_master(self.getModelMgr(), int(memoriesmaster.contentdata), using=settings.DB_READONLY)
                if moviemaster:
                    thumb = (self.makeAppLinkUrlMedia(Media.movie_thumbnail(moviemaster.filename)), 151, 88)
                    content = self.makeAppLinkUrlMedia(Media.movie_m3u8(moviemaster.filename))
            elif memoriesmaster.contenttype == Defines.MemoryContentType.VOICE:
                thumb = (self.makeAppImgUrl(memoriesmaster.thumb), 'auto', 88)
                voicemaster = BackendApi.get_voiceplaylist_master(self.getModelMgr(), int(memoriesmaster.contentdata), using=settings.DB_READONLY)
                if voicemaster:
                    content = self.makeAppLinkUrlMedia(Media.voice_aac(moviemaster.filename))
            
            row = [
                memoriesmaster.id,
                memoriesmaster.name,
                thumb,
                content,
            ]
            datalist.append(row)
        self.putData(titles, datalist)
        
        url = OSAUtil.addQuery(UrlMaker.view_images(), '_target', 'Memories')
        url = OSAUtil.addQuery(url, '_filter', urllib.quote(self.html_param['_filter'], ''))
        self.putPagenationData(url, page, pagemax)
    
    def procMovies(self, filter_json, page):
        """思い出動画確認.
        """
        PAGE_CONTENT_NUM = 50
        offset = page * PAGE_CONTENT_NUM
        
        filter_json = filter_json or {}
        filter_json['hklevel'] = Defines.HKLEVEL_MAX
        filter_json['rare__gte'] = Defines.Rarity.HIGH_RARE
        
        cardmasterlist = CardMasterView.fetchValues(filters=filter_json, order_by='id', limit=PAGE_CONTENT_NUM, offset=offset, using=settings.DB_READONLY)
        nummax = len(cardmasterlist)
        pagemax = int((nummax + PAGE_CONTENT_NUM - 1) / PAGE_CONTENT_NUM)
        cardmasterlist = cardmasterlist[offset:offset+PAGE_CONTENT_NUM]
        
        cardidlist = [cardmaster.id for cardmaster in cardmasterlist]
        
        filters = {
            'cardid__in' : cardidlist,
            'contenttype__in' : [Defines.MemoryContentType.MOVIE, Defines.MemoryContentType.MOVIE_PC],
        }
        memoriesmasterlist = MemoriesMaster.fetchValues(filters=filters, order_by='id', using=settings.DB_READONLY)
        pc_dict = {}
        sp_dict = {}
        for memoriesmaster in memoriesmasterlist:
            if memoriesmaster.contenttype == Defines.MemoryContentType.MOVIE:
                dic = sp_dict
            elif memoriesmaster.contenttype == Defines.MemoryContentType.MOVIE_PC:
                dic = pc_dict
            else:
                continue
            arr = dic[memoriesmaster.cardid] = dic.get(memoriesmaster.cardid) or []
            arr.append(int(memoriesmaster.contentdata))
        
        model_mgr = self.getModelMgr()
        
        titles = (
            u'カードID',
            u'名前',
            u'SP版',
            u'PC版',
        )
        datalist = []
        
        def thumbList(mov_cls, movieidlist):
            moviemasterlist = BackendApi.get_model_list(model_mgr, mov_cls, movieidlist, using=settings.DB_READONLY)
            dest = []
            for mov in moviemasterlist:
                if isinstance(mov, PcMoviePlayList):
                    url = Media.movie_pc_thumbnail(mov.filename)
                else:
                    url = Media.movie_thumbnail(mov.filename)
                dest.append((self.makeAppLinkUrlMedia(url), 151, 88))
            return dest
        
        for cardmaster in cardmasterlist:
            
            sp_thumb_list = thumbList(MoviePlayList, sp_dict.get(cardmaster.id) or [])
            pc_thumb_list = thumbList(PcMoviePlayList, pc_dict.get(cardmaster.id) or [])
            
            row = [
                cardmaster.id,
                cardmaster.name,
                sp_thumb_list or u'未設定',
                pc_thumb_list or u'未設定',
            ]
            datalist.append(row)
        self.putData(titles, datalist)
        
        url = OSAUtil.addQuery(UrlMaker.view_images(), '_target', 'Movies')
        url = OSAUtil.addQuery(url, '_filter', urllib.quote(self.html_param['_filter'], ''))
        self.putPagenationData(url, page, pagemax)
    
    def makeAppImgUrl(self, url):
        return '%simg/sp/large/%s' % (settings_sub.STATIC_URL_ROOT, url)

def main(request):
    return Handler.run(request)
