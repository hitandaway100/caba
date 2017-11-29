# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from defines import Defines
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.lib.opensocial.util import OSAUtil
import settings
from platinumegg.app.cabaret.util.cabareterror import CabaretError


class Handler(AppHandler):
    """仲間の近況.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        page = 0
        
        v_player = self.getViewerPlayer()
        try:
            if self.is_pc:
                #oid = int(self.request.get(Defines.URLQUERY_ID) or v_player.id)
                args = self.getUrlArgs('/friendlog/')
                oid = int(args.get(0, v_player.id))
                page = int(self.request.get(Defines.URLQUERY_PAGE) or 0)
                #content_num = Defines.PC_GAMELOG_CONTENT_NUM
                content_num = Defines.GAMELOG_PAGE_CONTENT_NUM
            else:
                args = self.getUrlArgs('/friendlog/')
                oid = int(args.get(0, v_player.id))
                page = int(self.request.get(Defines.URLQUERY_PAGE) or 0)
                content_num = Defines.GAMELOG_PAGE_CONTENT_NUM
        except:
            raise CabaretError(u'不正なアクセスです', CabaretError.Code.ILLEGAL_ARGS)
        
        model_mgr = self.getModelMgr()
        
        offset = page * content_num
        limit = content_num + 1
        obj_friendlog_list = BackendApi.get_friendlog_list(self, oid, offset, limit, model_mgr, using=settings.DB_READONLY)
        
        self.execute_api()
        
        has_next_page = content_num < len(obj_friendlog_list)
        self.html_param['friendlog_list'] = obj_friendlog_list[:content_num]
        
        url_base = UrlMaker.friendlog(oid)
        if 0 < page:
            url = OSAUtil.addQuery(url_base, Defines.URLQUERY_PAGE, page - 1)
            self.html_param['url_prev'] = self.makeAppLinkUrl(url)
        
        if has_next_page:
            url = OSAUtil.addQuery(url_base, Defines.URLQUERY_PAGE, page + 1)
            self.html_param['url_next'] = self.makeAppLinkUrl(url)
        
        lognum = BackendApi.get_friendlog_num(model_mgr, oid, using=settings.DB_READONLY)
        self.html_param['cur_page'] = page + 1
        self.html_param['page_max'] = max(1, int((lognum + content_num - 1) / content_num))
        
        self.writeAppHtml('friend')
    

def main(request):
    return Handler.run(request)
