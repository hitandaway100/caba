# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.application.happening.base import HappeningHandler
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.url_maker import UrlMaker
import settings
import settings_sub
from platinumegg.app.cabaret.util.cabareterror import CabaretError
from defines import Defines
from platinumegg.lib.opensocial.util import OSAUtil


class Handler(HappeningHandler):
    """レイドフレンド選択.
    """
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def redirectWithError(self, err):
        if settings_sub.IS_LOCAL:
            raise err
        url = UrlMaker.happening()
        self.appRedirect(self.makeAppLinkUrlRedirect(url, add_frompage=False))
    
    def process(self):
        
        v_player = self.getViewerPlayer()
        
        args = self.getUrlArgs('/raidfriendselect/')
        ope = args.get(0)
        raidid = '%s' % args.get(1)
        
        if not BackendApi.raid_is_can_callfriend(v_player.id):
            self.redirectWithError(CabaretError(u'まだキャストを呼べません', CabaretError.Code.NOT_ENOUGH))
            return
        elif not raidid.isdigit():
            self.redirectWithError(CabaretError(u'レイドが指定されていません', CabaretError.Code.ILLEGAL_ARGS))
            return
        
        raidid = int(raidid)
        
        table = {
            'list' : self.procList,
            'set' : self.procSet,
        }
        func = table.get(ope)
        if not func:
            self.redirectWithError(CabaretError(u'不正なアクセスです', CabaretError.Code.ILLEGAL_ARGS))
            return
        func(args, raidid)
    
    def procList(self, args, raidid):
        page = 0
        try:
            page = int(self.request.get(Defines.URLQUERY_PAGE) or 0)
        except:
            pass
        
        contentnum = Defines.RAIDFRIEND_LIST_CONTENT_NUM_PER_PAGE
        offset = contentnum * page
        limit = contentnum + 1
        cardsetlist = self.getFriendLeaderCardList(limit, offset)
        has_next_page = contentnum < len(cardsetlist)
        cardsetlist = cardsetlist[:contentnum]
        
        if cardsetlist:
            cb = self.putPlayerListByLeaderList(raidid, cardsetlist)
            if cb:
                self.execute_api()
                cb()
        
        url_base = UrlMaker.raidfriendselect(raidid)
        if 0 < page:
            url = OSAUtil.addQuery(url_base, Defines.URLQUERY_PAGE, page - 1)
            self.html_param['url_page_prev'] = self.makeAppLinkUrl(url)
        if has_next_page:
            url = OSAUtil.addQuery(url_base, Defines.URLQUERY_PAGE, page + 1)
            self.html_param['url_page_next'] = self.makeAppLinkUrl(url)
        self.html_param['cur_page'] = page + 1
        self.html_param['page_max'] = int((self.getFriendLeaderCardNum() + contentnum - 1) / contentnum)
        
        self.writeAppHtml('raid/friendselect')
    
    def procSet(self, args, raidid):
        
        fid = str(args.get(2))
        if not fid.isdigit():
            self.redirectWithError(CabaretError(u'フレンドを設定できません', CabaretError.Code.ILLEGAL_ARGS))
            return
        fid = int(fid)
        
        model_mgr = self.getModelMgr()
        v_player = self.getViewerPlayer()
        
        leader = BackendApi.get_leaders([fid], arg_model_mgr=model_mgr, using=settings.DB_READONLY).get(fid)
        if leader is None:
            self.redirectWithError(CabaretError(u'存在しないユーザーです', CabaretError.Code.NOT_DATA))
            return
        
        BackendApi.save_raidhelpcard(model_mgr, v_player.id, raidid, leader, using=settings.DB_READONLY)
        
        url = UrlMaker.happening()
        self.appRedirect(self.makeAppLinkUrlRedirect(url, add_frompage=False))
    

def main(request):
    return Handler.run(request)

