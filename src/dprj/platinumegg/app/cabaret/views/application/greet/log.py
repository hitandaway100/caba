# -*- coding: utf-8 -*-
from platinumegg.app.cabaret.views.apphandler import AppHandler
from defines import Defines
from platinumegg.app.cabaret.util.api import BackendApi
from platinumegg.app.cabaret.util.url_maker import UrlMaker
from platinumegg.lib.opensocial.util import OSAUtil
import settings
from platinumegg.app.cabaret.util.cabareterror import CabaretError


class Handler(AppHandler):
    """あいさつ履歴.
    """
    
    @classmethod
    def getViewerPlayerClassList(cls):
        return []
    
    def process(self):
        v_player = self.getViewerPlayer()
        
        page = 0
        try:
            if self.is_pc:
                #oid = int(self.request.get(Defines.URLQUERY_ID) or v_player.id)
                #content_num = Defines.PC_GAMELOG_CONTENT_NUM
                args = self.getUrlArgs('/greetlog/')
                oid = int(args.get(0, v_player.id))
                page = int(self.request.get(Defines.URLQUERY_PAGE) or 0)
                content_num = Defines.GAMELOG_PAGE_CONTENT_NUM
            else:
                args = self.getUrlArgs('/greetlog/')
                oid = int(args.get(0, v_player.id))
                page = int(self.request.get(Defines.URLQUERY_PAGE) or 0)
                content_num = Defines.GAMELOG_PAGE_CONTENT_NUM
        except:
            raise CabaretError(u'閲覧できません', CabaretError.Code.ILLEGAL_ARGS)
        
        model_mgr = self.getModelMgr()
        
        offset = page * content_num
        limit = content_num + 1
        obj_greetlog_list = BackendApi.get_greetlog_list(self, oid, offset, limit, model_mgr, using=settings.DB_READONLY)
        
        self.execute_api()
        
        has_next_page = content_num < len(obj_greetlog_list)
        self.html_param['greetlog_list'] = obj_greetlog_list[:content_num]
        
        url_base = UrlMaker.greetlog(oid)
        if 0 < page:
            url = OSAUtil.addQuery(url_base, Defines.URLQUERY_PAGE, page - 1)
            self.html_param['url_prev'] = self.makeAppLinkUrl(url)
        if has_next_page:
            url = OSAUtil.addQuery(url_base, Defines.URLQUERY_PAGE, page + 1)
            self.html_param['url_next'] = self.makeAppLinkUrl(url)
        
        greetnum = BackendApi.get_greetlog_num(model_mgr, oid, using=settings.DB_READONLY)
        self.html_param['cur_page'] = page + 1
        self.html_param['page_max'] = max(1, int((greetnum + content_num - 1) / content_num))
        
        self.writeAppHtml('greeting')
    

def main(request):
    return Handler.run(request)
