# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from defines import Defines
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from platinumegg.app.cabaret.util.db_util import ModelRequestMgr
from platinumegg.app.cabaret.util.api import BackendApi, Objects
from platinumegg.app.cabaret.models.Player import PlayerDeck, PlayerGold,\
    PlayerGachaPt, PlayerKey
import settings_sub
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.lib.opensocial.util import OSAUtil
import settings
from platinumegg.app.cabaret.util import db_util


class Handler(AppHandler):
    """プレゼント受け取り.
    processを引数で受け取る.
    一覧:
        引数
            ページ.
        未受け取りのプレゼントを一覧で表示.
        タイプで絞込み.
        ページ内一括受け取りURL.
    受け取り書き込み:
        引数
            受け取るプレゼント.
        アイテム等を集計して付与.
        受け取り結果へ受け取ったプレゼントのIDをつけてリダイレクト.
    受け取り結果:
        引数
            受け取ったプレゼントのID.
        受け取ったプレゼントの一覧を表示.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return [PlayerDeck]
    
    def process(self):
        args = self.getUrlArgs('/present/')
        self.__args = args
        
        procname = args.get(0)
        table = {
            'list' : self.procList,
            'do' : self.procDo,
            'result' : self.procResult,
        }
        proc = table.get(procname, None)
        if proc is None:
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'存在しないプロセスです.%s' % procname)
            self.procList()
        else:
            proc()
    
    def procList(self):
        """一覧表示.
        """
        
        # 絞り込みの引数.
        v_player = self.getViewerPlayer()
        
        client = OSAUtil.get_cache_client()
        
        topic = Defines.PresentTopic.ALL
        page = 0
        sort = "desc"
        if self.request.method == 'GET':
#            topic = client.get(v_player.id, namespace='presentbox:topic') or topic
            sort = client.get(v_player.id, namespace='present:sort') or sort
        
        topic = self.request.get(Defines.URLQUERY_CTYPE, topic)
        page = self.request.get(Defines.URLQUERY_PAGE, page)
        sort = self.request.get(Defines.URLQUERY_SORTBY, sort)
        
        if not str(topic).isdigit() or not str(page).isdigit():
            topic = Defines.PresentTopic.ALL
            page = 0
            if settings_sub.IS_LOCAL:
                raise CabaretError(u'引数が想定外です', CabaretError.Code.ILLEGAL_ARGS)
        else:
            topic = int(topic)
            page = int(page)
        
        self.putPresentList(UrlMaker.present(), topic, page, sort)
        
        if not self.response.isEnd:
            self.writeAppHtml('present')
    
    def procDo(self):
        """書き込み.
        """
        presentidlist = self.__get_present_idlist()
        
        v_player = self.getViewerPlayer()
        
        excludetable = {
            Defines.URLQUERY_CHECK_GOLD : Defines.ItemType.GOLD,
            Defines.URLQUERY_CHECK_CARD : Defines.ItemType.CARD,
        }
        excludetypes = [itype for key, itype in excludetable.items() if self.request.get(key)]
        
        model_mgr, result = db_util.run_in_transaction(self.tr_write, v_player.id, presentidlist, excludetypes)
        model_mgr.write_end()
        
        received_idlist = [k for k,v in result.items() if v in (CabaretError.Code.OK, CabaretError.Code.ALREADY_RECEIVED)]
        over = CabaretError.Code.OVER_LIMIT in result.values()
        
        url = self.addIDQuesyParam(UrlMaker.presentresult(over), received_idlist)
        
        topic = self.request.get(Defines.URLQUERY_CTYPE) or ""
        if str(topic).isdigit():
            url = OSAUtil.addQuery(url, Defines.URLQUERY_CTYPE, topic)
        
        self.appRedirect(self.makeAppLinkUrlRedirect(url))
    
    def procResult(self):
        """結果表示.
        """
        presentidlist = self.__get_present_idlist(True)
        over = False
        try:
            over = bool(int(self.__args.get(1, 0)))
        except:
            pass
        
        model_mgr = self.getModelMgr()
        
        presentlist = BackendApi.get_presents(presentidlist, model_mgr, using=settings.DB_READONLY, received=True)
        self.html_param['presentreceivedlist'] = [Objects.present(self, presentset) for presentset in presentlist]
        
        self.html_param['overlimit'] = over
        
        url_reload = self.addIDQuesyParam(UrlMaker.presentresult(over), presentidlist)
        
        topic = self.request.get(Defines.URLQUERY_CTYPE) or ""
        topic = int(topic) if str(topic).isdigit() else Defines.PresentTopic.ALL
        url_reload = OSAUtil.addQuery(url_reload, Defines.URLQUERY_CTYPE, topic)
        
        client = OSAUtil.get_cache_client()
        v_player = self.getViewerPlayer()
        sort = client.get(v_player.id, namespace='present:sort')
        
        self.putPresentList(url_reload, topic, sort=sort, using=settings.DB_DEFAULT)
        
        if not self.response.isEnd:
            self.writeAppHtml('presentrecieve')
    
    def __get_present_idlist(self, blank=False):
        """引数で渡されたIDのリスト.
        """
        try:
            str_idlist = self.request.get(Defines.URLQUERY_ID)
            idlist = [int(str_id) for str_id in str_idlist.split(',') if str_id]
            if not idlist and not blank:
                raise
        except:
            raise CabaretError(u'プレゼントが指定されていません', CabaretError.Code.ILLEGAL_ARGS)
        return idlist
    
    def addIDQuesyParam(self, url, idlist):
        """プレゼントのIDのリストを引数につける.
        """
        str_idlist = ','.join(['%d' % iid for iid in idlist])
        url = OSAUtil.addQuery(url, Defines.URLQUERY_ID, str_idlist)
        return url
    
    def putPresentList(self, url_reload, topic, page=0, sort="desc", using=settings.DB_READONLY):
        """プレゼントリストをHTMLに埋め込む.
        """
        model_mgr = self.getModelMgr()
        
        # 絞り込みの引数.
        v_player = self.getViewerPlayer()
        
        overlimit = v_player.cardlimit <= BackendApi.get_cardnum(v_player.id, model_mgr, using=settings.DB_READONLY)
        
        # プレゼントを取得.
        offset = page * Defines.PRESENT_PAGE_CONTENT_NUM
        limit = Defines.PRESENT_PAGE_CONTENT_NUM + 1
        presentidlist = BackendApi.get_present_idlist(v_player.id, topic, offset, limit, model_mgr, using=using, desc=sort=="desc")
        has_next_page = len(presentidlist) == limit
        presentidlist = presentidlist[:Defines.PRESENT_PAGE_CONTENT_NUM]
        presentlist = BackendApi.get_presents(presentidlist, model_mgr, using=using)
        if presentlist is None:
            # うまく取れなかった.リダイレクトさせておくか.
            BackendApi._save_presentidlist(v_player.id, model_mgr, topic, using=using)
            url = url_reload
            url = OSAUtil.addQuery(url, Defines.URLQUERY_CTYPE, topic)
            url = OSAUtil.addQuery(url, Defines.URLQUERY_PAGE, page)
            self.appRedirect(self.makeAppLinkUrlRedirect(url))
            return
        
        self.html_param['presentlist'] = [Objects.present(self, presentset, overlimit, cur_topic=topic) for presentset in presentlist]
        
        # 絞り込み用のURL.
        url_base = OSAUtil.addQuery(UrlMaker.present(), Defines.URLQUERY_SORTBY, sort)
        self.html_param['url_all'] = self.makeAppLinkUrl(OSAUtil.addQuery(url_base, Defines.URLQUERY_CTYPE, Defines.PresentTopic.ALL))
        self.html_param['url_card'] = self.makeAppLinkUrl(OSAUtil.addQuery(url_base, Defines.URLQUERY_CTYPE, Defines.PresentTopic.CARD))
        self.html_param['url_item'] = self.makeAppLinkUrl(OSAUtil.addQuery(url_base, Defines.URLQUERY_CTYPE, Defines.PresentTopic.ITEM))
        self.html_param['url_etc'] = self.makeAppLinkUrl(OSAUtil.addQuery(url_base, Defines.URLQUERY_CTYPE, Defines.PresentTopic.ETC))
        
        # ソート切り替え.
        url_base = OSAUtil.addQuery(UrlMaker.present(), Defines.URLQUERY_CTYPE, topic)
        self.html_param['url_desc'] = self.makeAppLinkUrl(OSAUtil.addQuery(url_base, Defines.URLQUERY_SORTBY, "desc"))
        self.html_param['url_asc'] = self.makeAppLinkUrl(OSAUtil.addQuery(url_base, Defines.URLQUERY_SORTBY, "asc"))
        self.html_param['cur_sort'] = "desc" if sort == "desc" else "asc"
        
        # ページ切り替えURL.
        url_base = OSAUtil.addQuery(url_base, Defines.URLQUERY_SORTBY, sort)
        if 0 < page:
            self.html_param['url_prev'] = self.makeAppLinkUrl(OSAUtil.addQuery(url_base, Defines.URLQUERY_PAGE, page - 1))
        if has_next_page:
            self.html_param['url_next'] = self.makeAppLinkUrl(OSAUtil.addQuery(url_base, Defines.URLQUERY_PAGE, page + 1))
        
        # まとめて受け取るUrl.
        url = UrlMaker.presentdo()
        url = OSAUtil.addQuery(url, Defines.URLQUERY_CTYPE, topic)
        url = OSAUtil.addQuery(url, Defines.URLQUERY_SORTBY, sort)
        self.html_param['url_receive_all'] = self.makeAppLinkUrl(self.addIDQuesyParam(url, presentidlist))
        
        # チェックボックスのキー.
        self.html_param['key_except_card'] = Defines.URLQUERY_CHECK_CARD
        self.html_param['key_except_gold'] = Defines.URLQUERY_CHECK_GOLD
        
        self.html_param['cur_topic'] = topic
        
        client = OSAUtil.get_cache_client()
#        client.set(v_player.id, topic, namespace='presentbox:topic')
        client.set(v_player.id, sort, namespace='present:sort')
    
    def tr_write(self, uid, presentidlist, excludetypes):
        """書き込み.
        """
        model_mgr = ModelRequestMgr(loginfo=self.addloginfo)
        player = BackendApi.get_players(self, [uid], [PlayerDeck, PlayerGold, PlayerGachaPt, PlayerKey], model_mgr=model_mgr)[0]
        result = BackendApi.tr_receive_present(model_mgr, player, presentidlist, excludetypes)
        model_mgr.write_all()
        return model_mgr, result

def main(request):
    return Handler.run(request)
